import asyncio
import math
from typing import Any

from app.infrastructure.kubernetes_client import (
    get_apps_api,
    get_core_api,
    get_custom_objects_api,
)
from app.infrastructure.prometheus_client import query_prometheus
from app.schemas.service import PodSnapshot, ServiceSnapshot


class ServiceInventoryService:
    async def list_services(
        self,
        namespace: str,
    ) -> list[ServiceSnapshot]:
        return await asyncio.to_thread(self._kubernetes_snapshot, namespace)

    def _kubernetes_snapshot(
        self,
        namespace: str,
    ) -> list[ServiceSnapshot]:
        apps_api = get_apps_api()
        core_api = get_core_api()
        metrics_api = get_custom_objects_api()
        deployments = apps_api.list_namespaced_deployment(namespace).items
        pods = core_api.list_namespaced_pod(namespace).items
        try:
            metrics_payload: dict[str, Any] = (
                metrics_api.list_namespaced_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    namespace=namespace,
                    plural="pods",
                )
            )
        except Exception:
            metrics_payload = {"items": []}
        metrics_by_pod = {
            item["metadata"]["name"]: item
            for item in metrics_payload.get("items", [])
        }
        try:
            warning_events = core_api.list_namespaced_event(
                namespace,
                field_selector="type=Warning",
            ).items
        except Exception:
            warning_events = []

        snapshots: list[ServiceSnapshot] = []
        for deployment in deployments:
            name = deployment.metadata.name
            selector = deployment.spec.selector.match_labels or {}
            selected_pods = [
                pod for pod in pods
                if all(
                    (pod.metadata.labels or {}).get(key) == value
                    for key, value in selector.items()
                )
            ]
            pod_snapshots = []
            for pod in selected_pods:
                statuses = pod.status.container_statuses or []
                pod_metrics = metrics_by_pod.get(pod.metadata.name, {})
                usage = [
                    container.get("usage", {})
                    for container in pod_metrics.get("containers", [])
                ]
                pod_snapshots.append(
                    PodSnapshot(
                        name=pod.metadata.name,
                        phase=pod.status.phase or "Unknown",
                        ready=bool(statuses) and all(item.ready for item in statuses),
                        restarts=sum(item.restart_count for item in statuses),
                        cpu=", ".join(
                            filter(None, (item.get("cpu") for item in usage))
                        )
                        or None,
                        memory=", ".join(
                            filter(None, (item.get("memory") for item in usage))
                        )
                        or None,
                    )
                )
            desired = deployment.spec.replicas or 0
            ready = deployment.status.ready_replicas or 0
            available = deployment.status.available_replicas or 0
            warnings = [
                event.message
                for event in warning_events
                if event.involved_object.name == name
                or any(event.involved_object.name == pod.name for pod in pod_snapshots)
            ][-5:]
            healthy = desired > 0 and ready == desired and available == desired
            snapshots.append(
                ServiceSnapshot(
                    service=name,
                    namespace=namespace,
                    health="HEALTHY" if healthy else "DEGRADED",
                    desired_replicas=desired,
                    ready_replicas=ready,
                    available_replicas=available,
                    restarts=sum(pod.restarts for pod in pod_snapshots),
                    cpu=" · ".join(
                        filter(None, (pod.cpu for pod in pod_snapshots))
                    )
                    or None,
                    memory=" · ".join(
                        filter(None, (pod.memory for pod in pod_snapshots))
                    )
                    or None,
                    deployment_status=f"{available}/{desired} available",
                    pods=pod_snapshots,
                    recent_warnings=warnings,
                )
            )
        return snapshots

    async def add_application_metrics(
        self,
        services: list[ServiceSnapshot],
    ) -> list[ServiceSnapshot]:
        if not services:
            return services
        error_query = (
            "100 * sum(rate(payment_http_requests_total{"
            'job="prod-demo-payment",status=~"5.."}[5m])) '
            "/ sum(rate(payment_http_requests_total{"
            'job="prod-demo-payment"}[5m]))'
        )
        latency_query = (
            "1000 * histogram_quantile(0.95, sum by (le) "
            "(rate(payment_http_request_duration_seconds_bucket{"
            'job="prod-demo-payment"}[5m])))'
        )
        try:
            error_rate, latency = await asyncio.gather(
                query_prometheus(error_query),
                query_prometheus(latency_query),
            )
        except Exception:
            error_rate, latency = None, None
        if error_rate is None or not math.isfinite(error_rate):
            try:
                error_rate = await query_prometheus(
                    "100 * sum(payment_http_requests_total{"
                    'job="prod-demo-payment",status=~"5.."}) '
                    "/ sum(payment_http_requests_total{"
                    'job="prod-demo-payment"})'
                )
            except Exception:
                error_rate = None
        if latency is None or not math.isfinite(latency):
            try:
                latency = await query_prometheus(
                    "1000 * histogram_quantile(0.95, sum by (le) "
                    "(payment_http_request_duration_seconds_bucket{"
                    'job="prod-demo-payment"}))'
                )
            except Exception:
                latency = None
        for service in services:
            if service.service == "prod-demo-payment":
                service.http_5xx_rate_percent = error_rate
                service.p95_latency_ms = latency
        return services
