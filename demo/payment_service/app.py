import os
import time

import psycopg
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app

app = FastAPI(title="Payment Service")


DB_HOST = os.getenv("DB_HOST", "prod-demo-postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "payments")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


REQUESTS = Counter(
    "payment_http_requests_total",
    "Payment HTTP requests",
    ["status"],
)

LATENCY = Histogram(
    "payment_http_request_duration_seconds",
    "Payment request latency",
)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ready")
async def ready():
    try:
        with psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=2,
        ):
            pass

        return {"status": "ready"}

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"database unavailable: {exc}",
        ) from exc


@app.post("/payments")
async def payment():
    start = time.perf_counter()

    try:
        with psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=2,
        ) as conn:

            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")

        REQUESTS.labels(status="200").inc()

        return {
            "status": "processed",
        }

    except Exception as exc:
        print(
            f"ERROR database connection failure: {exc}",
            flush=True,
        )

        REQUESTS.labels(status="500").inc()

        raise HTTPException(
            status_code=500,
            detail="database connection failure",
        ) from exc

    finally:
        LATENCY.observe(
            time.perf_counter() - start
        )


app.mount(
    "/metrics",
    make_asgi_app(),
)
