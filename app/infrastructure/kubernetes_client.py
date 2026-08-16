from kubernetes import client, config


def load_kubernetes_config() -> None:
    config.load_kube_config(
        context="kind-infrapilot"
    )


def get_core_api() -> client.CoreV1Api:
    load_kubernetes_config()

    return client.CoreV1Api()


def get_apps_api() -> client.AppsV1Api:
    load_kubernetes_config()

    return client.AppsV1Api()

def get_custom_objects_api() -> client.CustomObjectsApi:
    load_kubernetes_config()

    return client.CustomObjectsApi()