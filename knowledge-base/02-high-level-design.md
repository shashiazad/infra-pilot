# High-Level Design

## System context

InfraPilot is a control plane around a monitored Kubernetes workload. It owns
incidents, investigations, knowledge retrieval, and approval state. Kubernetes
and Prometheus remain the sources of live operational evidence.

```mermaid
flowchart LR
    Operator["Operator"] --> UI["Next.js dashboard"]
    UI -->|"REST"| API["FastAPI control plane"]
    API --> DB[("PostgreSQL + pgvector")]
    API --> Agent["LangGraph investigation engine"]
    Agent --> LLM["Groq LLM API"]
    Agent --> MCP["Infrastructure MCP server"]
    Agent --> DB
    MCP --> K8s["Kind Kubernetes API"]
    MCP --> Prom["Prometheus query API"]
    K8s --> Metrics["Metrics Server"]
    K8s --> Demo["prod-demo workloads"]
    Prom -->|"scrape /metrics"| Demo
```

## Runtime topology

```mermaid
flowchart TB
    User["Browser"]

    subgraph Compose["Docker Compose: infra-pilot"]
        Frontend["infra-pilot-frontend\nNext.js :3000"]
        Backend["infra-pilot-backend\nFastAPI :8000"]
        PlatformDB[("infra-pilot-postgres\nPostgreSQL + pgvector")]
        Prometheus["infra-pilot-prometheus\nPrometheus :9090"]
        CLoad["prod-demo-load-generator"]
        CCheckout["prod-demo-checkout"]
        CInventory["prod-demo-inventory"]
        CPayment["prod-demo-payment"]
        CDB[("prod-demo-postgres")]

        Frontend --> Backend
        Backend --> PlatformDB
        Backend --> Prometheus
        CLoad --> CCheckout
        CCheckout --> CInventory
        CCheckout --> CPayment
        CPayment --> CDB
        Prometheus --> CCheckout
        Prometheus --> CInventory
        Prometheus --> CPayment
    end

    subgraph Kind["Kind: prod-demo-cluster / namespace prod-demo"]
        KubeAPI["Kubernetes API"]
        MetricsServer["Metrics Server"]
        KLoad["prod-demo-load-generator"]
        KCheckout["prod-demo-checkout"]
        KInventory["prod-demo-inventory"]
        KPayment["prod-demo-payment"]
        KDB[("prod-demo-postgres")]

        KLoad --> KCheckout
        KCheckout --> KInventory
        KCheckout --> KPayment
        KPayment --> KDB
        MetricsServer --> KubeAPI
    end

    User -->|"localhost:3000"| Frontend
    User -->|"localhost:8001"| Backend
    Backend -->|"mounted kubeconfig via host.docker.internal"| KubeAPI
```

## Hybrid-runtime behavior

The local design has two representations of the demo workload:

1. Compose services generate traffic and expose application metrics to the
   Compose Prometheus server.
2. Kind Deployments provide pods, events, logs, deployment health, and resource
   metrics to the Kubernetes inventory and MCP tools.

The Services API merges those sources by service name. Kubernetes supplies the
inventory; Prometheus enriches `prod-demo-payment` with 5xx and p95 values. This
is useful locally but is not a single-cluster production monitoring design.

## Investigation flow

```mermaid
sequenceDiagram
    actor Operator
    participant UI as Next.js
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Graph as LangGraph
    participant LLM as Groq
    participant MCP as MCP tools
    participant Infra as Kubernetes and Prometheus

    Operator->>UI: Run investigation
    UI->>API: POST /incidents/{id}/investigate
    API->>DB: Create RUNNING run
    API->>Graph: Invoke graph
    Graph->>LLM: Classify
    Graph->>DB: Retrieve runbooks and history
    loop At most five tool iterations
        Graph->>LLM: Select evidence tools
        LLM-->>Graph: Tool calls
        Graph->>MCP: Execute read-only tool
        MCP->>Infra: Query live state
        Infra-->>Graph: Structured evidence
    end
    Graph->>LLM: Analyze evidence
    Graph->>LLM: Propose remediation
    Graph-->>API: Final state
    API->>DB: Persist evidence and completed run
    API-->>UI: Investigation report
```

## Remediation flow

```mermaid
sequenceDiagram
    actor Operator
    participant UI as Next.js
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Executor as Allow-listed executor
    participant K8s as Kubernetes API

    Operator->>UI: Approve proposal
    UI->>API: POST /investigations/{run}/approve
    API->>DB: Lock row and set APPROVED
    Operator->>UI: Execute action
    UI->>API: POST /investigations/{run}/execute
    API->>DB: Set RUNNING
    API->>Executor: Validate action
    alt RESTART_DEPLOYMENT
        Executor->>K8s: Patch pod-template annotation
        API->>DB: Set COMPLETED and result
    else Not allow-listed
        API->>DB: Set FAILED and error
    end
    API-->>UI: Auditable result
```

## External dependencies

- Groq models through `langchain-groq`.
- Kubernetes through the official Python client.
- Prometheus HTTP query API.
- MCP over a local stdio subprocess.
- Sentence Transformers for local embeddings.
- PostgreSQL with pgvector.

## Availability model

Investigations run inside the API process. A synchronous investigation occupies
one HTTP request until completion. There is no queue, worker service, scheduler,
or durable graph checkpoint. PostgreSQL becomes authoritative after state is
persisted.
