# infra-pilot

A lightweight FastAPI starter for infrastructure automation work.

## Features

- FastAPI application scaffold
- Health endpoint at `/api/v1/health`
- PostgreSQL via Docker Compose
- Environment-based settings

## Run the complete stack with Docker Compose

```bash
docker compose up --build -d
```

This starts both PostgreSQL databases, runs migrations, indexes the runbooks,
starts the FastAPI backend and Next.js dashboard, and launches the simulated
demo request path (`checkout -> inventory + payment`) with a load
generator and Prometheus. InfraPilot components retain the `infra-pilot-*`
names; monitored workload components use `prod-demo-*` names.

The prefixes make the boundary explicit:

- `infra-pilot-*`: the real InfraPilot platform (`backend`, `frontend`,
  `postgres`, and `prometheus`).
- `prod-demo-*`: disposable services that imitate a production workload
  (`checkout`, `inventory`, `payment`, `load-generator`, and their database).

- Dashboard: http://localhost:3000
- InfraPilot API: http://127.0.0.1:8001/docs
- Demo checkout API: http://127.0.0.1:8080/docs
- Demo payment API: http://127.0.0.1:8081/docs
- Demo inventory API: http://127.0.0.1:8082/docs
- Prometheus: http://127.0.0.1:9090
- Kubernetes target: context `kind-prod-demo-cluster`, namespace `prod-demo`.

Stop the complete stack:

```bash
docker compose down
```

Remove the stack and its PostgreSQL data:

```bash
docker compose down -v
```

Optional host-port overrides can be supplied before the command:

```bash
INFRA_WEB_PORT=3002 INFRA_API_PORT=8010 CHECKOUT_PORT=8090 \
  docker compose up --build -d
```

## Run the simulated demo services on kind

Create the dedicated production-like demo cluster once:

```bash
kind create cluster --name prod-demo-cluster
```

Build the same workload images used by Compose and load them into that
cluster:

```bash
docker compose build \
  prod-demo-checkout \
  prod-demo-inventory \
  prod-demo-payment \
  prod-demo-load-generator

kind load docker-image \
  prod-demo/checkout:latest \
  prod-demo/inventory:latest \
  prod-demo/payment:latest \
  prod-demo/load-generator:latest \
  --name prod-demo-cluster

kubectl --context kind-prod-demo-cluster apply \
  -f infrastructure/kubernetes/demo/namespace.yaml
kubectl --context kind-prod-demo-cluster apply \
  -f infrastructure/kubernetes/demo/base
```

If the Prometheus Operator is installed, add the payment ServiceMonitor:

```bash
kubectl --context kind-prod-demo-cluster apply \
  -f infrastructure/kubernetes/demo/payment-service-monitor.yaml
```

Remove the Kubernetes demo workloads together:

```bash
kubectl --context kind-prod-demo-cluster delete \
  -f infrastructure/kubernetes/demo/base
```

Kind clusters cannot be renamed. After the `prod-demo-cluster` is verified
and any monitoring configuration has been recreated, the old demo cluster can
be removed explicitly with `kind delete cluster --name infrapilot`.

## Run directly during development

```bash
uv sync
uv run uvicorn app.main:app --reload
```

## Test

```bash
uv run pytest -q
```
