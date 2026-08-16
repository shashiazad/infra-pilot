from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.investigation.nodes import (
    HistoricalContextProvider,
    agent_node,
    analyze_evidence,
    classify_incident,
    collect_tool_evidence,
    create_investigation_plan,
    finalize_investigation,
    increment_tool_iteration,
    propose_remediation,
    retrieve_historical_incidents,
    retrieve_relevant_runbooks,
)
from app.agents.investigation.routing import route_agent
from app.agents.investigation.state import InvestigationState
from app.mcp.tools import load_infrastructure_tools


async def build_investigation_graph(
    session: AsyncSession,
    investigation_service: HistoricalContextProvider,
):

    tools = await load_infrastructure_tools()

    tool_node = ToolNode(
        tools,
        handle_tool_errors=True,
    )

    async def run_agent(
        state: InvestigationState,
    ) -> dict:
        return await agent_node(
            state,
            tools,
        )

    async def run_runbook_retrieval(
        state: InvestigationState,
    ) -> dict:
        return await retrieve_relevant_runbooks(
            state,
            session,
        )

    async def run_history_retrieval(
        state: InvestigationState,
    ) -> dict:
        return await retrieve_historical_incidents(
            state,
            investigation_service,
        )

    graph = StateGraph(
        InvestigationState
    )

    graph.add_node(
        "classify",
        classify_incident,
    )

    graph.add_node(
        "plan",
        create_investigation_plan,
    )

    graph.add_node(
        "agent",
        run_agent,
    )

    graph.add_node(
        "retrieve_runbooks",
        run_runbook_retrieval,
    )

    graph.add_node(
        "retrieve_history",
        run_history_retrieval,
    )

    graph.add_node(
        "tools",
        tool_node,
    )

    graph.add_node(
        "collect_evidence",
        collect_tool_evidence,
    )

    graph.add_node(
        "increment_iteration",
        increment_tool_iteration,
    )

    graph.add_node(
        "analyze",
        analyze_evidence,
    )

    graph.add_node(
        "propose_remediation",
        propose_remediation,
    )

    graph.add_node(
        "finalize",
        finalize_investigation,
    )

    graph.add_edge(
        START,
        "classify",
    )

    graph.add_edge(
        "classify",
        "plan",
    )

    graph.add_edge(
        "plan",
        "retrieve_runbooks",
    )

    graph.add_edge(
        "retrieve_runbooks",
        "retrieve_history",
    )

    graph.add_edge(
        "retrieve_history",
        "agent",
    )

    graph.add_conditional_edges(
        "agent",
        route_agent,
        {
            "tools": "tools",
            "analyze": "analyze",
        },
    )

    graph.add_edge(
        "tools",
        "collect_evidence",
    )

    graph.add_edge(
        "collect_evidence",
        "increment_iteration",
    )

    graph.add_edge(
        "increment_iteration",
        "agent",
    )

    graph.add_edge(
        "analyze",
        "propose_remediation",
    )

    graph.add_edge(
        "propose_remediation",
        "finalize",
    )

    graph.add_edge(
        "finalize",
        END,
    )

    return graph.compile()
