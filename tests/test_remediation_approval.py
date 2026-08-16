import uuid
from types import SimpleNamespace

import pytest

from app.services.investigation_service import InvestigationService

pytestmark = pytest.mark.asyncio


class FakeInvestigationRepository:
    def __init__(self, run) -> None:
        self.run = run

    async def get_run_for_update(self, run_id):
        return self.run

    async def approve_run(self, run):
        run.approval_status = "APPROVED"
        return run

    async def reject_run(self, run):
        run.approval_status = "REJECTED"
        return run

    async def update_remediation_status(
        self,
        run,
        status,
        result=None,
    ):
        run.remediation_status = status
        run.remediation_result = result
        return run


def make_service(run) -> InvestigationService:
    service = InvestigationService(SimpleNamespace())
    service.investigation_repository = (
        FakeInvestigationRepository(run)
    )
    return service


def make_run(**overrides):
    values = {
        "id": uuid.uuid4(),
        "approval_status": "PENDING",
        "remediation_status": "NOT_STARTED",
        "remediation_proposal": {
            "action": "RESTART_DEPLOYMENT",
            "target_service": "prod-demo-payment",
        },
        "remediation_result": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


async def test_execute_requires_approval() -> None:
    service = make_service(make_run())

    with pytest.raises(
        ValueError,
        match="Remediation is not approved",
    ):
        await service.execute_approved_remediation(
            uuid.uuid4()
        )


async def test_rejected_run_cannot_be_approved() -> None:
    service = make_service(
        make_run(approval_status="REJECTED")
    )

    with pytest.raises(
        ValueError,
        match="already been rejected",
    ):
        await service.approve_investigation(
            uuid.uuid4()
        )


async def test_completed_execution_is_idempotent(
    monkeypatch,
) -> None:
    run = make_run(
        approval_status="APPROVED",
        remediation_status="COMPLETED",
        remediation_result={"success": True},
    )
    service = make_service(run)

    async def fail_if_called(proposal):
        raise AssertionError("executor must not run twice")

    monkeypatch.setattr(
        "app.services.investigation_service.execute_remediation",
        fail_if_called,
    )
    result = await service.execute_approved_remediation(
        run.id
    )
    assert result["remediation_status"] == "COMPLETED"
