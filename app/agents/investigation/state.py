from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class InvestigationState(TypedDict):
    incident_id: str

    incident: dict

    classification: dict

    investigation_plan: list[str]

    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    evidence: list[dict]

    tool_iterations: int

    max_tool_iterations: int

    analysis: dict

    final_result: dict