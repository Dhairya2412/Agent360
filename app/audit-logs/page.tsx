"use client";

import { useEffect, useState } from "react";
import { Topbar } from "@/components/layout/Topbar";
import { AuditLogTable } from "@/components/audit/AuditLogTable";
import { ErrorState } from "@/components/ui/error-state";
import { api } from "@/lib/api";
import type { AuditLog } from "@/lib/types";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState("");
  const [filterAgent, setFilterAgent] = useState("");

  const load = () => {
    setLoading(true);
    setError(null);
    const params: Record<string, string> = {};
    if (filterType) params.workflow_type = filterType;
    if (filterAgent) params.agent_name = filterAgent;
    api.listAuditLogs(params)
      .then(setLogs)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load audit logs"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [filterType, filterAgent]);

  return (
    <>
      <Topbar title="Audit Logs" subtitle="Searchable workflow and agent trace history" />
      <div className="space-y-4 p-8">
        <div className="flex flex-wrap gap-4">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="rounded-lg border border-border bg-secondary px-4 py-2 text-sm"
          >
            <option value="">All Types</option>
            <option value="IT_HELPDESK">IT Helpdesk</option>
            <option value="SUPPLY_CHAIN_ORDER">Supply Chain</option>
            <option value="BANKING_SUPPORT">Banking Support</option>
          </select>
          <select
            value={filterAgent}
            onChange={(e) => setFilterAgent(e.target.value)}
            className="rounded-lg border border-border bg-secondary px-4 py-2 text-sm"
          >
            <option value="">All Agents</option>
            <option value="orchestrator">Orchestrator</option>
            <option value="critic">Critic</option>
            <option value="human_approval">Human Approval</option>
            <option value="audit">Audit</option>
          </select>
        </div>
        {error ? (
          <ErrorState message={error} onRetry={load} />
        ) : (
          <AuditLogTable logs={logs} loading={loading} />
        )}
      </div>
    </>
  );
}
