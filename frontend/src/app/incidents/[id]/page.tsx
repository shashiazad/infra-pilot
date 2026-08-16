import Link from "next/link";

import { RunInvestigationButton } from "@/components/run-investigation-button";
import { apiGet } from "@/lib/api";
import type { Incident, InvestigationSummary } from "@/types";

export default async function IncidentDetailPage({ params }:{ params:Promise<{id:string}> }) {
  const {id}=await params;
  let incident:Incident; let history:InvestigationSummary[];
  try { [incident,history]=await Promise.all([apiGet<Incident>(`/incidents/${id}`),apiGet<InvestigationSummary[]>(`/incidents/${id}/investigations`)]); }
  catch { return <main className="page"><div className="empty-state"><strong>Incident unavailable</strong><p>Confirm that the backend is running and this incident still exists.</p><Link className="text-link" href="/incidents">Return to incidents</Link></div></main>; }

  return <main className="page">
    <Link href="/incidents" className="back-link">← Incident queue</Link>
    <div className="detail-hero"><div><div className="hero-badges"><span className={`badge ${incident.severity==="SEV-1"?"badge-danger":"badge-warning"}`}>{incident.severity}</span><span className="badge">{incident.status}</span></div><h1>{incident.title}</h1><p>{incident.description}</p></div><RunInvestigationButton incidentId={incident.id}/></div>
    <div className="metric-strip"><div><span>SERVICE</span><strong>{incident.service}</strong></div><div><span>INCIDENT ID</span><strong className="mono">{incident.id.slice(0,13)}…</strong></div><div><span>CREATED</span><strong>{new Date(incident.created_at).toLocaleString()}</strong></div></div>
    <section className="section"><div className="section-heading"><div><span className="eyebrow">INVESTIGATION MEMORY</span><h2>Previous runs</h2></div><span className="count-label">{history.length} total</span></div>
      {history.length===0?<div className="empty-state compact"><strong>No previous investigations</strong><p>Run the agent to create the first evidence-backed analysis.</p></div>:<div className="history-list">{history.map((run)=><Link key={run.run_id} href={`/investigations/${run.run_id}`} className="history-row"><span><b>{run.status}</b><small>{new Date(run.started_at).toLocaleString()}</small></span><span>{run.tool_iterations} tool iterations</span><span>View analysis →</span></Link>)}</div>}
    </section>
  </main>;
}
