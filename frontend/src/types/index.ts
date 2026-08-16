export interface Incident { id:string; title:string; description:string; service:string; severity:string; status:string; created_at:string; updated_at:string; }
export interface Evidence { tool:string; status:string; finding:unknown; created_at?:string; }
export interface InvestigationAnalysis { summary:string; confirmed_facts:string[]; possible_causes:string[]; recommended_checks:string[]; confidence:number; }
export interface RemediationProposal { action:string; reason:string; target_service:string; risk:string; commands:string[]; requires_approval:boolean; }
export interface InvestigationSummary { run_id:string; incident_id:string; status:string; tool_iterations:number; started_at:string; completed_at?:string|null; }
export interface Investigation { run_id:string; incident_id:string; status:string; classification:Record<string,unknown>|null; investigation_plan:string[]|null; evidence:Evidence[]; analysis:InvestigationAnalysis|null; tool_iterations:number; remediation_proposal?:RemediationProposal|null; approval_status?:string|null; remediation_status?:string|null; remediation_result?:Record<string,unknown>|null; runbooks:RunbookReference[]; historical_incidents:HistoricalIncident[]; started_at?:string; completed_at?:string|null; }
export interface ApprovalResponse { run_id:string; approval_status:string; remediation_status:string|null; }
export interface ExecutionResponse extends ApprovalResponse { remediation_status:string; remediation_result:Record<string,unknown>|null; }
export interface InvestigationListItem extends InvestigationSummary { incident_title:string; service:string; severity:string; confidence:number|null; }
export interface RunbookReference { title?:string; source?:string; content?:string; score?:number; [key:string]:unknown; }
export interface HistoricalIncident { run_id?:string; classification?:Record<string,unknown>|null; analysis?:InvestigationAnalysis|null; tool_iterations?:number; [key:string]:unknown; }
export interface RunbookCatalogItem { title:string; source:string; chunks:number; last_indexed:string; content:string; index_status:string; }
export interface PodSnapshot { name:string; phase:string; ready:boolean; restarts:number; cpu:string|null; memory:string|null; }
export interface ServiceSnapshot { service:string; namespace:string; health:string; desired_replicas:number; ready_replicas:number; available_replicas:number; restarts:number; cpu:string|null; memory:string|null; http_5xx_rate_percent:number|null; p95_latency_ms:number|null; deployment_status:string; pods:PodSnapshot[]; recent_warnings:string[]; }
export interface RemediationAuditItem { run_id:string; incident_id:string; incident_title:string; service:string; time:string; action:string; target:string; risk:string; approval_status:string|null; remediation_status:string|null; result:Record<string,unknown>|null; }
