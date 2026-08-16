from urllib.parse import urlsplit, urlunsplit

from kubernetes import client, config

from app.core.config import settings


def load_kubernetes_config() -> None:
    config.load_kube_config(
        context=settings.kubernetes_context
    )
    if settings.kubernetes_host_alias:
        configuration = client.Configuration.get_default_copy()
        parsed = urlsplit(configuration.host)
        port = parsed.port
        host = settings.kubernetes_host_alias
        configuration.host = urlunsplit(
            (
                parsed.scheme,
                f"{host}:{port}" if port else host,
                parsed.path,
                parsed.query,
                parsed.fragment,
            )
        )
        if settings.kubernetes_tls_server_name:
            configuration.tls_server_name = (
                settings.kubernetes_tls_server_name
            )
        client.Configuration.set_default(configuration)


def get_core_api() -> client.CoreV1Api:
    load_kubernetes_config()

    return client.CoreV1Api()


def get_apps_api() -> client.AppsV1Api:
    load_kubernetes_config()

    return client.AppsV1Api()

def get_custom_objects_api() -> client.CustomObjectsApi:
    load_kubernetes_config()

    return client.CustomObjectsApi()
