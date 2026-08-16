import asyncio

from app.mcp.tools import load_infrastructure_tools


async def main() -> None:
    tools = await load_infrastructure_tools()

    logs_tool = next(tool for tool in tools if tool.name == "get_service_logs")

    print("\nTool name:")
    print(logs_tool.name)

    print("\nTool args:")
    print(logs_tool.args)

    result = await logs_tool.ainvoke(
        {
            "service": "payment-service",
        }
    )

    print("\nResult:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
