import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.investigation.graph import (
    build_investigation_graph,
)
from app.db.session import AsyncSessionLocal
from app.services.investigation_service import InvestigationService


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await run_graph(session)


async def run_graph(session: AsyncSession) -> None:
    investigation_service = InvestigationService(
        session
    )
    graph = await build_investigation_graph(
        session,
        investigation_service,
    )

    initial_state = {
        "incident_id": "00000000-0000-0000-0000-000000000001",
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
        "runbooks": [],
        "historical_incidents": [],
        "tool_iterations": 0,
        "max_tool_iterations": 5,
        "analysis": {},
        "remediation_proposal": {},
        "final_result": {},
    }

    result = await graph.ainvoke(initial_state)

    print("\n=== MESSAGE FLOW ===")

    for message in result["messages"]:
        print(f"\n{type(message).__name__}")
        print(message)

    print("\n=== EVIDENCE ===")
    print(result["evidence"])

    print("\n=== RUNBOOKS ===")
    print(result["runbooks"])

    print("\n=== HISTORY ===")
    print(result["historical_incidents"])

    print("\n=== TOOL ITERATIONS ===")
    print(result["tool_iterations"])

    print("\n=== ANALYSIS ===")
    print(result["analysis"])

    print("\n=== REMEDIATION ===")
    print(result["remediation_proposal"])


if __name__ == "__main__":
    asyncio.run(main())
