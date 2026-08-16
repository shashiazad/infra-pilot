import Link from "next/link";
import { RemediationActions } from "@/components/remediation-actions";
import {
  EvidencePanel,
  StatusBadge,
  Timeline,
  relativeTime,
} from "@/components/operations-ui";
import { RunInvestigationButton } from "@/components/run-investigation-button";
import { apiGet } from "@/lib/api";
import type { Investigation } from "@/types";
function AnalysisList({ items, type }: { items: string[]; type?: string }) {
  return items.length ? (
    <ul className={`analysis-list ${type ?? ""}`}>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  ) : (
    <span className="panel-subtitle">No items reported.</span>
  );
}
export default async function InvestigationPage({
  params,
}: {
  params: Promise<{
    runId: string;
  }>;
}) {
  const { runId } = await params;
  let data: Investigation;
  try {
    data = await apiGet<Investigation>(`/investigations/${runId}`);
  } catch {
    return (
      <main className="page">
        <div className="empty-state">
          <strong>Investigation unavailable</strong>
          <p>Confirm the backend is running and the run ID is valid.</p>
          <Link className="text-link" href="/incidents">
            Return to incidents
          </Link>
        </div>
      </main>
    );
  }
  const analysis = data.analysis;
  const classification = data.classification ?? {};
  const confidence = analysis?.confidence ?? 0;
  return (
    <main className="page">
      <Link href={`/incidents/${data.incident_id}`} className="back-link">
        ← Incident detail
      </Link>
      <header className="incident-header">
        <div className="incident-header-top">
          <div>
            <div className="badge-row">
              <StatusBadge value={data.status} />
              <span className="badge badge-info">
                {String(classification.category ?? "Unclassified")}
              </span>
              <span className="badge badge-muted">
                Priority {String(classification.priority ?? "—")}
              </span>
            </div>
            <h1>Infrastructure investigation</h1>
            <p className="mono">Run {data.run_id}</p>
          </div>
          <div className="action-stack">
            <div className="badge-row">
              <span className="badge badge-muted">
                {data.tool_iterations} tool calls
              </span>
              <span className="badge badge-success">
                {Math.round(confidence * 100)}% confidence
              </span>
            </div>
            {data.status.toUpperCase() === "FAILED" && (
              <RunInvestigationButton incidentId={data.incident_id} rerun />
            )}
          </div>
        </div>
        <div className="meta-grid">
          <div className="meta-item">
            <span>INCIDENT</span>
            <strong className="mono">{data.incident_id}</strong>
          </div>
          <div className="meta-item">
            <span>STARTED</span>
            <strong>
              {data.started_at ? relativeTime(data.started_at) : "—"}
            </strong>
          </div>
          <div className="meta-item">
            <span>COMPLETED</span>
            <strong>
              {data.completed_at
                ? new Date(data.completed_at).toLocaleString()
                : "In progress"}
            </strong>
          </div>
          <div className="meta-item">
            <span>APPROVAL</span>
            <strong>{data.approval_status ?? "Not proposed"}</strong>
          </div>
        </div>
      </header>
      <nav className="tabs" aria-label="Investigation sections">
        <a className="tab tab-active" href="#overview">
          Overview
        </a>
        <a className="tab" href="#evidence">
          Evidence
        </a>
        <a className="tab" href="#timeline">
          Agent timeline
        </a>
        <a className="tab" href="#runbooks">
          Runbooks
        </a>
        <a className="tab" href="#history">
          History
        </a>
        <a className="tab" href="#remediation">
          Remediation
        </a>
      </nav>
      <div className="investigation-grid" id="overview">
        <div className="stack">
          <section className="panel">
            <div className="panel-header">
              <h2>Root-cause assessment</h2>
              <span className="panel-subtitle">Evidence-level reasoning</span>
            </div>
            <div className="panel-body">
              <p className="summary-text">
                {analysis?.summary ?? "Analysis has not completed."}
              </p>
            </div>
          </section>
          <section className="panel">
            <div className="panel-header">
              <h3>Confirmed facts</h3>
              <span className="panel-subtitle">
                Directly supported by evidence
              </span>
            </div>
            <div className="panel-body">
              <AnalysisList
                items={analysis?.confirmed_facts ?? []}
                type="confirmed"
              />
            </div>
          </section>
          <section className="panel">
            <div className="panel-header">
              <h3>Ranked possible causes</h3>
              <span className="panel-subtitle">
                Hypotheses, not confirmed facts
              </span>
            </div>
            <div className="panel-body">
              <AnalysisList
                items={analysis?.possible_causes ?? []}
                type="causes"
              />
            </div>
          </section>
          <section className="panel">
            <div className="panel-header">
              <h3>Recommended checks</h3>
            </div>
            <div className="panel-body">
              <AnalysisList items={analysis?.recommended_checks ?? []} />
            </div>
          </section>
        </div>
        <aside className="sticky-column stack">
          <section className="panel">
            <div className="panel-header">
              <h2>Investigation summary</h2>
              <StatusBadge value={data.status} />
            </div>
            <div className="panel-body">
              <p className="summary-text">
                {analysis?.summary ??
                  "The agent is still collecting infrastructure evidence."}
              </p>
              <div className="confidence">
                <span className="metric-label">Confidence</span>
                <strong>
                  {Math.round(confidence * 100)}%{" "}
                  {confidence >= 0.8
                    ? "High"
                    : confidence >= 0.5
                      ? "Medium"
                      : "Low"}
                </strong>
              </div>
            </div>
          </section>
          <section className="panel" id="timeline">
            <div className="panel-header">
              <h2>Execution trace</h2>
            </div>
            <Timeline
              steps={data.investigation_plan ?? []}
              evidence={data.evidence}
            />
          </section>
        </aside>
      </div>
      <section className="panel section-space" id="evidence">
        <div className="panel-header">
          <h2>Live infrastructure evidence</h2>
          <span className="panel-subtitle">
            {data.evidence.length} findings · raw payloads preserved
          </span>
        </div>
        <div className="panel-body evidence-list">
          {data.evidence.length ? (
            data.evidence.map((item, index) => (
              <EvidencePanel item={item} key={`${item.tool}-${index}`} />
            ))
          ) : (
            <div className="empty-state">
              <strong>No evidence collected</strong>
            </div>
          )}
        </div>
      </section>
      <div className="dashboard-grid section-space">
        <section className="panel" id="runbooks">
          <div className="panel-header">
            <h2>Operational runbooks</h2>
            <span className="badge badge-muted">
              Guidance · {data.runbooks.length}
            </span>
          </div>
          {data.runbooks.length ? (
            <div className="panel-body evidence-list">
              {data.runbooks.map((book, index) => (
                <article
                  className="evidence-panel"
                  key={`${book.source ?? book.title}-${index}`}
                >
                  <div className="evidence-head">
                    <span className="tool-name">
                      {book.title ?? "Retrieved runbook"}
                    </span>
                    <span className="badge badge-success">Retrieved</span>
                  </div>
                  <div className="evidence-summary">
                    {book.source ?? "Operational knowledge index"}
                  </div>
                  {book.content && (
                    <details className="json-inspector">
                      <summary>View guidance</summary>
                      <pre>{book.content}</pre>
                    </details>
                  )}
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <strong>No runbook matches recorded</strong>
              <p>
                Older runs predate context persistence; new investigations store
                retrieved guidance.
              </p>
            </div>
          )}
        </section>
        <section className="panel" id="history">
          <div className="panel-header">
            <h2>Historical incident memory</h2>
            <span className="panel-subtitle">
              {data.historical_incidents.length} related runs
            </span>
          </div>
          {data.historical_incidents.length ? (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Run</th>
                    <th>Classification</th>
                    <th>Iterations</th>
                  </tr>
                </thead>
                <tbody>
                  {data.historical_incidents.map((item, index) => (
                    <tr key={`${item.run_id}-${index}`}>
                      <td>
                        <Link
                          className="text-link mono"
                          href={`/investigations/${item.run_id}`}
                        >
                          {item.run_id?.slice(0, 8) ?? "Unknown"}
                        </Link>
                      </td>
                      <td>{String(item.classification?.category ?? "—")}</td>
                      <td>{item.tool_iterations ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <strong>No related historical runs</strong>
              <p>This may be the first investigation in memory.</p>
            </div>
          )}
        </section>
      </div>
      {data.remediation_proposal && (
        <section
          className="panel remediation-panel section-space"
          id="remediation"
        >
          <div className="panel-header">
            <h2>Controlled remediation</h2>
            <span className="badge badge-warning">
              {data.remediation_proposal.risk} risk · approval required
            </span>
          </div>
          <div className="proposal-grid">
            <div className="proposal-item">
              <span>ACTION</span>
              <strong>
                {data.remediation_proposal.action.replaceAll("_", " ")}
              </strong>
            </div>
            <div className="proposal-item">
              <span>TARGET</span>
              <strong>{data.remediation_proposal.target_service}</strong>
            </div>
          </div>
          <p className="proposal-reason">{data.remediation_proposal.reason}</p>
          {data.remediation_proposal.commands.length > 0 && (
            <div className="command-preview">
              <span>PROPOSED COMMAND — DISPLAY ONLY</span>
              <code>{data.remediation_proposal.commands[0]}</code>
            </div>
          )}
          <RemediationActions
            runId={runId}
            initialApproval={data.approval_status}
            initialRemediation={data.remediation_status}
          />
          {data.remediation_result && (
            <pre className="result-box">
              {JSON.stringify(data.remediation_result, null, 2)}
            </pre>
          )}
        </section>
      )}
    </main>
  );
}
