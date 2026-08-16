from app.tools.infrastructure import (
    get_deployment_status,
    get_service_logs,
    get_service_metrics,
)


def main() -> None:

    service = "payment-service"

    logs = get_service_logs.invoke({"service": service})

    metrics = get_service_metrics.invoke({"service": service})

    deployment = get_deployment_status.invoke({"service": service})

    print("\nLogs:")
    print(logs)

    print("\nMetrics:")
    print(metrics)

    print("\nDeployment:")
    print(deployment)


if __name__ == "__main__":
    main()
