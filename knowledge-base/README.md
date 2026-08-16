# InfraPilot Knowledge Base

This directory is the technical source of truth for InfraPilot's current
implementation. It is intended for maintainers, reviewers, interviewers, and
operators who need to understand the system without reconstructing it from the
source tree.

Last verified against the repository: **2026-08-17**.

## Reading paths

For an architectural overview, read:

1. [Product and scope](01-product-and-scope.md)
2. [High-level design](02-high-level-design.md)
3. [Investigation engine](04-investigation-engine.md)
4. [Security and remediation](10-security-and-remediation.md)

For implementation work, continue with:

1. [Low-level design](03-low-level-design.md)
2. [Data model and RAG](05-data-model-and-rag.md)
3. [API contracts](06-api-contracts.md)
4. [Frontend design](07-frontend-design.md)
5. [Development and testing](11-development-and-testing.md)

For operations, use:

1. [Observability and demo environment](08-observability-and-demo.md)
2. [Deployment and operations](09-deployment-and-operations.md)
3. [Current limitations and roadmap](12-current-limitations-and-roadmap.md)

## Document index

- [01 — Product and scope](01-product-and-scope.md): problem, users, use cases,
  capabilities, and boundaries.
- [02 — High-level design](02-high-level-design.md): components, trust
  boundaries, runtime topology, and main data flows.
- [03 — Low-level design](03-low-level-design.md): backend modules, classes,
  dependencies, state machines, and implementation rules.
- [04 — Investigation engine](04-investigation-engine.md): LangGraph workflow,
  MCP tools, evidence handling, model calls, and persistence.
- [05 — Data model and RAG](05-data-model-and-rag.md): PostgreSQL schema,
  pgvector retrieval, runbook ingestion, and historical memory.
- [06 — API contracts](06-api-contracts.md): HTTP endpoints, payloads, status
  codes, SSE events, and state transitions.
- [07 — Frontend design](07-frontend-design.md): routes, rendering model, API
  client, user flows, and component responsibilities.
- [08 — Observability and demo](08-observability-and-demo.md): demo services,
  metrics, Kubernetes inventory, traffic generation, and failure injection.
- [09 — Deployment and operations](09-deployment-and-operations.md): Compose,
  Kind, startup ordering, configuration, and lifecycle commands.
- [10 — Security and remediation](10-security-and-remediation.md): human
  approval, allow-listing, trust boundaries, secrets, and production gaps.
- [11 — Development and testing](11-development-and-testing.md): repository
  layout, local development, migrations, tests, and change recipes.
- [12 — Current limitations and roadmap](12-current-limitations-and-roadmap.md):
  explicit implementation constraints and prioritized improvements.

## Documentation principles

- Implemented behavior is separated from recommendations.
- Runbooks and historical incidents guide analysis but do not prove a cause.
- Compose runs the local product; the Services page lists Kubernetes objects.
- Generated commands are display-only. Server-side code authorizes execution.

For command-by-command setup, see the repository [README](../README.md).
