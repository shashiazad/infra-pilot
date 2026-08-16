# Development and Testing

## Repository map

```text
app/
  agents/investigation/   LangGraph state, nodes, routing, graph
  api/v1/                 FastAPI routers
  core/                   Settings
  db/                     Async session and SQLAlchemy models
  infrastructure/         Kubernetes and Prometheus clients
  llm/                    Groq model construction and prompts
  mcp/                    MCP client adapter, tools, and server
  rag/                    Embeddings and retrieval
  remediation/            Allow-listed executor
  repositories/           Database access
  schemas/                Pydantic API and model-output contracts
  services/               Use-case orchestration
demo/                     Synthetic workload source and Dockerfiles
frontend/                 Next.js dashboard
infrastructure/           Kubernetes and Prometheus configuration
migrations/               Alembic history
runbooks/                 Markdown operational guidance
scripts/                  Ingestion and manual integration probes
tests/                    Automated backend tests
knowledge-base/           Technical documentation
```

## Backend development

Install dependencies:

```bash
uv sync
```

With local dependencies available, apply migrations and ingest runbooks:

```bash
uv run alembic upgrade head
uv run python -m scripts.ingest_runbooks
```

Start the API:

```bash
uv run uvicorn app.main:app --reload
```

The local `.env` must contain database and Groq settings. Direct local execution
normally uses API port 8000; Compose publishes container port 8000 as host 8001.

## Frontend development

```bash
cd frontend
npm ci
npm run dev
```

Set `NEXT_PUBLIC_API_URL` to the browser-accessible backend base URL and
`API_INTERNAL_URL` when server-side rendering needs a different internal URL.

The installed Next.js version has repository-local guidance in
`frontend/AGENTS.md`; read the relevant docs from `frontend/node_modules/next`
before changing framework behavior.

## Database changes

1. Update SQLAlchemy models.
2. Generate or write an Alembic revision.
3. Review upgrade and downgrade operations.
4. Run `uv run alembic upgrade head` against a disposable database.
5. Update schemas, repositories, services, API contracts, and this knowledge
   base when the domain contract changes.

The backend container applies all migrations automatically at startup.

## Runbook changes

Add or edit Markdown under `runbooks/`, then run:

```bash
uv run python -m scripts.ingest_runbooks
```

Ingestion replaces the full runbook index. A production implementation should
use stable document IDs and incremental updates.

## Automated checks

```bash
uv run ruff check app demo scripts tests
uv run pytest -q

cd frontend
npm run lint
npm run build
```

Validate deployment configuration:

```bash
docker compose config --quiet

kubectl --context kind-prod-demo-cluster apply --dry-run=client \
  -f infrastructure/kubernetes/demo/namespace.yaml \
  -f infrastructure/kubernetes/demo/base
```

## Current automated test coverage

- Health endpoint response.
- Historical-context node behavior.
- Enforcement of `requires_approval=true`.
- Execute-before-approval denial.
- Rejected-to-approved transition denial.
- Completed-execution idempotency.
- Rejection of non-allow-listed actions.
- Kubernetes restart patch arguments and namespace.

## Important missing tests

- Incident CRUD and validation integration tests.
- Full investigation graph with deterministic fake models/tools.
- MCP transport and every tool's success/failure behavior.
- Runbook ingestion and pgvector retrieval.
- Service inventory joins and Prometheus enrichment.
- SSE semantics and disconnect handling.
- Database concurrency for approval/execution.
- Frontend component and browser end-to-end tests.
- Compose and Kind smoke tests in CI.

## Change recipes

### Add a read-only infrastructure tool

1. Define it with `@mcp.tool()` in the infrastructure server.
2. Accept `service` and `namespace` so the LangChain adapter can wrap it.
3. Return structured, bounded evidence and convert expected API errors to data.
4. Make no mutations from investigation tools.
5. Add tests and document evidence semantics.

### Add a runbook

1. Add focused Markdown under `runbooks/`.
2. Separate symptoms, checks, and causes.
3. Avoid claims that could be mistaken for current evidence.
4. Re-index and verify the catalog/retrieval.

### Add a frontend API view

1. Add or confirm a typed backend response schema.
2. Add the TypeScript interface.
3. Use `apiGet` for server-rendered live data or `apiPost` in a Client Component.
4. Provide explicit loading/error/empty behavior.
5. Run lint and the production build.

### Change service naming

Update Compose service/DNS names, demo defaults, Prometheus jobs, Kubernetes
resources and labels, backend PromQL matching, frontend examples, tests, root
README, and this knowledge base together.
