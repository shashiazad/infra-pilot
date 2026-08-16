from langchain.messages import HumanMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool

from app.agents.investigation.state import InvestigationState
from app.llm.groq import create_groq_model, create_structured_groq_model
from app.schemas.investigation import IncidentClassification, InvestigationResult


async def agent_node(
    state: InvestigationState,
    tools: list[BaseTool],
) -> dict:


    incident = state["incident"]
    plan = state["investigation_plan"]

    model = create_groq_model()

    model_with_tools = model.bind_tools(tools)

    messages = state["messages"]

    #========testing=======
    print(
        f"\nAgent iteration: "
        f"{state['tool_iterations']}"
    )

    print(
        "Current message count:",
        len(messages),
    )

    if not messages:
        prompt = f"""
You are an infrastructure incident investigation agent.

Incident:

Title:
{incident["title"]}

Description:
{incident["description"]}

Service:
{incident["service"]}

Severity:
{incident["severity"]}

Investigation plan:
{plan}

Your goal is to gather enough evidence to identify
the most likely cause of the incident.

Rules:

1. Use infrastructure tools whenever evidence is needed.
2. Inspect tool results before choosing another action.
3. Do not fabricate logs, metrics, or deployment information.
4. Do not repeatedly call the same tool unless justified.
5. Stop requesting tools when enough evidence has been collected.
6. Do not perform remediation.
"""

        messages = [
            HumanMessage(content=prompt)
        ]

    response = await model_with_tools.ainvoke(
        messages
    )

    print(
        "Tool calls:",
        response.tool_calls,
    )

    return {
        "messages": [response]
    }


def increment_tool_iteration(
    state: InvestigationState,
) -> dict:

    return {
        "tool_iterations": (
            state["tool_iterations"] + 1
        )
    }


async def select_tools(
    state: InvestigationState,
    tools: list[BaseTool],
) -> dict:

    incident = state["incident"]
    plan = state["investigation_plan"]

    model = create_groq_model()

    model_with_tools = model.bind_tools(tools)

    prompt = f"""
You are investigating an infrastructure incident.

Incident:

Title:
{incident["title"]}

Description:
{incident["description"]}

Service:
{incident["service"]}

Severity:
{incident["severity"]}

Investigation plan:
{plan}

Select the infrastructure tools required to collect
evidence for this incident.

Rules:

- Call only relevant tools.
- Use the exact affected service name.
- Do not fabricate infrastructure information.
- Do not claim to have inspected data until a tool
  has actually been called.
"""

    response = await model_with_tools.ainvoke(prompt)

    return {"messages": [response]}


def collect_tool_evidence(
    state: InvestigationState,
) -> dict:

    evidence = []

    for message in state["messages"]:
        if isinstance(message, ToolMessage):
            evidence.append(
                {
                    "tool": message.name,
                    "status": "SUCCESS",
                    "finding": message.content,
                }
            )

    return {
        "evidence": evidence
    }

def classify_incident(
    state: InvestigationState,
) -> dict:

    incident = state["incident"]

    model = create_structured_groq_model(IncidentClassification)

    prompt = f"""
Classify the following infrastructure incident.

Title:
{incident["title"]}

Description:
{incident["description"]}

Service:
{incident["service"]}

Severity:
{incident["severity"]}

Possible categories:

- SERVICE_DEGRADATION
- SERVICE_OUTAGE
- PERFORMANCE
- DATABASE
- NETWORK
- INFRASTRUCTURE
- UNKNOWN

Possible priorities:

- LOW
- MEDIUM
- HIGH
- CRITICAL
"""

    result = model.invoke(prompt)

    return {"classification": result.model_dump()}


def create_investigation_plan(
    state: InvestigationState,
) -> dict:

    classification = state["classification"]

    category = classification["category"]

    plans = {
        "SERVICE_DEGRADATION": [
            "Inspect application logs",
            "Check service error rate",
            "Check resource utilization",
        ],
        "SERVICE_OUTAGE": [
            "Check service health",
            "Inspect recent deployments",
            "Inspect application logs",
        ],
        "DATABASE": [
            "Check database connectivity",
            "Check connection pool",
            "Inspect database errors",
        ],
        "NETWORK": [
            "Check network connectivity",
            "Inspect network errors",
            "Check service dependencies",
        ],
        "PERFORMANCE": [
            "Check CPU utilization",
            "Check memory utilization",
            "Check request latency",
        ],
        "INFRASTRUCTURE": [
            "Check infrastructure health",
            "Inspect resource utilization",
            "Inspect recent infrastructure changes",
        ],
        "UNKNOWN": [
            "Collect application logs",
            "Collect infrastructure metrics",
            "Inspect recent changes",
        ],
    }

    return {
        "investigation_plan": plans.get(
            category,
            plans["UNKNOWN"],
        )
    }


async def analyze_evidence(
    state: InvestigationState,
) -> dict:

    incident = state["incident"]

    model = create_structured_groq_model(
        InvestigationResult
    )

    prompt = f"""
You are performing the final analysis of an
infrastructure incident.

Incident:

Title:
{incident["title"]}

Description:
{incident["description"]}

Service:
{incident["service"]}

Severity:
{incident["severity"]}

Classification:
{state["classification"]}

Investigation plan:
{state["investigation_plan"]}

Collected infrastructure evidence:
{state["evidence"]}

Rules:

- Treat tool output as observed evidence.
- Do not invent additional telemetry.
- Clearly distinguish observed facts from hypotheses.
- Do not claim root-cause certainty unless the evidence supports it.
- Recommend further checks when uncertainty remains.
"""

    result = await model.ainvoke(prompt)

    return {
        "analysis": result.model_dump()
    }

def evaluate_evidence(
    state: InvestigationState,
) -> dict:

    evidence = state["evidence"]

    successful_evidence = [item for item in evidence if item["status"] == "SUCCESS"]

    evidence_sufficient = len(successful_evidence) > 0

    return {"evidence_sufficient": evidence_sufficient}


def finalize_investigation(
    state: InvestigationState,
) -> dict:

    return {
        "final_result": {
            "classification": state["classification"],
            "investigation_plan": state["investigation_plan"],
            "evidence": state.get("evidence", []),
            "analysis": state["analysis"],
            "evidence_attempts": state.get(
                "evidence_attempts",
                0,
            ),
            "evidence_sufficient": state.get(
                "evidence_sufficient",
                False,
            ),
        }
    }


def gather_evidence(
    state: InvestigationState,
) -> dict:

    attempt = state.get("evidence_attempts", 0) + 1

    if attempt == 2:
        evidence = [
            {
                "check": "Inspect application logs",
                "status": "SUCCESS",
                "finding": (
                    "Application logs show repeated database connection timeout errors."
                ),
                "attempt": attempt,
            }
        ]

    else:
        evidence = [
            {
                "check": "Inspect application logs",
                "status": "NOT_CONNECTED",
                "finding": "No evidence available.",
                "attempt": attempt,
            }
        ]

    return {
        "evidence": evidence,
        "evidence_attempts": attempt,
    }
