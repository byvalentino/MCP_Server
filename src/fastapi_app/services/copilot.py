#Need to commit this file to the repository
from datetime import datetime, timedelta

import pytz
from fastapi import HTTPException
from semantic_kernel.connectors.mcp import MCPSsePlugin
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
#from src.fastapi_app.config.chat_kernel import get_kernel
#from src.fastapi_app.config.config import get_settings
#from src.fastapi_app.responses.copilot import ChatResponse
#from src.fastapi_app.schemas.copilot import ChatHistoryElement, ChatRequest
from pydantic import BaseModel


#config = get_settings()
#deployment_name = config.AZURE_OPENAI_DEPLOYMENT
#endpoint = config.AZURE_OPENAI_ENDPOINT
#api_key = config.AZURE_OPENAI_KEY

#kernel = get_kernel()
#mcp_url = config.MCP_URL
#mcp_url = "https://apim-demo-tvdp.azure-api.net/petstore-mcp/sse"
#mcp_url = "https://glorious-train-49gqppvg9w2wwj-8000.app.github.dev/sse"
mcp_url = "http://127.0.0.1:8000/sse"


#from src.fastapi_app.responses.base import BaseResponse
#class BaseResponse(BaseModel):
#    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

#class ChatResponse(BaseResponse):
#class ChatResponse():
class ChatResponse(BaseModel):
    content: str

class ChatHistoryElement(BaseModel):
#class ChatHistoryElement():
    role: str
    content: str

class ChatRequest(BaseModel):
#class ChatRequest():
    message: str
    history: list[ChatHistoryElement] = []

def get_kernel() -> tuple[Kernel, AzureChatCompletion]:
    kernel = Kernel()
    service_id = "AZURE_OPENAI"
    deployment_name = "gpt-4o-mini"
    api_key=""
    endpoint=""
    
    chat_service = AzureChatCompletion(
        deployment_name=deployment_name,
        endpoint=endpoint,
        api_key=api_key,
        service_id=service_id,
        instruction_role=None,
    )
    settings = AzureChatPromptExecutionSettings(service_id=service_id)
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    kernel.add_service(chat_service)
    return kernel, chat_service, settings

def parse_chat_history(chat_history: ChatHistory, history: list[ChatHistoryElement]) -> ChatHistory:
    for entry in history:
        if entry.role == "user":
            chat_history.add_user_message(entry.content)
        elif entry.role == "assistant":
            chat_history.add_assistant_message(entry.content)
    return chat_history



async def get_chat_response(request: ChatRequest):
    dk_timezone = pytz.timezone("Europe/Copenhagen")
    dk_time = datetime.now(dk_timezone).isoformat()
    dk_end_date = datetime.now(dk_timezone).date()

    _hour = datetime.now(dk_timezone).hour
    if _hour >= 14:
        dk_end_date = dk_end_date + timedelta(days=1)

    system_message = f"""
        You are a chat bot. And you help users interact with prices on electricity in denmark.
        You are especially good at answering questions about the taxes and tarifs and current price (spotprice).
        You can call functions to get the information you need.
        current time is {dk_time}
        When using spotprices, always use 'DK1' or 'DK2' as area, depending on the user location.
        'DK1' is the western part of denmark including fyn, and 'DK2' is the eastern part of denmark including Bornholm.
        If your missing information to answer a question, ask the user to provide the information.
        If you don't know the answer, say that you don't know.
        Answer in Danish exept if the user is asking in a different language, then answer in that language.
        Limit the data gathered to maximum of 7 day for spotprices.
        Spotprices are only available from 1/4 2025 days and til {dk_end_date}.
        """
    kernel, chat_service, settings = get_kernel()

    chat_history = ChatHistory()
    chat_history.add_system_message(system_message)
    chat_history.add_user_message(request.message)
    history = parse_chat_history(chat_history, request.history)

    async with MCPSsePlugin(
        name="prices",
        description="get danish electricity tax prices and spotprices",
        url=mcp_url,
        #headers = {}
    ) as price_plugin:
        kernel.add_plugin(price_plugin)
        result = await chat_service.get_chat_message_content(history, settings, kernel=kernel)
        if not result.items:
            raise HTTPException(status_code=404, detail="No response from the chat service.")
        response = ChatResponse(
            content=result.items[0].text,
        )
        return response