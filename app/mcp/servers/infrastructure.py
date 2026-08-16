from typing import Any

from kubernetes.client.exceptions import ApiException
from mcp.server import MCPServer

from app.core.config import settings
from app.infrastructure.kubernetes_client import (
    get_apps_api,
    get_core_api,
    get_custom_objects_api,
)
from app.infrastructure.prometheus_client import (
    query_prometheus,
)

mcp = MCPServer("InfraPilot Infrastructure")


@mcp.tool()
def get_service_logs(
    service: str,
    namespace: str = settings.kubernetes_namespace,
) -> dict[str, Any]:
    """
    Retrieve recent Kubernetes pod logs for a service.

    Use when investigating application errors,
    crashes, or unexpected service behavior.
    """

    api = get_core_api()

    try:
        pods = api.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"app={service}",
        )

        results = []

        for pod in pods.items:

            pod_name = pod.metadata.name

            logs = api.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=50,
            )

            if isinstance(logs, bytes):
                logs = logs.decode(
                    "utf-8",
                    errors="replace",
                )

            results.append(
                {
                    "pod": pod_name,
                    "logs": logs.splitlines(),
                }
            )

        return {
            "service": service,
            "namespace": namespace,
            "pods": results,
        }

    except ApiException as exc:

        return {
            "service": service,
            "namespace": namespace,
            "error": str(exc),
        }


@mcp.tool()
def get_service_metrics(
    service: str,
    namespace: str = settings.kubernetes_namespace,
) -> dict[str, Any]:
    """
    Retrieve current Kubernetes CPU and memory usage
    for pods belonging to a service.
    """

    metrics_api = get_custom_objects_api()
    core_api = get_core_api()

    try:
        pods = core_api.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"app={service}",
        )

        pod_names = {
            pod.metadata.name
            for pod in pods.items
        }

        metrics = (
            metrics_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods",
            )
        )

        results = []

        for item in metrics.get(
            "items",
            [],
        ):
            pod_name = item[
                "metadata"
            ]["name"]

            if pod_name not in pod_names:
                continue

            containers = []

            for container in item.get(
                "containers",
                [],
            ):
                usage = container[
                    "usage"
                ]

                containers.append(
                    {
                        "name": container["name"],
                        "cpu": usage.get(
                            "cpu"
                        ),
                        "memory": usage.get(
                            "memory"
                        ),
                    }
                )

            results.append(
                {
                    "pod": pod_name,
                    "containers": containers,
                }
            )

        return {
            "service": service,
            "namespace": namespace,
            "pods": results,
        }

    except ApiException as exc:
        return {
            "service": service,
            "namespace": namespace,
            "error": str(exc),
        }


@mcp.tool()
async def get_application_metrics(
    service: str,
    namespace: str = settings.kubernetes_namespace,
) -> dict[str, Any]:
    """
    Retrieve application-level HTTP metrics
    from Prometheus.
    """

    error_rate_query = """
    100 *
    (
        sum(
            rate(
                payment_http_requests_total{
                    status=~"5.."
                }[5m]
            )
        )
        /
        sum(
            rate(
                payment_http_requests_total[5m]
            )
        )
    )
    """

    p95_latency_query = """
    1000 *
    histogram_quantile(
        0.95,
        sum by (le) (
            rate(
                payment_http_request_duration_seconds_bucket[5m]
            )
        )
    )
    """

    error_rate = await query_prometheus(
        error_rate_query
    )

    p95_latency = await query_prometheus(
        p95_latency_query
    )

    return {
        "service": service,
        "namespace": namespace,
        "http_5xx_rate_percent": error_rate,
        "p95_latency_ms": p95_latency,
    }

@mcp.tool()
def get_deployment_status(
    service: str,
    namespace: str = settings.kubernetes_namespace,
) -> dict[str, Any]:
    """
    Retrieve Kubernetes deployment status and replica health.
    """

    api = get_apps_api()

    try:

        deployment = (
            api.read_namespaced_deployment(
                name=service,
                namespace=namespace,
            )
        )

        return {
            "service": service,
            "namespace": namespace,

            "replicas": (
                deployment.status.replicas or 0
            ),

            "ready_replicas": (
                deployment.status.ready_replicas
                or 0
            ),

            "available_replicas": (
                deployment.status.available_replicas
                or 0
            ),

            "unavailable_replicas": (
                deployment.status.unavailable_replicas
                or 0
            ),

            "updated_replicas": (
                deployment.status.updated_replicas
                or 0
            ),
        }

    except ApiException as exc:

        return {
            "service": service,
            "namespace": namespace,
            "error": str(exc),
        }

@mcp.tool()
def get_pod_status(
    service: str,
    namespace: str = settings.kubernetes_namespace,
) -> dict[str, Any]:

    api = get_core_api()

    try:
        pods = api.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"app={service}",
        )

        results = []

        for pod in pods.items:
            containers = []

            for container in (
                pod.status.container_statuses or []
            ):
                containers.append(
                    {
                        "name": container.name,
                        "ready": container.ready,
                        "restart_count": container.restart_count,
                    }
                )

            results.append(
                {
                    "pod": pod.metadata.name,
                    "phase": pod.status.phase,
                    "pod_ip": pod.status.pod_ip,
                    "containers": containers,
                }
            )

        return {
            "service": service,
            "namespace": namespace,
            "pods": results,
        }

    except ApiException as exc:
        return {
            "service": service,
            "namespace": namespace,
            "error": str(exc),
        }

@mcp.tool()
def get_pod_events(
    service: str,
    namespace: str = settings.kubernetes_namespace,
) -> dict[str, Any]:

    api = get_core_api()

    try:
        pods = api.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"app={service}",
        )

        pod_names = {
            pod.metadata.name
            for pod in pods.items
        }

        events = api.list_namespaced_event(
            namespace=namespace
        )

        results = []

        for event in events.items:
            involved_name = (
                event.involved_object.name
            )

            if involved_name not in pod_names:
                continue

            results.append(
                {
                    "pod": involved_name,
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "count": event.count,
                }
            )

        return {
            "service": service,
            "namespace": namespace,
            "events": results,
        }

    except ApiException as exc:
        return {
            "service": service,
            "namespace": namespace,
            "error": str(exc),
        }
