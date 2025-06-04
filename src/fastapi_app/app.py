import datetime
import os
from zoneinfo import ZoneInfo
from fastapi import FastAPI

import requests
from starlette.applications import Starlette
from starlette.routing import Route, Mount
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from dotenv import load_dotenv

load_dotenv()
base_url = os.getenv("BASE_URL", "http://localhost:8000")



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")


# Initialize the MCP server with your tools
mcp = FastMCP(
    name="Weather and Time SSE Server"
)


@mcp.tool()
def TimeTool():
    "Provides the current time for Europe/Copenhagen, it returns the local time."
    current_time = datetime.datetime.now(tz=ZoneInfo("Europe/Copenhagen"))
    return f"The current time is {current_time}."

transport = SseServerTransport("/messages/")


@mcp.tool()
def Electricity_Tax_tool():
    """
    Provides electricity tax information for denmark
    Data is from 2015 to present
    This data is also called 'Elafgift' in Danish.
    """

    url = f"{base_url}/tax"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
    
@mcp.tool()
def Electricity_spot_price_tool(priece_area="DK1", date=None):
    """
    Provides electricity spot price information for denmark
    Data is from 2015 to present, Areas accepted is 'DK1' and 'DK2'.
    This data is also called 'Elspotpris' in Danish.
    """

    url = f"{base_url}/spotprice/date/area?pricearea={priece_area}&qdate={date}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
    

async def handle_sse(request):
    # Prepare bidirectional streams over SSE
    async with transport.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as (in_stream, out_stream):
        # Run the MCP server: read JSON-RPC from in_stream, write replies to out_stream
        await mcp._mcp_server.run(
            in_stream,
            out_stream,
            mcp._mcp_server.create_initialization_options()
        )


#Build a small Starlette app for the two MCP endpoints
sse_app = Starlette(
    routes=[
        Route("/sse", handle_sse, methods=["GET"]),
        # Note the trailing slash to avoid 307 redirects
        Mount("/messages/", app=transport.handle_post_message)
    ]
)


app = FastAPI()
app.mount("/", sse_app)

@app.get("/health")
def read_root():
    return {"message": "MCP SSE Server is running"}

