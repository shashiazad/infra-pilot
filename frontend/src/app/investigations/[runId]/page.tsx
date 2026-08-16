import Link from "next/link";

import { RemediationActions } from "@/components/remediation-actions";
import { apiGet } from "@/lib/api";
import type { Investigation } from "@/types";

function ListCard({title,items}:{title:string;items:string[]}) { return <div className="analysis-card"><h3>{title}</h3>{items.length?<ul>{items.map((item)=><li key={item}>{item}</li>)}</ul>:<p className="muted">No items reported.</p>}</div>; }

export default async function InvestigationPage({params}:{params:Promise<{runId:string}>}) {
  const {runId}=await params; let investigation:Investigation;
  try { investigation=await apiGet<Investigation>(`/investigations/${runId}`); }
  catch { return <main className="page"><div className="empty-state"><strong>Investigation unavailable</strong><p>Confirm the backend is running and the run ID is valid.</p><Link className="text-link" href="/incidents">Return to incidents</Link></div></main>; }
  const classification=investigation.classification??{}; const analysis=investigation.analysis;
  return <main className="page">
    <Link href={`/incidents/${investigation.incident_id}`} className="back-link">← Incident detail</Link>
    <div className="detail-hero investigation-hero"><div><span className="eyebrow">INVESTIGATION RUN</span><h1>Evidence report</h1><p className="mono">{investigation.run_id}</p></div><span className={`badge ${investigation.status==="COMPLETED"?"badge-success":"badge-danger"}`}>{investigation.status}</span></div>
    <div className="metric-strip"><div><span>CLASSIFICATION</span><strong>{String(classification.category??"Unknown")}</strong></div><div><span>PRIORITY</span><strong>{String(classification.priority??"Unknown")}</strong></div><div><span>TOOL ITERATIONS</span><strong>{investigation.tool_iterations}</strong></div><div><span>CONFIDENCE</span><strong>{analysis?`${Math.round(analysis.confidence*100)}%`:"—"}</strong></div></div>

    <section className="section"><div className="section-heading"><div><span className="eyebrow">AGENT STRATEGY</span><h2>Investigation plan</h2></div></div><ol className="plan-list">{(investigation.investigation_plan??[]).map((step,index)=><li key={step}><span>{String(index+1).padStart(2,"0")}</span>{step}</li>)}</ol></section>

    <section className="section"><div className="section-heading"><div><span className="eyebrow">LIVE INFRASTRUCTURE</span><h2>Collected evidence</h2></div><span className="count-label">{investigation.evidence.length} findings</span></div><div className="evidence-grid">{investigation.evidence.map((item,index)=><article className="evidence-card" key={`${item.tool}-${index}`}><div><strong>{item.tool}</strong><span className={`badge ${item.status==="SUCCESS"?"badge-success":"badge-danger"}`}>{item.status}</span></div><pre>{JSON.stringify(item.finding,null,2)}</pre></article>)}</div></section>

    <section className="section"><div className="section-heading"><div><span className="eyebrow">SYNTHESIS</span><h2>Analysis</h2></div></div>{analysis?<><div className="summary-card"><span>SUMMARY</span><p>{analysis.summary}</p></div><div className="analysis-grid"><ListCard title="Confirmed facts" items={analysis.confirmed_facts}/><ListCard title="Possible causes" items={analysis.possible_causes}/><ListCard title="Recommended checks" items={analysis.recommended_checks}/></div></>:<div className="empty-state compact"><strong>Analysis not available</strong></div>}</section>

    {investigation.remediation_proposal&&<section className="section remediation-section"><div className="section-heading"><div><span className="eyebrow">HUMAN CONTROL PLANE</span><h2>Remediation proposal</h2></div><span className="badge badge-warning">{investigation.remediation_proposal.risk} RISK</span></div><div className="proposal-grid"><div><span>ACTION</span><strong>{investigation.remediation_proposal.action.replaceAll("_"," ")}</strong></div><div><span>TARGET</span><strong>{investigation.remediation_proposal.target_service}</strong></div></div><p className="proposal-reason">{investigation.remediation_proposal.reason}</p>{investigation.remediation_proposal.commands.length>0&&<div className="command-preview"><span>PROPOSED COMMAND — DISPLAY ONLY</span><code>{investigation.remediation_proposal.commands[0]}</code></div>}<RemediationActions runId={runId} initialApproval={investigation.approval_status} initialRemediation={investigation.remediation_status}/>{investigation.remediation_result&&<pre className="result-box">{JSON.stringify(investigation.remediation_result,null,2)}</pre>}</section>}
  </main>;
}
