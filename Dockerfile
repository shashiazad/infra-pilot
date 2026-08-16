FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
COPY scripts ./scripts
COPY runbooks ./runbooks

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m scripts.ingest_runbooks && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
