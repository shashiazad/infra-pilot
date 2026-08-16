import json
import uuid
from typing import Protocol

from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.investigation.state import (
    InvestigationState,
)
from app.llm.groq import (
    create_groq_model,
    create_structured_groq_model,
)
from app.rag.retriever import retrieve_runbooks
from app.schemas.investigation import (
    IncidentClassification,
    InvestigationResult,
    RemediationProposal,
)


class HistoricalContextProvider(Protocol):
    async def get_historical_context(
        self,
        incident_id: uuid.UUID,
    ) -> list[dict]: ...


async def agent_node(
    state: InvestigationState,
    tools: list[BaseTool],
) -> dict:

    incident = state["incident"]
    plan = state["investigation_plan"]

    model = create_groq_model()

    model_with_tools = model.bind_tools(
        tools
    )

    messages = state["messages"]

    # Temporary debugging
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

When investigating Kubernetes workloads:

- Check pod status and restart counts when availability is affected.
- Check Kubernetes events for scheduling, crash, probe, or restart failures.
- Use logs to identify application-level failures.
- Use deployment status to compare desired and ready replicas.
- Correlate evidence across multiple tools before concluding a root cause.

Resource investigation rules:

1. Never invent Kubernetes service, deployment, pod, or dependency names.

2. Only call tools for:
   - the incident's specified service, or
   - another resource whose exact name was discovered from collected evidence.

3. A database-related error message does NOT imply that a Kubernetes resource
   named "database-service" exists.

4. Do not repeat the same tool call with identical arguments unless new evidence
   makes repetition necessary.

5. Before requesting another tool, inspect the evidence already collected.

6. Stop requesting tools when the available evidence is sufficient to explain
   the observed symptoms with reasonable confidence.

7. A Kubernetes 404 for a guessed resource is not evidence that the missing
   resource caused the incident.

8. Do not perform remediation. Investigation is read-only.
"""

        human_message = HumanMessage(
            content=prompt
        )

        response = await (
            model_with_tools.ainvoke(
                [human_message]
            )
        )

        print(
            "Tool calls:",
            response.tool_calls,
        )

        return {
            "messages": [
                human_message,
                response,
            ]
        }

    response = await (
        model_with_tools.ainvoke(
            messages
        )
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


def collect_tool_evidence(
    state: InvestigationState,
) -> dict:

    evidence = []

    for message in state["messages"]:

        if not isinstance(
            message,
            ToolMessage,
        ):
            continue

        finding = message.content

        if isinstance(finding, str):
            try:
                finding = json.loads(
                    finding
                )
            except json.JSONDecodeError:
                pass

        evidence.append(
            {
                "tool": message.name,
                "status": (
                    "ERROR"
                    if message.status == "error"
                    else "SUCCESS"
                ),
                "finding": finding,
            }
        )

    return {
        "evidence": evidence
    }


async def classify_incident(
    state: InvestigationState,
) -> dict:

    incident = state["incident"]

    model = create_structured_groq_model(
        IncidentClassification
    )

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

    result = await model.ainvoke(
        prompt
    )

    return {
        "classification": (
            result.model_dump()
        )
    }


def create_investigation_plan(
    state: InvestigationState,
) -> dict:

    classification = state[
        "classification"
    ]

    category = classification[
        "category"
    ]

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


async def retrieve_relevant_runbooks(
    state: InvestigationState,
    session: AsyncSession,
) -> dict:
    incident = state["incident"]
    query = f"""
Incident title:
{incident["title"]}

Description:
{incident["description"]}

Service:
{incident["service"]}

Classification:
{state["classification"]}
"""
    runbooks = await retrieve_runbooks(
        session=session,
        query=query,
    )
    return {"runbooks": runbooks}


async def retrieve_historical_incidents(
    state: InvestigationState,
    investigation_service: HistoricalContextProvider,
) -> dict:
    history = await (
        investigation_service.get_historical_context(
            uuid.UUID(state["incident_id"])
        )
    )
    return {"historical_incidents": history}


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

Relevant operational runbooks:
{state["runbooks"]}

Previous investigation history:
{state["historical_incidents"]}

Runbook interpretation rules:

1. Runbooks are operational guidance, not live evidence.

2. Do not treat runbook symptoms as confirmed facts.

3. Use runbooks to suggest relevant checks and interpret live evidence.

4. Live infrastructure evidence takes precedence over runbook guidance.

Historical incident rules:

1. Previous incidents are contextual evidence, not proof of the current root cause.

2. Do not assume the current incident has the same cause.

3. Use prior incidents only to identify useful patterns and checks.

4. Live infrastructure evidence takes precedence.

Evidence interpretation rules:

1. confirmed_facts must contain facts directly supported by collected evidence.

2. Do not convert hypotheses into confirmed facts.

3. Do not treat failed lookups for guessed resources as evidence of root cause.

4. Do not describe CPU or memory utilization as high unless a threshold,
   configured limit, baseline, or saturation signal supports that conclusion.

5. Distinguish observed symptoms from possible root causes.

6. Prefer conclusions supported by correlated evidence across logs,
   Kubernetes deployment status, pod status, and Kubernetes events.

7. A log message mentioning a database does not prove that a Kubernetes
   database deployment exists.

8. Clearly identify uncertainty when the available evidence cannot establish
   the exact root cause.
"""

    result = await model.ainvoke(
        prompt
    )

    return {
        "analysis": result.model_dump()
    }


async def propose_remediation(
    state: InvestigationState,
) -> dict:
    model = create_structured_groq_model(
        RemediationProposal
    )
    incident = state["incident"]
    prompt = f"""
You are proposing a safe remediation for an
infrastructure incident.

Incident:
{incident}

Analysis:
{state["analysis"]}

Evidence:
{state["evidence"]}

Operational runbooks:
{state["runbooks"]}

Rules:

1. Do not claim the remediation has been executed.
2. Do not perform any action.
3. Propose only one primary remediation.
4. Prefer reversible actions.
5. Do not propose destructive actions such as deleting databases,
   namespaces, persistent volumes, or data.
6. The action must require human approval.
7. If the root cause is uncertain, propose further investigation
   rather than a risky remediation.
"""
    result = await model.ainvoke(prompt)
    proposal = result.model_dump()
    proposal["requires_approval"] = True
    return {"remediation_proposal": proposal}


def finalize_investigation(
    state: InvestigationState,
) -> dict:

    return {
        "final_result": {
            "classification": (
                state["classification"]
            ),
            "investigation_plan": (
                state[
                    "investigation_plan"
                ]
            ),
            "evidence": state.get(
                "evidence",
                [],
            ),
            "runbooks": state.get(
                "runbooks",
                [],
            ),
            "historical_incidents": state.get(
                "historical_incidents",
                [],
            ),
            "remediation_proposal": state.get(
                "remediation_proposal",
                {},
            ),
            "analysis": state[
                "analysis"
            ],
            "tool_iterations": state[
                "tool_iterations"
            ],
        }
    }
