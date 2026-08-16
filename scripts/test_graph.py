import asyncio

from app.agents.investigation.graph import (
    build_investigation_graph,
)


async def main() -> None:
    graph = await build_investigation_graph()

    initial_state = {
        "incident_id": "test-incident",
        "incident": {
            "title": "Payment service degradation",
            "description": (
                "Payment service is returning "
                "HTTP 5xx responses."
            ),
            "service": "payment-service",
            "severity": "SEV-2",
            "status": "OPEN",
        },
        "classification": {},
        "investigation_plan": [],
        "messages": [],
        "evidence": [],
        "tool_iterations": 0,
        "max_tool_iterations": 5,
        "analysis": {},
        "final_result": {},
    }

    result = await graph.ainvoke(initial_state)

    print("\n=== MESSAGE FLOW ===")

    for message in result["messages"]:
        print(f"\n{type(message).__name__}")
        print(message)

    print("\n=== EVIDENCE ===")
    print(result["evidence"])

    print("\n=== TOOL ITERATIONS ===")
    print(result["tool_iterations"])

    print("\n=== ANALYSIS ===")
    print(result["analysis"])


if __name__ == "__main__":
    asyncio.run(main())