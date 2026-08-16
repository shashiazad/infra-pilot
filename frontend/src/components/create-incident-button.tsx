"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { apiPost } from "@/lib/api";
import type { Incident } from "@/types";

export function CreateIncidentButton(){
  const router=useRouter();
  const[open,setOpen]=useState(false);
  const[submitting,setSubmitting]=useState(false);
  const[error,setError]=useState<string|null>(null);

  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();
    const form=new FormData(event.currentTarget);
    try{
      setSubmitting(true);setError(null);
      const incident=await apiPost<Incident>("/incidents",{
        title:String(form.get("title")),
        description:String(form.get("description")),
        service:String(form.get("service")),
        severity:String(form.get("severity")),
      });
      setOpen(false);
      router.push(`/incidents/${incident.id}`);
      router.refresh();
    }catch(caught){
      setError(caught instanceof Error?caught.message:"Unable to create incident");
      setSubmitting(false);
    }
  }

  return <>
    <button className="button button-primary" onClick={()=>setOpen(true)}>Create incident</button>
    {open&&<div className="modal-backdrop" role="presentation" onMouseDown={()=>!submitting&&setOpen(false)}>
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="create-incident-title" onMouseDown={event=>event.stopPropagation()}>
        <div className="modal-header"><div><span className="eyebrow">Manual intake</span><h2 id="create-incident-title">Create incident</h2></div><button className="modal-close" aria-label="Close" disabled={submitting} onClick={()=>setOpen(false)}>×</button></div>
        <form className="incident-form" onSubmit={submit}>
          <label>Title<input name="title" required minLength={3} maxLength={255} placeholder="Payment service error rate elevated" autoFocus/></label>
          <label>Service<input name="service" required maxLength={100} placeholder="prod-demo-payment"/></label>
          <label>Severity<select name="severity" defaultValue="SEV-2"><option value="SEV-1">SEV-1 — Critical</option><option value="SEV-2">SEV-2 — High</option><option value="SEV-3">SEV-3 — Moderate</option></select></label>
          <label>Description<textarea name="description" required rows={5} placeholder="Describe the observed symptoms and operational impact."/></label>
          {error&&<p className="inline-error" role="alert">{error}</p>}
          <div className="modal-actions"><button type="button" className="button" disabled={submitting} onClick={()=>setOpen(false)}>Cancel</button><button type="submit" className="button button-primary" disabled={submitting}>{submitting?<><span className="spinner"/>Creating…</>:"Create incident"}</button></div>
        </form>
      </section>
    </div>}
  </>
}
