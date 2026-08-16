import pytest

from app.agents.investigation import nodes
from app.schemas.investigation import RemediationProposal


class FakeHistoryService:
    async def get_historical_context(self, incident_id):
        return [{"run_id": str(incident_id)}]


class FakeStructuredModel:
    async def ainvoke(self, prompt):
        return RemediationProposal(
            action="VERIFY_DATABASE_CONNECTIVITY",
            reason="The root cause is not yet confirmed.",
            target_service="prod-demo-payment",
            risk="LOW",
            commands=[],
            requires_approval=False,
        )


@pytest.mark.asyncio
async def test_retrieve_historical_incidents() -> None:
    incident_id = "00000000-0000-0000-0000-000000000001"
    result = await nodes.retrieve_historical_incidents(
        {"incident_id": incident_id},
        FakeHistoryService(),
    )
    assert result == {
        "historical_incidents": [
            {"run_id": incident_id}
        ]
    }


@pytest.mark.asyncio
async def test_remediation_always_requires_approval(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        nodes,
        "create_structured_groq_model",
        lambda schema: FakeStructuredModel(),
    )
    result = await nodes.propose_remediation(
        {
            "incident": {
                "service": "prod-demo-payment",
            },
            "analysis": {},
            "evidence": [],
            "runbooks": [],
        }
    )
    assert result["remediation_proposal"]["requires_approval"] is True
