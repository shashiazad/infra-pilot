import pytest

from app.remediation import executor

pytestmark = pytest.mark.asyncio


class FakeAppsApi:
    def __init__(self) -> None:
        self.calls = []

    def patch_namespaced_deployment(self, **kwargs) -> None:
        self.calls.append(kwargs)


async def test_executor_rejects_non_allow_listed_action() -> None:
    result = await executor.execute_remediation(
        {
            "action": "RUN_SHELL_COMMAND",
            "target_service": "prod-demo-payment",
            "commands": ["echo unsafe"],
        }
    )
    assert result["success"] is False
    assert "not allow-listed" in result["error"]


async def test_executor_uses_kubernetes_api(monkeypatch) -> None:
    api = FakeAppsApi()
    monkeypatch.setattr(
        executor,
        "get_apps_api",
        lambda: api,
    )

    result = await executor.execute_remediation(
        {
            "action": "RESTART_DEPLOYMENT",
            "target_service": "prod-demo-payment",
            "commands": ["this value must be ignored"],
        }
    )

    assert result == {
        "success": True,
        "action": "RESTART_DEPLOYMENT",
        "service": "prod-demo-payment",
        "namespace": "prod-demo",
    }
    assert len(api.calls) == 1
    assert api.calls[0]["name"] == "prod-demo-payment"
    assert api.calls[0]["namespace"] == "prod-demo"
