import uuid
from types import SimpleNamespace

import pytest

from app.services import investigation_service
from app.services.investigation_service import InvestigationService


class FakeIncidentRepository:
    def __init__(self, incident) -> None:
        self.incident = incident

    async def get_by_id(self, incident_id):
        return self.incident


class FakeInvestigationRepository:
    def __init__(self, run) -> None:
        self.run = run
        self.saved_evidence: list[dict] = []
        self.failed_result = None

    async def create_run(self, incident_id):
        return self.run

    async def save_evidence(self, run_id, evidence):
        self.saved_evidence.extend(evidence)

    async def fail_run(self, run, result=None):
        self.failed_result = result


class FailingGraph:
    async def astream(self, initial_state, stream_mode):
        yield initial_state
        yield {
            **initial_state,
            "classification": {
                "category": "DATABASE",
                "priority": "HIGH",
            },
            "investigation_plan": ["Inspect database errors"],
            "evidence": [
                {
                    "tool": "get_service_logs",
                    "status": "SUCCESS",
                    "finding": {"message": "timeout"},
                }
            ],
            "tool_iterations": 1,
        }
        raise RuntimeError("structured analysis failed")


@pytest.mark.asyncio
async def test_failed_run_preserves_partial_evidence(
    monkeypatch,
) -> None:
    incident_id = uuid.uuid4()
    incident = SimpleNamespace(
        id=incident_id,
        title="Database failure",
        description="Connections are timing out",
        service="prod-demo-postgres",
        severity="SEV-2",
        status="OPEN",
    )
    run = SimpleNamespace(id=uuid.uuid4())
    repository = FakeInvestigationRepository(run)
    service = InvestigationService(SimpleNamespace())
    service.incident_repository = FakeIncidentRepository(incident)
    service.investigation_repository = repository

    async def fake_build_graph(session, provider):
        return FailingGraph()

    monkeypatch.setattr(
        investigation_service,
        "build_investigation_graph",
        fake_build_graph,
    )

    with pytest.raises(
        RuntimeError,
        match="structured analysis failed",
    ):
        await service.investigate(incident_id)

    assert repository.saved_evidence == [
        {
            "tool": "get_service_logs",
            "status": "SUCCESS",
            "finding": {"message": "timeout"},
        }
    ]
    assert repository.failed_result["tool_iterations"] == 1
    assert repository.failed_result["classification"] == {
        "category": "DATABASE",
        "priority": "HIGH",
    }
