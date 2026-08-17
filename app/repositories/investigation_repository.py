import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.incident import Incident
from app.db.models.investigation import (
    InvestigationEvidence,
    InvestigationRun,
)


class InvestigationRepository:

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_run(
        self,
        incident_id: uuid.UUID,
    ) -> InvestigationRun:

        run = InvestigationRun(
            incident_id=incident_id,
            status="RUNNING",
        )

        self.session.add(run)

        await self.session.commit()
        await self.session.refresh(run)

        return run

    async def get_run(
        self,
        run_id: uuid.UUID,
    ) -> InvestigationRun | None:

        result = await self.session.execute(
            select(InvestigationRun).where(
                InvestigationRun.id == run_id
            )
        )

        return result.scalar_one_or_none()

    async def get_run_for_update(
        self,
        run_id: uuid.UUID,
    ) -> InvestigationRun | None:
        result = await self.session.execute(
            select(InvestigationRun)
            .where(InvestigationRun.id == run_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def save_evidence(
        self,
        run_id: uuid.UUID,
        evidence: list[dict[str, Any]],
    ) -> None:

        for item in evidence:
            record = InvestigationEvidence(
                investigation_run_id=run_id,
                tool=item["tool"],
                status=item["status"],
                finding=item["finding"],
            )

            self.session.add(record)

        await self.session.commit()

    async def complete_run(
        self,
        run: InvestigationRun,
        result: dict[str, Any],
    ) -> InvestigationRun:

        run.status = "COMPLETED"

        run.classification = result[
            "classification"
        ]

        run.investigation_plan = result[
            "investigation_plan"
        ]

        run.analysis = result[
            "analysis"
        ]

        run.remediation_proposal = result.get(
            "remediation_proposal"
        )

        run.runbooks = result.get("runbooks", [])
        run.historical_incidents = result.get(
            "historical_incidents",
            [],
        )

        if run.remediation_proposal:
            run.approval_status = "PENDING"
            run.remediation_status = "NOT_STARTED"

        run.tool_iterations = result[
            "tool_iterations"
        ]

        run.completed_at = datetime.now(
            UTC
        )

        await self.session.commit()
        await self.session.refresh(run)

        return run

    async def fail_run(
        self,
        run: InvestigationRun,
        result: dict[str, Any] | None = None,
    ) -> None:

        run.status = "FAILED"

        if result:
            run.classification = result.get(
                "classification"
            ) or None
            run.investigation_plan = result.get(
                "investigation_plan"
            ) or None
            run.runbooks = result.get(
                "runbooks",
                [],
            )
            run.historical_incidents = result.get(
                "historical_incidents",
                [],
            )
            run.tool_iterations = result.get(
                "tool_iterations",
                0,
            )

        run.completed_at = datetime.now(
            UTC
        )

        await self.session.commit()

    async def get_evidence(
        self,
        run_id: uuid.UUID,
    ) -> list[InvestigationEvidence]:

        result = await self.session.execute(
            select(InvestigationEvidence)
            .where(
                InvestigationEvidence.investigation_run_id
                == run_id
            )
            .order_by(
                InvestigationEvidence.created_at.asc()
            )
        )

        return list(result.scalars().all())

    async def approve_run(
        self,
        run: InvestigationRun,
    ) -> InvestigationRun:
        run.approval_status = "APPROVED"
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def reject_run(
        self,
        run: InvestigationRun,
    ) -> InvestigationRun:
        run.approval_status = "REJECTED"
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def update_remediation_status(
        self,
        run: InvestigationRun,
        status: str,
        result: dict[str, Any] | None = None,
    ) -> InvestigationRun:
        run.remediation_status = status
        run.remediation_result = result
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get_recent_completed_runs(
        self,
        incident_id: uuid.UUID,
        limit: int = 5,
    ) -> list[InvestigationRun]:
        result = await self.session.execute(
            select(InvestigationRun)
            .where(
                InvestigationRun.status == "COMPLETED",
                InvestigationRun.incident_id != incident_id,
            )
            .order_by(
                InvestigationRun.completed_at.desc()
            )
            .limit(limit)
        )
        return list(result.scalars().all())


    async def get_runs_by_incident(
        self,
        incident_id: uuid.UUID,
    ) -> list[InvestigationRun]:

        result = await self.session.execute(
            select(InvestigationRun)
            .where(
                InvestigationRun.incident_id
                == incident_id
            )
            .order_by(
                InvestigationRun.started_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_all_runs(
        self,
    ) -> list[tuple[InvestigationRun, Incident]]:
        result = await self.session.execute(
            select(InvestigationRun, Incident)
            .join(Incident, Incident.id == InvestigationRun.incident_id)
            .order_by(InvestigationRun.started_at.desc())
        )
        return list(result.tuples().all())

    async def get_remediation_runs(
        self,
    ) -> list[tuple[InvestigationRun, Incident]]:
        result = await self.session.execute(
            select(InvestigationRun, Incident)
            .join(Incident, Incident.id == InvestigationRun.incident_id)
            .where(InvestigationRun.remediation_proposal.is_not(None))
            .order_by(InvestigationRun.completed_at.desc())
        )
        return list(result.tuples().all())
