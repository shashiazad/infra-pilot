import os
import time

import httpx

CHECKOUT_URL = os.getenv(
    "CHECKOUT_URL",
    "http://prod-demo-checkout:8080",
)

INTERVAL = float(
    os.getenv(
        "REQUEST_INTERVAL_SECONDS",
        "2",
    )
)


while True:
    try:
        response = httpx.post(
            f"{CHECKOUT_URL}/checkout",
            timeout=10,
        )

        print(
            "checkout",
            response.status_code,
            response.text,
            flush=True,
        )

    except Exception as exc:
        print(
            f"ERROR request failed: {exc}",
            flush=True,
        )

    time.sleep(INTERVAL)
