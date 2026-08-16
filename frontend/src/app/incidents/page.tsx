import { IncidentTable, MetricCard } from "@/components/operations-ui";
import { CreateIncidentButton } from "@/components/create-incident-button";
import { apiGet } from "@/lib/api";
import type { Incident } from "@/types";

export default async function IncidentsPage() {
  let incidents:Incident[]=[]; let unavailable=false;
  try { incidents=await apiGet<Incident[]>("/incidents"); } catch { unavailable=true; }
  const active=incidents.filter(i=>i.status!=="RESOLVED");
  return <main className="page">
    <div className="page-header"><div><span className="eyebrow">Incident queue</span><h1>Incidents</h1><p>Track, investigate, and resolve infrastructure degradation.</p></div><div className="header-actions"><CreateIncidentButton/></div></div>
    {!unavailable&&<div className="metrics-grid"><MetricCard label="Total incidents" value={incidents.length}/><MetricCard label="Active" value={active.length} tone={active.length?"yellow":"green"}/><MetricCard label="SEV-1 active" value={active.filter(i=>i.severity==="SEV-1").length} tone="red"/><MetricCard label="Services affected" value={new Set(active.map(i=>i.service)).size}/></div>}
    {unavailable ? <div className="empty-state"><strong>Backend connection unavailable</strong><p>Start the InfraPilot API on port 8000, then refresh this page.</p><div className="technical-note">GET /api/v1/incidents</div></div> : incidents.length===0 ? <div className="empty-state"><strong>No active incidents</strong><p>New infrastructure incidents will appear here.</p></div> : <><div className="filters"><input className="filter-input" placeholder="Search title, ID, or service" aria-label="Search incidents"/><select className="filter-select"><option>All severities</option></select><select className="filter-select"><option>All statuses</option></select><select className="filter-select"><option>All services</option></select></div><section className="panel"><div className="panel-header"><h2>Incident records</h2><span className="panel-subtitle">{incidents.length} records</span></div><IncidentTable incidents={incidents}/></section></>}
  </main>;
}
