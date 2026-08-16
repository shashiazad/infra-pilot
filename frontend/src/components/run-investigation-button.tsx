"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiPost } from "@/lib/api";
import type { Investigation } from "@/types";

interface RunInvestigationButtonProps {
  incidentId: string;
  rerun?: boolean;
}

export function RunInvestigationButton({
  incidentId,
  rerun = false,
}: RunInvestigationButtonProps) {
  const router = useRouter();
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    try {
      setRunning(true);
      setError(null);
      const result = await apiPost<Investigation>(`/incidents/${incidentId}/investigate`);
      router.push(`/investigations/${result.run_id}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Investigation failed");
      setRunning(false);
    }
  }

  return <div className="action-stack">
    <button onClick={run} disabled={running} className="button button-primary">
      {running ? <><span className="spinner" /> {rerun ? "Rerunning investigation…" : "Investigating infrastructure…"}</> : rerun ? "Rerun investigation" : "Run investigation"}
    </button>
    {error && <p className="inline-error" role="alert">{error}</p>}
  </div>;
}
