from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agents.investigation.nodes import (
    agent_node,
    analyze_evidence,
    classify_incident,
    collect_tool_evidence,
    create_investigation_plan,
    finalize_investigation,
    increment_tool_iteration,
)
from app.agents.investigation.routing import route_agent
from app.agents.investigation.state import InvestigationState
from app.mcp.tools import load_infrastructure_tools


async def build_investigation_graph():

    tools = await load_infrastructure_tools()

    tool_node = ToolNode(tools)

    async def run_agent(
        state: InvestigationState,
    ) -> dict:
        return await agent_node(
            state,
            tools,
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
        "finalize",
    )

    graph.add_edge(
        "finalize",
        END,
    )

    return graph.compile()