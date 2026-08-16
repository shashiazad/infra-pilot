import asyncio

from mcp import Client
from mcp.client.stdio import stdio_client
from mcp_types import TextContent

from app.mcp.client import get_infrastructure_server_params


async def main() -> None:
    params = get_infrastructure_server_params()

    async with Client(stdio_client(params)) as client:
        tools = await client.list_tools()

        print("\nAvailable MCP Tools:")

        for tool in tools.tools:
            print(f"- {tool.name}")

        result = await client.call_tool(
            "get_service_logs",
            {
                "service": "prod-demo-payment",
            },
        )

        print("\nTool Result:")

        for content in result.content:
            if isinstance(content, TextContent):
                print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
