# infra-pilot

A lightweight FastAPI starter for infrastructure automation work.

## Features

- FastAPI application scaffold
- Health endpoint at `/api/v1/health`
- PostgreSQL via Docker Compose
- Environment-based settings

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload
```

## Run database

```bash
docker compose up -d
```

## Test

```bash
uv run pytest -q
```
