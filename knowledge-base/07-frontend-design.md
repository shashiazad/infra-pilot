# Frontend Design

## Technology and rendering model

The dashboard uses Next.js App Router, React, and TypeScript. The root layout
wraps every page in a persistent client-side `AppShell`. Most pages are async
Server Components that fetch current API data with `cache: "no-store"`.

Interactive actions use Client Components:

- `CreateIncidentButton`
- `RunInvestigationButton`
- `RemediationActions`

## API routing

`frontend/src/lib/api.ts` chooses the base URL by execution environment:

- Server-side rendering uses `API_INTERNAL_URL`, which resolves to
  `http://infra-pilot-backend:8000/api/v1` in Compose.
- Browser requests use build-time `NEXT_PUBLIC_API_URL`, normally
  `http://127.0.0.1:8001/api/v1`.
- Local fallbacks use port 8000.

`apiGet` disables caching. `apiPost` sends JSON only when a body exists. Both
parse FastAPI's `detail` field before falling back to response text.

## Route map

| Route | Responsibility | Main API calls |
|---|---|---|
| `/` | Redirect to overview | None |
| `/overview` | Operational summary | incidents, services, investigations, audit |
| `/incidents` | Incident queue and creation | incidents GET/POST |
| `/incidents/[id]` | Incident detail and run history | incident, history, latest run |
| `/investigations` | Global run list | investigations |
| `/investigations/[runId]` | Evidence report and remediation controls | investigation detail, approve/reject/execute |
| `/services` | Kubernetes inventory | services for `prod-demo` |
| `/runbooks` | Indexed knowledge catalog | runbooks |
| `/remediations` | Global remediation audit | remediation audit |
| `/settings` | Informational local configuration view | None |

## User flows

### Incident creation

The modal collects title, service, severity, and description, posts the record,
then navigates to the new incident detail page. Client validation mirrors the
main backend length constraints.

### Investigation

The incident detail button calls the synchronous investigation endpoint. While
the request is active it shows a busy state. Success redirects directly to the
persisted investigation report.

The current UI does not consume the SSE investigation endpoint.

### Investigation review

The report separates:

- summary and confidence
- confirmed facts
- possible causes
- recommended checks
- raw evidence
- plan/timeline
- retrieved runbooks
- historical run memory
- remediation proposal and result

Raw tool payloads remain accessible in expandable JSON inspectors.

### Remediation

Buttons are enabled from current state:

- approve and reject only when approval is `PENDING`
- execute only when approval is `APPROVED` and remediation is `NOT_STARTED`

Backend state validation remains authoritative; UI gating is convenience only.

## Shared components

- `AppShell`: navigation, environment/namespace selectors, search field, and
  status strip.
- `IncidentTable`: severity, incident, service, status, and relative times.
- `StatusBadge` and `SeverityBadge`: visual state mapping.
- `MetricCard`: dashboard counters.
- `EvidencePanel`: summary plus raw payload.
- `Timeline`: maps plan steps to evidence by list position.

## Error behavior

Pages surface backend errors instead of fabricating data. Overview requires the
incident endpoint and treats services, runs, and remediations as optional.
Feature pages show an empty state with the failing endpoint or diagnostic hint.

## Current UI limitations

- Environment and namespace selectors are display-only.
- Search is display-only.
- Sidebar health indicators are static labels, not live probes.
- Settings is informational and does not persist configuration.
- The timeline pairs plan steps and evidence by index; this is not a true graph
  execution trace.
- Investigation execution uses a long synchronous request rather than SSE or a
  background job.
- There is no authentication or role-aware approval UI.
