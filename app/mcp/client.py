from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = Path(__file__).parent / "servers" / "infrastructure.py"


def get_infrastructure_server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command="uv",
        args=[
            "run",
            "python",
            str(SERVER_PATH),
        ],
    )


async def list_infrastructure_tools():
    params = get_infrastructure_server_params()

    async with Client(stdio_client(params)) as client:
        return await client.list_tools()
