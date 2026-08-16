import os
import time

import httpx
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app

app = FastAPI(title="Checkout Service")


PAYMENT_URL = os.getenv(
    "PAYMENT_URL",
    "http://prod-demo-payment:8080",
)

INVENTORY_URL = os.getenv(
    "INVENTORY_URL",
    "http://prod-demo-inventory:8080",
)


REQUESTS = Counter(
    "checkout_http_requests_total",
    "Checkout HTTP requests",
    ["status"],
)

LATENCY = Histogram(
    "checkout_http_request_duration_seconds",
    "Checkout request latency",
)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ready")
async def ready():
    return {"status": "ready"}


@app.post("/checkout")
async def checkout():
    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(
            timeout=5
        ) as client:

            inventory_response = await client.post(
                f"{INVENTORY_URL}/reserve"
            )

            if inventory_response.status_code >= 400:
                raise RuntimeError(
                    "inventory reservation failed"
                )

            payment_response = await client.post(
                f"{PAYMENT_URL}/payments"
            )

            if payment_response.status_code >= 400:
                raise RuntimeError(
                    "payment processing failed"
                )

        REQUESTS.labels(
            status="200"
        ).inc()

        return {
            "status": "completed"
        }

    except Exception as exc:
        print(
            f"ERROR checkout failed: {exc}",
            flush=True,
        )

        REQUESTS.labels(
            status="500"
        ).inc()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    finally:
        LATENCY.observe(
            time.perf_counter() - start
        )


app.mount(
    "/metrics",
    make_asgi_app(),
)
