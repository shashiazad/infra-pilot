from app.infrastructure.kubernetes_client import (
    get_custom_objects_api,
)


def main() -> None:
    api = get_custom_objects_api()

    metrics = (
        api.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace="infrapilot-demo",
            plural="pods",
        )
    )

    for item in metrics.get(
        "items",
        [],
    ):
        print(
            "\nPod:",
            item["metadata"]["name"],
        )

        for container in item.get(
            "containers",
            [],
        ):
            print(
                container["name"],
                container["usage"],
            )


if __name__ == "__main__":
    main()