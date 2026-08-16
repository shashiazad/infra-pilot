import os
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = (
    Path(__file__).parent
    / "servers"
    / "infrastructure.py"
)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _server_params() -> StdioServerParameters:
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


async def _call_mcp_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> Any:

    async with stdio_client(
        _server_params()
    ) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            if result.is_error:

                texts = [
                    item.text
                    for item in result.content
                    if hasattr(item, "text")
                ]

                raise RuntimeError(
                    "\n".join(texts)
                    or (
                        f"MCP tool "
                        f"{tool_name!r} failed"
                    )
                )

            if result.structured_content is not None:
                return result.structured_content

            texts = [
                item.text
                for item in result.content
                if hasattr(item, "text")
            ]

            return "\n".join(texts)


def _create_langchain_tool(
    name: str,
    description: str,
) -> BaseTool:

    async def call_tool(
        service: str,
        namespace: str = "infrapilot-demo",
    ) -> Any:

        return await _call_mcp_tool(
            name,
            {
                "service": service,
                "namespace": namespace,
            },
        )

    return StructuredTool.from_function(
        coroutine=call_tool,
        name=name,
        description=description,
    )


async def load_infrastructure_tools() -> list[BaseTool]:

    async with stdio_client(
        _server_params()
    ) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            result = await session.list_tools()

            return [
                _create_langchain_tool(
                    name=mcp_tool.name,
                    description=(
                        mcp_tool.description
                        or ""
                    ),
                )
                for mcp_tool in result.tools
            ]
