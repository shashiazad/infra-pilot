# Product and Scope

## Purpose

InfraPilot helps an operator move from an infrastructure incident report to an
evidence-backed diagnosis and a controlled remediation decision. It combines
incident tracking, Kubernetes evidence, Prometheus metrics, operational
runbooks, historical investigation memory, and an LLM-driven investigation
workflow.

The current project is a local, portfolio-grade platform and demonstration
environment. It is not yet a multi-tenant production incident-management
service.

## Primary users

- Platform and site-reliability engineers investigating Kubernetes failures.
- Application engineers reviewing correlated infrastructure evidence.
- Reviewers learning how an agent can use operational tools safely.
- Developers extending agent workflows, retrieval, and remediation controls.

## Core use cases

### Incident management

Create, list, inspect, update, and delete incidents. Each incident has a title,
description, affected service, severity, status, and timestamps.

### Agentic investigation

Classify an incident, generate a plan, retrieve runbooks and historical context,
collect live evidence through read-only tools, analyze that evidence, and create
one remediation proposal.

### Evidence and audit review

Persist classification, plan, raw tool findings, analysis, confidence,
retrieved knowledge, historical context, approval state, and execution result.

### Human-controlled remediation

Require explicit approval, then execute only a server-side allow-listed action.
Generated command strings are never passed to a shell. The only implemented
action is `RESTART_DEPLOYMENT`.

### Infrastructure inventory

Display Kubernetes Deployment and Pod health from `prod-demo`. Enrich resource
usage from Metrics Server and payment HTTP signals from Prometheus.

### Operational knowledge

Embed Markdown runbooks with `all-MiniLM-L6-v2`, store 384-dimensional vectors
in pgvector, and retrieve the nearest guidance during investigations.

## Implemented capabilities

- FastAPI REST API and OpenAPI schema.
- Next.js operations dashboard.
- PostgreSQL persistence and Alembic migrations.
- LangGraph investigation orchestration.
- Groq-hosted primary and fallback models.
- Pydantic-constrained structured model outputs.
- MCP server for Kubernetes and Prometheus evidence tools.
- Runbook RAG and recent-investigation memory.
- Remediation audit, human approval, and allow-listed execution.
- Docker Compose product stack and separate Kind demo environment.
- Synthetic checkout, inventory, payment, database, and traffic services.

## Naming boundary

- `infra-pilot-*`: real InfraPilot application components.
- `prod-demo-*`: simulated production workloads.
- Kind cluster: `prod-demo-cluster`.
- kubeconfig context: `kind-prod-demo-cluster`.
- Kubernetes namespace: `prod-demo`.

## Current non-goals

- Autonomous remediation without approval.
- Arbitrary shell command execution or destructive actions.
- Multi-user authentication, authorization, or tenant isolation.
- Alert-manager ingestion or automatic incident creation.
- Distributed background workers or queued investigations.
- Production-grade secret management.
- Docker container inventory on the Kubernetes Services page.
- Semantic similarity search across historical incidents.

See [Current limitations and roadmap](12-current-limitations-and-roadmap.md) for
the engineering implications.
