import os
from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = Path(__file__).parent / "servers" / "infrastructure.py"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_infrastructure_server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command="uv",
        args=[
            "run",
            "mcp",
            "run",
            str(SERVER_PATH),
        ],
        cwd=PROJECT_ROOT,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                filter(
                    None,
                    (
                        str(PROJECT_ROOT),
                        os.environ.get("PYTHONPATH"),
                    ),
                )
            ),
        },
    )


async def list_infrastructure_tools():
    params = get_infrastructure_server_params()

    async with Client(stdio_client(params)) as client:
        return await client.list_tools()
