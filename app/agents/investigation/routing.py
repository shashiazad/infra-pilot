from typing import Literal

from app.agents.investigation.state import InvestigationState


def route_agent(
    state: InvestigationState,
) -> Literal["tools", "analyze"]:

    if (
        state["tool_iterations"]
        >= state["max_tool_iterations"]
    ):
        return "analyze"

    last_message = state["messages"][-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        None,
    )

    if tool_calls:
        return "tools"

    return "analyze"