import os
import time

from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app

app = FastAPI(title="Inventory Service")


DELAY_SECONDS = float(
    os.getenv("DELAY_SECONDS", "0")
)

FAIL_READINESS = (
    os.getenv("FAIL_READINESS", "false").lower()
    == "true"
)


REQUESTS = Counter(
    "inventory_http_requests_total",
    "Inventory HTTP requests",
    ["status"],
)

LATENCY = Histogram(
    "inventory_http_request_duration_seconds",
    "Inventory request latency",
)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ready")
async def ready():
    if FAIL_READINESS:
        raise HTTPException(
            status_code=503,
            detail="inventory service not ready",
        )

    return {"status": "ready"}


@app.post("/reserve")
async def reserve():
    start = time.perf_counter()

    try:
        if DELAY_SECONDS > 0:
            time.sleep(DELAY_SECONDS)

        REQUESTS.labels(
            status="200"
        ).inc()

        return {
            "status": "reserved"
        }

    finally:
        LATENCY.observe(
            time.perf_counter() - start
        )


app.mount(
    "/metrics",
    make_asgi_app(),
)