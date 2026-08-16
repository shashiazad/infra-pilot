from app.infrastructure.kubernetes_client import (
    get_core_api,
)


def main() -> None:

    api = get_core_api()

    pods = api.list_namespaced_pod(
        namespace="prod-demo"
    )

    for pod in pods.items:
        print(
            pod.metadata.name,
            pod.status.phase,
        )


if __name__ == "__main__":
    main()
