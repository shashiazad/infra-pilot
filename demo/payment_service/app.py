import random
import time

from fastapi import FastAPI, HTTPException, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
    make_asgi_app,
)


app = FastAPI(
    title="InfraPilot Demo Payment Service"
)


REQUEST_COUNT = Counter(
    "payment_http_requests_total",
    "Total payment HTTP requests",
    ["method", "endpoint", "status"],
)


REQUEST_LATENCY = Histogram(
    "payment_http_request_duration_seconds",
    "Payment HTTP request latency",
    ["method", "endpoint"],
)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy"
    }


@app.post("/payments")
async def create_payment() -> dict:

    start = time.perf_counter()

    try:
        # Intentionally create failures
        # for InfraPilot testing.
        if random.random() < 0.35:

            REQUEST_COUNT.labels(
                method="POST",
                endpoint="/payments",
                status="500",
            ).inc()

            raise HTTPException(
                status_code=500,
                detail="database connection timeout",
            )

        REQUEST_COUNT.labels(
            method="POST",
            endpoint="/payments",
            status="200",
        ).inc()

        return {
            "status": "processed"
        }

    finally:

        REQUEST_LATENCY.labels(
            method="POST",
            endpoint="/payments",
        ).observe(
            time.perf_counter() - start
        )


metrics_app = make_asgi_app()


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


app.mount(
    "/metrics",
    metrics_app,
)
