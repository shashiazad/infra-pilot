import asyncio
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.infrastructure.kubernetes_client import get_apps_api

ALLOWED_ACTIONS = frozenset({"RESTART_DEPLOYMENT"})
DEFAULT_NAMESPACE = settings.kubernetes_namespace


async def execute_remediation(
    proposal: dict[str, Any],
) -> dict[str, Any]:
    action = proposal.get("action")

    if action not in ALLOWED_ACTIONS:
        return {
            "success": False,
            "error": f"Action {action!r} is not allow-listed.",
        }

    if action == "RESTART_DEPLOYMENT":
        return await restart_deployment(proposal)

    return {
        "success": False,
        "error": "Unsupported remediation action.",
    }


async def restart_deployment(
    proposal: dict[str, Any],
) -> dict[str, Any]:
    service = proposal.get("target_service")
    if not isinstance(service, str) or not service:
        return {
            "success": False,
            "error": "A target service is required.",
        }

    api = get_apps_api()
    body = {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "infrapilot/restarted-at": (
                            datetime.now(UTC).isoformat()
                        )
                    }
                }
            }
        }
    }
    await asyncio.to_thread(
        api.patch_namespaced_deployment,
        name=service,
        namespace=DEFAULT_NAMESPACE,
        body=body,
    )
    return {
        "success": True,
        "action": "RESTART_DEPLOYMENT",
        "service": service,
        "namespace": DEFAULT_NAMESPACE,
    }
