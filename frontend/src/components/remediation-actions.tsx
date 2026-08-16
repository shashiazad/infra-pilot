"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiPost } from "@/lib/api";
import type { ApprovalResponse, ExecutionResponse } from "@/types";

interface Props { runId:string; initialApproval?:string|null; initialRemediation?:string|null; }

export function RemediationActions({ runId, initialApproval, initialRemediation }:Props) {
  const router=useRouter();
  const [approval,setApproval]=useState(initialApproval??null);
  const [remediation,setRemediation]=useState(initialRemediation??null);
  const [busy,setBusy]=useState<string|null>(null);
  const [error,setError]=useState<string|null>(null);

  async function decide(action:"approve"|"reject") {
    try { setBusy(action); setError(null); const result=await apiPost<ApprovalResponse>(`/investigations/${runId}/${action}`); setApproval(result.approval_status); setRemediation(result.remediation_status); router.refresh(); }
    catch(caught){setError(caught instanceof Error?caught.message:"Request failed");}
    finally{setBusy(null);}
  }

  async function execute() {
    try { setBusy("execute"); setError(null); const result=await apiPost<ExecutionResponse>(`/investigations/${runId}/execute`); setApproval(result.approval_status); setRemediation(result.remediation_status); router.refresh(); }
    catch(caught){setError(caught instanceof Error?caught.message:"Execution failed");}
    finally{setBusy(null);}
  }

  const pending=approval==="PENDING";
  const canExecute=approval==="APPROVED"&&remediation==="NOT_STARTED";
  return <div>
    <div className="state-row"><span>Approval <b className={`badge ${approval==="APPROVED"?"badge-success":approval==="REJECTED"?"badge-danger":"badge-warning"}`}>{approval??"UNAVAILABLE"}</b></span><span>Remediation <b className={`badge ${remediation==="COMPLETED"?"badge-success":remediation==="FAILED"?"badge-danger":""}`}>{remediation??"UNAVAILABLE"}</b></span></div>
    <div className="button-row">
      <button className="button button-primary" disabled={!pending||busy!==null} onClick={()=>decide("approve")}>{busy==="approve"?"Approving…":"Approve"}</button>
      <button className="button button-secondary" disabled={!pending||busy!==null} onClick={()=>decide("reject")}>{busy==="reject"?"Rejecting…":"Reject"}</button>
      <button className="button button-execute" disabled={!canExecute||busy!==null} onClick={execute}>{busy==="execute"?"Executing…":"Execute approved action"}</button>
    </div>
    {error&&<p className="inline-error" role="alert">{error}</p>}
    <p className="safety-note">Execution is limited to server-side allow-listed Kubernetes actions. Generated command text is never run.</p>
  </div>;
}
