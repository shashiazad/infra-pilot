from typing import Any

from mcp.server import MCPServer

mcp = MCPServer("InfraPilot Infrastructure")


@mcp.tool()
def get_service_logs(service: str) -> dict[str, Any]:
    """
    Retrieve recent application logs for an infrastructure service.

    Use this when investigating application failures,
    HTTP errors, crashes, or unexpected service behavior.
    """

    mock_logs = {
        "payment-service": {
            "service": "payment-service",
            "entries": [
                {
                    "level": "ERROR",
                    "message": "database connection timeout",
                },
                {
                    "level": "ERROR",
                    "message": "failed to process payment request",
                },
                {
                    "level": "ERROR",
                    "message": "database connection timeout",
                },
            ],
        }
    }

    return mock_logs.get(
        service,
        {
            "service": service,
            "entries": [],
            "message": "No recent error logs found.",
        },
    )


@mcp.tool()
def get_service_metrics(service: str) -> dict[str, Any]:
    """
    Retrieve CPU, memory, latency and error-rate metrics
    for an infrastructure service.
    """

    mock_metrics = {
        "payment-service": {
            "service": "payment-service",
            "cpu_usage_percent": 42,
            "memory_usage_percent": 68,
            "http_5xx_rate_percent": 31,
            "p95_latency_ms": 2800,
        }
    }

    return mock_metrics.get(
        service,
        {
            "service": service,
            "message": "No metrics available.",
        },
    )


@mcp.tool()
def get_deployment_status(service: str) -> dict[str, Any]:
    """
    Retrieve deployment health, replica state and
    recent deployment information for a service.
    """

    mock_deployments = {
        "payment-service": {
            "service": "payment-service",
            "deployment_status": "healthy",
            "ready_replicas": 3,
            "desired_replicas": 3,
            "last_deployment": "2026-08-15T18:30:00Z",
        }
    }

    return mock_deployments.get(
        service,
        {
            "service": service,
            "message": "No deployment information found.",
        },
    )
