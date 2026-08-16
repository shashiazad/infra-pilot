import asyncio

from app.mcp.tools import (
    load_infrastructure_tools,
)


async def main() -> None:

    tools = await load_infrastructure_tools()

    for tool in tools:
        print(
            "\nTool:",
            tool.name,
        )

        print(
            "Args:",
            tool.args,
        )

    for tool in tools:

        if tool.name == "get_pod_status":

            result = await tool.ainvoke(
                {
                    "service": "prod-demo-payment",
                    "namespace": "prod-demo",
                }
            )

            print(
                "\n=== POD STATUS ==="
            )

            print(result)

        if tool.name == "get_pod_events":

            result = await tool.ainvoke(
                {
                    "service": "prod-demo-payment",
                    "namespace": "prod-demo",
                }
            )

            print(
                "\n=== POD EVENTS ==="
            )

            print(result)

        if tool.name == "get_application_metrics":

            result = await tool.ainvoke(
                {
                    "service": "prod-demo-payment",
                    "namespace": "prod-demo",
                }
            )

            print(
                "\n=== APPLICATION METRICS ==="
            )

            print(result)


if __name__ == "__main__":
    asyncio.run(main())
