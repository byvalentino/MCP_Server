from fastapi import APIRouter, status

#from src.fastapi_app.responses.copilot import ChatResponse
#from src.fastapi_app.schemas.copilot import ChatRequest
from src.fastapi_app.services.copilot import get_chat_response
from pydantic import BaseModel

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

copilot_router = APIRouter(
    prefix="/copilot",
    tags=["Copilot"],
    responses={404: {"description": "Not found"}},
)


@copilot_router.post("/agent/", status_code=status.HTTP_200_OK, response_model=ChatResponse)
async def agent(request: ChatRequest):
    response = await get_chat_response(request)
    return response

@copilot_router.get("/hello", status_code=status.HTTP_200_OK)
async def get_tax_info_by_dat(
    #qdate: datetime = None,
    #session: Session = Depends(get_db_session),
    #user=Depends(get_current_user),
):
    #if qdate is None:
    #    qdate = datetime.now().astimezone().date()
    #return await "Hello, World!"  # Replace with actual logic if needed
    return {"message": "Hello, World!"}