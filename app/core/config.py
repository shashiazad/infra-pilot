from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InfraPilot"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str

    groq_api_key: str
    llm_model: str = "openai/gpt-oss-120b"
    llm_fallback_model: str = "openai/gpt-oss-20b"
    llm_structured_model: str = "openai/gpt-oss-120b"
    llm_structured_fallback_model: str = "openai/gpt-oss-20b"

    prometheus_url: str = "http://localhost:9090"
    kubernetes_context: str = "kind-prod-demo-cluster"
    kubernetes_namespace: str = "prod-demo"
    kubernetes_host_alias: str | None = None
    kubernetes_tls_server_name: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
