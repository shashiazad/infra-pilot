import Link from "next/link";
import { apiGet } from "@/lib/api";
import type { Incident } from "@/types";

function formatTime(value:string) { return new Intl.DateTimeFormat("en",{month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"}).format(new Date(value)); }

export default async function IncidentsPage() {
  let incidents:Incident[]=[]; let unavailable=false;
  try { incidents=await apiGet<Incident[]>("/incidents"); } catch { unavailable=true; }
  return <main className="page">
    <div className="page-heading"><div><span className="eyebrow">INCIDENT QUEUE</span><h1 className="page-title">Active operations</h1><p className="page-copy">Investigate service degradation with live infrastructure evidence.</p></div><div className="count-card"><strong>{incidents.length}</strong><span>INCIDENTS</span></div></div>
    {unavailable ? <div className="empty-state"><strong>Backend connection unavailable</strong><p>Start the InfraPilot API on port 8000, then refresh this page to load the incident queue.</p></div> : incidents.length===0 ? <div className="empty-state"><strong>No incidents in the queue</strong><p>New infrastructure incidents will appear here.</p></div> : <div className="incident-list">{incidents.map((incident)=>{const critical=incident.severity==="SEV-1";return <Link key={incident.id} href={`/incidents/${incident.id}`} className="incident-card"><span className={`severity-rail ${critical?"critical":""}`}/><div><h2 className="incident-title">{incident.title}</h2><div className="incident-meta"><span>{incident.service}</span><span className="separator">/</span><span>{incident.id.slice(0,8)}</span></div></div><div className="card-status"><span className={`badge ${critical?"badge-danger":"badge-warning"}`}>{incident.severity}</span><span className="timestamp">{formatTime(incident.created_at)}</span></div></Link>})}</div>}
  </main>;
}
