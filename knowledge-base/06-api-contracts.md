# API Contracts

Base URL in Docker Compose: `http://127.0.0.1:8001/api/v1`.

Interactive OpenAPI documentation: `http://127.0.0.1:8001/docs`.

## Endpoint catalog

| Method | Path | Purpose | Success |
|---|---|---|---|
| GET | `/` | Product name and version | 200 |
| GET | `/api/v1/health` | Application health | 200 |
| GET | `/api/v1/incidents` | List incidents newest first | 200 |
| POST | `/api/v1/incidents` | Create incident | 201 |
| GET | `/api/v1/incidents/{incident_id}` | Get incident | 200 |
| PATCH | `/api/v1/incidents/{incident_id}` | Partially update incident | 200 |
| DELETE | `/api/v1/incidents/{incident_id}` | Delete incident | 204 |
| POST | `/api/v1/incidents/{incident_id}/investigate` | Run and persist investigation | 200 |
| POST | `/api/v1/incidents/{incident_id}/investigate/stream` | Stream graph progress | SSE |
| GET | `/api/v1/incidents/{incident_id}/investigations` | Incident run history | 200 |
| GET | `/api/v1/investigations` | Global investigation feed | 200 |
| GET | `/api/v1/investigations/remediations/audit` | Remediation audit feed | 200 |
| GET | `/api/v1/investigations/{run_id}` | Full investigation report | 200 |
| POST | `/api/v1/investigations/{run_id}/approve` | Approve proposal | 200 |
| POST | `/api/v1/investigations/{run_id}/reject` | Reject proposal | 200 |
| POST | `/api/v1/investigations/{run_id}/execute` | Execute approved proposal | 200 |
| GET | `/api/v1/runbooks` | Indexed runbook catalog | 200 |
| GET | `/api/v1/services` | Kubernetes service inventory | 200 |

## Incident contracts

Create request:

```json
{
  "title": "Payment pods are restarting",
  "description": "Checkout errors increased after payment restarts.",
  "service": "prod-demo-payment",
  "severity": "SEV-2"
}
```

Validation limits: title 3–255 characters, non-empty description, service up to
100 characters, and severity up to 20 characters. Severity and status are not
enforced enums.

Incident response:

```json
{
  "id": "uuid",
  "title": "Payment pods are restarting",
  "description": "Checkout errors increased after payment restarts.",
  "service": "prod-demo-payment",
  "severity": "SEV-2",
  "status": "OPEN",
  "created_at": "date-time",
  "updated_at": "date-time"
}
```

PATCH accepts any subset of title, description, service, severity, and status.

## Investigation result

The synchronous investigation response includes:

- `run_id` and `status`
- classification and investigation plan
- raw evidence list
- structured analysis
- remediation proposal
- approval and remediation states
- tool iteration count

The detail endpoint additionally includes incident ID, persisted runbooks,
historical incidents, remediation result, evidence timestamps, and run timing.

Structured analysis contains:

```json
{
  "summary": "string",
  "confirmed_facts": ["string"],
  "possible_causes": ["string"],
  "recommended_checks": ["string"],
  "confidence": 0.0
}
```

Confidence is constrained to 0–1. Possible causes and recommended checks must
each contain at least one item.

## Remediation contracts

Proposal:

```json
{
  "action": "RESTART_DEPLOYMENT",
  "reason": "string",
  "target_service": "prod-demo-payment",
  "risk": "LOW",
  "commands": ["display-only preview"],
  "requires_approval": true
}
```

Approval responses return run ID, approval status, and remediation status.
Execution adds the remediation result.

State violations return HTTP 409, including execute-before-approval, attempting
to reverse an approval decision, or retrying a failed/running execution.

## Services query

`GET /api/v1/services?namespace=prod-demo` returns one item per Kubernetes
Deployment. The default namespace comes from configuration.

Each item contains deployment replicas, pod readiness/restarts, optional CPU and
memory, optional HTTP metrics, deployment status, Pod details, and recent
warning-event messages. An unavailable Kubernetes inventory returns HTTP 503.

## SSE contract

The stream endpoint emits named server-sent events for graph-node progress. Its
payload currently contains only node identity, not detailed node output. It also
does not persist an investigation run. Use the synchronous endpoint when a
durable report is required.

## Common errors

- 404: incident or investigation does not exist.
- 409: invalid approval or remediation transition.
- 422: request validation failure.
- 429: Groq rate limit on synchronous investigation.
- 503: Kubernetes inventory unavailable.
- 500: unhandled provider, database, graph, or infrastructure failure.

## Authentication

No endpoint currently requires authentication or authorization. CORS is limited
to local port 3000 origins, but CORS is not an access-control mechanism.
