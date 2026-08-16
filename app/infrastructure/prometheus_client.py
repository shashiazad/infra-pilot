from typing import Any

import httpx

from app.core.config import settings


async def query_prometheus(
    query: str,
) -> float | None:

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.prometheus_url}/api/v1/query",
            params={
                "query": query,
            },
            timeout=10,
        )

        response.raise_for_status()

        payload: dict[str, Any] = (
            response.json()
        )

    results = (
        payload
        .get("data", {})
        .get("result", [])
    )

    if not results:
        return None

    value = results[0].get("value")

    if not value or len(value) < 2:
        return None

    try:
        return float(value[1])

    except (
        TypeError,
        ValueError,
    ):
        return None
