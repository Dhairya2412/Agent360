"use client";

import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import type { AuditLog } from "@/lib/types";

interface AuditLogTableProps {
  logs: AuditLog[];
  loading?: boolean;
}

export function AuditLogTable({ logs, loading }: AuditLogTableProps) {
  if (loading) {
    return (
      <div className="flex h-48 items-center justify-center text-muted-foreground">
        Loading audit logs...
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="flex h-48 flex-col items-center justify-center text-muted-foreground">
        <p>No audit logs found</p>
        <p className="text-sm">Run a workflow to generate traces</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-secondary/50">
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Workflow ID</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Type</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Agent</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Confidence</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Approval</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Tool</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Created</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, i) => (
            <tr key={log.id || i} className="border-b border-border/50 hover:bg-secondary/30">
              <td className="px-4 py-3 font-mono text-xs">{log.workflow_id?.slice(0, 10)}...</td>
              <td className="px-4 py-3">{log.workflow_type?.replace(/_/g, " ")}</td>
              <td className="px-4 py-3">{log.agent_name}</td>
              <td className="px-4 py-3">
                <Badge variant={log.status === "completed" ? "success" : log.status === "failed" ? "danger" : "warning"}>
                  {log.status}
                </Badge>
              </td>
              <td className="px-4 py-3">{log.confidence_score?.toFixed(2) ?? "—"}</td>
              <td className="px-4 py-3">{log.human_approval_required ? "Yes" : "No"}</td>
              <td className="px-4 py-3 text-xs">{log.tool_executed || "—"}</td>
              <td className="px-4 py-3 text-xs text-muted-foreground">{formatDate(log.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
