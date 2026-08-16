from pydantic import BaseModel, Field


class PodSnapshot(BaseModel):
    name: str
    phase: str
    ready: bool
    restarts: int
    cpu: str | None = None
    memory: str | None = None


class ServiceSnapshot(BaseModel):
    service: str
    namespace: str
    health: str
    desired_replicas: int
    ready_replicas: int
    available_replicas: int
    restarts: int
    cpu: str | None = None
    memory: str | None = None
    http_5xx_rate_percent: float | None = None
    p95_latency_ms: float | None = None
    deployment_status: str
    pods: list[PodSnapshot] = Field(default_factory=list)
    recent_warnings: list[str] = Field(default_factory=list)
