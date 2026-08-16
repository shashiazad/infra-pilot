import uuid
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.investigation.graph import (
    build_investigation_graph,
)
from app.remediation.executor import execute_remediation
from app.repositories.incident_repository import (
    IncidentRepository,
)
from app.repositories.investigation_repository import (
    InvestigationRepository,
)


class InvestigationService:

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        self.session = session

        self.incident_repository = (
            IncidentRepository(session)
        )

        self.investigation_repository = (
            InvestigationRepository(session)
        )

    async def investigate(
        self,
        incident_id: uuid.UUID,
    ) -> dict[str, Any] | None:

        incident = (
            await self.incident_repository.get_by_id(
                incident_id
            )
        )

        if incident is None:
            return None

        run = (
            await self.investigation_repository.create_run(
                incident_id
            )
        )

        try:

            graph = (
                await build_investigation_graph(
                    self.session,
                    self,
                )
            )

            initial_state = {
                "incident_id": str(
                    incident.id
                ),

                "incident": {
                    "title": incident.title,
                    "description": (
                        incident.description
                    ),
                    "service": incident.service,
                    "severity": incident.severity,
                    "status": incident.status,
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

            result = await graph.ainvoke(
                initial_state
            )

            await (
                self.investigation_repository
                .save_evidence(
                    run.id,
                    result["evidence"],
                )
            )

            completed_run = await (
                self.investigation_repository
                .complete_run(
                    run,
                    result,
                )
            )

            return {
                "run_id": completed_run.id,
                "status": (
                    completed_run.status
                ),
                "classification": result[
                    "classification"
                ],
                "investigation_plan": result[
                    "investigation_plan"
                ],
                "evidence": result[
                    "evidence"
                ],
                "analysis": result[
                    "analysis"
                ],
                "remediation_proposal": result[
                    "remediation_proposal"
                ],
                "approval_status": (
                    completed_run.approval_status
                ),
                "remediation_status": (
                    completed_run.remediation_status
                ),
                "tool_iterations": result[
                    "tool_iterations"
                ],
            }

        except Exception:

            await (
                self.investigation_repository
                .fail_run(run)
            )

            raise

    async def get_investigation(
        self,
        run_id: uuid.UUID,
    ) -> dict[str, Any] | None:

        run = await (
            self.investigation_repository
            .get_run(run_id)
        )

        if run is None:
            return None

        evidence = await (
            self.investigation_repository
            .get_evidence(run_id)
        )

        return {
            "run_id": run.id,
            "incident_id": run.incident_id,
            "status": run.status,
            "classification": run.classification,
            "investigation_plan": run.investigation_plan,
            "analysis": run.analysis,
            "remediation_proposal": (
                run.remediation_proposal
            ),
            "approval_status": run.approval_status,
            "remediation_status": run.remediation_status,
            "remediation_result": run.remediation_result,
            "runbooks": run.runbooks or [],
            "historical_incidents": run.historical_incidents or [],
            "tool_iterations": run.tool_iterations,
            "evidence": [
                {
                    "tool": item.tool,
                    "status": item.status,
                    "finding": item.finding,
                    "created_at": item.created_at,
                }
                for item in evidence
            ],
            "started_at": run.started_at,
            "completed_at": run.completed_at,
        }

    async def get_incident_investigations(
        self,
        incident_id: uuid.UUID,
    ) -> list[dict[str, Any]]:

        runs = await (
            self.investigation_repository
            .get_runs_by_incident(
                incident_id
            )
        )

        return [
            {
                "run_id": run.id,
                "incident_id": run.incident_id,
                "status": run.status,
                "tool_iterations": run.tool_iterations,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
            }
            for run in runs
        ]

    async def get_investigations(self) -> list[dict[str, Any]]:
        rows = await self.investigation_repository.get_all_runs()
        return [
            {
                "run_id": run.id,
                "incident_id": run.incident_id,
                "incident_title": incident.title,
                "service": incident.service,
                "severity": incident.severity,
                "status": run.status,
                "tool_iterations": run.tool_iterations,
                "confidence": (
                    run.analysis or {}
                ).get("confidence"),
                "started_at": run.started_at,
                "completed_at": run.completed_at,
            }
            for run, incident in rows
        ]

    async def get_remediations(self) -> list[dict[str, Any]]:
        rows = await self.investigation_repository.get_remediation_runs()
        results = []
        for run, incident in rows:
            proposal = run.remediation_proposal or {}
            results.append(
                {
                    "run_id": run.id,
                    "incident_id": run.incident_id,
                    "incident_title": incident.title,
                    "service": incident.service,
                    "time": run.completed_at or run.started_at,
                    "action": proposal.get("action", "UNKNOWN"),
                    "target": proposal.get("target_service", incident.service),
                    "risk": proposal.get("risk", "UNKNOWN"),
                    "approval_status": run.approval_status,
                    "remediation_status": run.remediation_status,
                    "result": run.remediation_result,
                }
            )
        return results

    async def get_historical_context(
        self,
        incident_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        runs = await (
            self.investigation_repository
            .get_recent_completed_runs(
                incident_id,
                limit=5,
            )
        )
        return [
            {
                "run_id": str(run.id),
                "classification": run.classification,
                "analysis": run.analysis,
                "tool_iterations": run.tool_iterations,
            }
            for run in runs
        ]

    async def approve_investigation(
        self,
        run_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        run = await (
            self.investigation_repository
            .get_run_for_update(run_id)
        )
        if run is None:
            return None
        if not run.remediation_proposal:
            raise ValueError(
                "No remediation proposal exists."
            )
        if run.approval_status == "REJECTED":
            raise ValueError(
                "Remediation has already been rejected."
            )
        if run.approval_status == "APPROVED":
            return self._approval_response(run)
        if run.approval_status != "PENDING":
            raise ValueError(
                "Remediation is not pending approval."
            )

        run = await (
            self.investigation_repository
            .approve_run(run)
        )
        return self._approval_response(run)

    async def reject_investigation(
        self,
        run_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        run = await (
            self.investigation_repository
            .get_run_for_update(run_id)
        )
        if run is None:
            return None
        if not run.remediation_proposal:
            raise ValueError(
                "No remediation proposal exists."
            )
        if run.approval_status == "APPROVED":
            raise ValueError(
                "Remediation has already been approved."
            )
        if run.approval_status == "REJECTED":
            return self._approval_response(run)
        if run.approval_status != "PENDING":
            raise ValueError(
                "Remediation is not pending approval."
            )

        run = await (
            self.investigation_repository
            .reject_run(run)
        )
        return self._approval_response(run)

    async def execute_approved_remediation(
        self,
        run_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        run = await (
            self.investigation_repository
            .get_run_for_update(run_id)
        )
        if run is None:
            return None
        if not run.remediation_proposal:
            raise ValueError(
                "No remediation proposal exists."
            )
        if run.approval_status != "APPROVED":
            raise ValueError(
                "Remediation is not approved."
            )
        if run.remediation_status == "COMPLETED":
            return self._execution_response(run)
        if run.remediation_status in {"RUNNING", "FAILED"}:
            raise ValueError(
                "Remediation has already been attempted."
            )
        if run.remediation_status != "NOT_STARTED":
            raise ValueError(
                "Remediation is not ready to execute."
            )

        await (
            self.investigation_repository
            .update_remediation_status(
                run,
                "RUNNING",
            )
        )

        try:
            result = await execute_remediation(
                run.remediation_proposal
            )
            status_value = (
                "COMPLETED"
                if result.get("success")
                else "FAILED"
            )
        except Exception as exc:
            result = {
                "success": False,
                "error": str(exc),
            }
            status_value = "FAILED"

        run = await (
            self.investigation_repository
            .update_remediation_status(
                run,
                status_value,
                result,
            )
        )
        return self._execution_response(run)

    @staticmethod
    def _approval_response(run) -> dict[str, Any]:
        return {
            "run_id": run.id,
            "approval_status": run.approval_status,
            "remediation_status": run.remediation_status,
        }

    @staticmethod
    def _execution_response(run) -> dict[str, Any]:
        return {
            "run_id": run.id,
            "approval_status": run.approval_status,
            "remediation_status": run.remediation_status,
            "remediation_result": run.remediation_result,
        }

    async def stream_investigation(
        self,
        incident_id: uuid.UUID,
    ) -> AsyncGenerator[dict[str, Any], None]:

        incident = await (
            self.incident_repository
            .get_by_id(incident_id)
        )

        if incident is None:
            yield {
                "event": "error",
                "data": {
                    "message": "Incident not found",
                },
            }
            return

        graph = await build_investigation_graph(
            self.session,
            self,
        )

        initial_state = {
            "incident_id": str(incident.id),

            "incident": {
                "title": incident.title,
                "description": incident.description,
                "service": incident.service,
                "severity": incident.severity,
                "status": incident.status,
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

        yield {
            "event": "investigation_started",
            "data": {
                "incident_id": str(
                    incident.id
                ),
            },
        }

        async for update in graph.astream(
            initial_state,
            stream_mode="updates",
        ):

            for node_name, _node_data in (
                update.items()
            ):

                yield {
                    "event": (
                        self._get_event_name(
                            node_name
                        )
                    ),
                    "data": {
                        "node": node_name,
                    },
                }

        yield {
            "event": "investigation_completed",
            "data": {
                "incident_id": str(
                    incident.id
                ),
            },
        }

    def _get_event_name(
        self,
        node_name: str,
    ) -> str:

        events = {
            "classify": (
                "classification_completed"
            ),
            "plan": "plan_created",
            "retrieve_runbooks": (
                "runbooks_retrieved"
            ),
            "retrieve_history": (
                "history_retrieved"
            ),
            "agent": "agent_updated",
            "tools": "tools_executed",
            "collect_evidence": (
                "evidence_collected"
            ),
            "increment_iteration": (
                "iteration_completed"
            ),
            "analyze": (
                "analysis_completed"
            ),
            "propose_remediation": (
                "remediation_proposed"
            ),
            "finalize": (
                "investigation_finalized"
            ),
        }

        return events.get(
            node_name,
            "graph_updated",
        )
