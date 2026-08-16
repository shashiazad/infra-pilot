# Current Limitations and Roadmap

This document distinguishes verified implementation constraints from future
improvements. It is not a promise of delivery order.

## Highest-priority correctness work

### Persist streamed investigations

The SSE endpoint runs the graph and emits node names but does not create an
investigation row, save evidence, mark failure, or return the final result.
Unify synchronous and streaming execution around one persisted run lifecycle.

### Make application metrics service-aware

The MCP application-metrics tool and inventory enrichment use payment metric
names. Add a metrics registry per service or a normalized HTTP metric contract,
and include a job/service filter in every PromQL expression.

### Improve evidence accumulation

`collect_tool_evidence` rescans every ToolMessage on each cycle. Use a state
reducer or append only newly executed results, with stable evidence IDs to avoid
duplicates and preserve call arguments.

### Improve historical relevance

Historical memory is simply the five most recent completed runs from other
incidents. Filter by service/classification or embed incident summaries for
semantic retrieval.

## Reliability and scale

- Move investigation execution to a durable worker and job queue.
- Add graph checkpoints, cancellation, timeouts, retry policy, and recovery.
- Reuse MCP connections instead of starting a subprocess/session for each call.
- Add database connection-pool and provider timeout configuration.
- Add idempotency keys for create and investigate operations.
- Define retry semantics for failed remediation.
- Add pagination to incidents, investigations, evidence, runbooks, and audit.
- Add health/readiness checks for Groq, database, Kubernetes, and Prometheus.

## RAG quality

- Split long documents into meaningful chunks rather than one file per vector.
- Persist chunk order, document checksum, embedding-model version, and metadata.
- Perform incremental ingestion rather than delete-and-rebuild.
- Return distance/score and enforce a relevance threshold.
- Add citations from analysis statements to retrieved runbook chunks.
- Evaluate retrieval quality with a fixed incident/runbook benchmark.

## API and domain contracts

- Replace free-form severity, status, category, priority, risk, and action strings
  with enums.
- Version stored JSON payloads and validate them when reading.
- Add endpoint pagination, sorting, and filters.
- Add incident status transitions when investigation starts/completes.
- Return detailed execution error classes rather than free-form strings.
- Add an explicit investigation cancel endpoint.

## Frontend work

- Consume durable SSE or job status for live investigation progress.
- Connect environment/namespace selectors to API state.
- Implement search and filtering.
- Replace static sidebar health labels with real probes.
- Add incident editing and resolution controls.
- Render a true node execution trace rather than positional plan/evidence pairs.
- Add accessible confirmation and reason capture for approval/execution.
- Add component, integration, and browser tests.

## Observability work

- Expose InfraPilot API, graph, model, tool, and remediation metrics.
- Add structured logging and request/run correlation IDs.
- Add OpenTelemetry tracing across API, graph, MCP, Kubernetes, and Groq.
- Add Alertmanager or webhook ingestion for automatic incident creation.
- Deploy one Prometheus architecture for the actual monitored Kubernetes target.
- Add recording/alert rules and telemetry retention guidance.

## Kubernetes and deployment work

- Deploy InfraPilot itself to Kubernetes for a production-like topology.
- Replace demo plaintext credentials with Secrets.
- Add resource requests/limits, liveness probes, security contexts, and network
  policies.
- Add a PersistentVolumeClaim for demo PostgreSQL where persistence is desired.
- Use immutable image tags instead of `latest`.
- Add Helm or Kustomize overlays for local and production environments.
- Add CI image builds, vulnerability scanning, manifest validation, and smoke
  tests.

## Security work

See [Security and remediation](10-security-and-remediation.md). Authentication,
RBAC, actor audit, least-privilege Kubernetes credentials, target allow-listing,
secret management, redaction, and prompt-injection hardening are required before
production use.

## Deliberately retained demo behavior

- Separate `infra-pilot-*` and `prod-demo-*` names make failures unambiguous.
- The broken payment manifest intentionally creates restart/log evidence.
- Local `--kubelet-insecure-tls` is limited to the disposable Kind cluster.
- The load generator continuously exercises the checkout path.

These behaviors support demonstrations and incident exercises; they should not
be copied unchanged into a production environment.
