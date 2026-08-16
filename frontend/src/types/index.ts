export interface Incident { id:string; title:string; description:string; service:string; severity:string; status:string; created_at:string; updated_at:string; }
export interface Evidence { tool:string; status:string; finding:unknown; created_at?:string; }
export interface InvestigationAnalysis { summary:string; confirmed_facts:string[]; possible_causes:string[]; recommended_checks:string[]; confidence:number; }
export interface RemediationProposal { action:string; reason:string; target_service:string; risk:string; commands:string[]; requires_approval:boolean; }
export interface InvestigationSummary { run_id:string; incident_id:string; status:string; tool_iterations:number; started_at:string; completed_at?:string|null; }
export interface Investigation { run_id:string; incident_id:string; status:string; classification:Record<string,unknown>|null; investigation_plan:string[]|null; evidence:Evidence[]; analysis:InvestigationAnalysis|null; tool_iterations:number; remediation_proposal?:RemediationProposal|null; approval_status?:string|null; remediation_status?:string|null; remediation_result?:Record<string,unknown>|null; started_at?:string; completed_at?:string|null; }
export interface ApprovalResponse { run_id:string; approval_status:string; remediation_status:string|null; }
export interface ExecutionResponse extends ApprovalResponse { remediation_status:string; remediation_result:Record<string,unknown>|null; }
