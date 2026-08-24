"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  CheckCircle,
  Clock,
  FileText,
  AlertTriangle,
  TrendingUp,
} from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { MetricsCard } from "@/components/dashboard/MetricsCard";
import { WorkflowChart } from "@/components/dashboard/WorkflowChart";
import { WorkflowStatusBadge } from "@/components/workflows/WorkflowStatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatDate, formatMs } from "@/lib/utils";
import type { AnalyticsSummary, Workflow } from "@/lib/types";

export default function DashboardPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [typeData, setTypeData] = useState<{ type: string; count: number }[]>([]);
  const [perf, setPerf] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.analyticsSummary(),
      api.listWorkflows(),
      api.analyticsWorkflowTypes(),
      api.analyticsAgentPerformance(),
    ])
      .then(([s, w, t, p]) => {
        setSummary(s);
        setWorkflows(w.slice(0, 8));
        setTypeData(t);
        setPerf(p);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const statusBreakdown = (perf?.status_breakdown as Record<string, number>) || {};
  const statusData = [
    { name: "Completed", value: statusBreakdown.completed || 0 },
    { name: "Failed", value: statusBreakdown.failed || 0 },
    { name: "Pending Approval", value: statusBreakdown.awaiting_approval || 0 },
  ].filter((d) => d.value > 0);

  if (loading) {
    return (
      <>
        <Topbar title="Dashboard" subtitle="Loading metrics..." />
        <div className="flex h-96 items-center justify-center text-muted-foreground">Loading dashboard...</div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Topbar title="Dashboard" />
        <div className="flex h-96 flex-col items-center justify-center gap-2 text-red-400">
          <AlertTriangle className="h-8 w-8" />
          <p>Failed to load dashboard: {error}</p>
          <p className="text-sm text-muted-foreground">Ensure backend is running on port 8000</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title="Dashboard" subtitle="Enterprise workflow automation overview" />
      <div className="space-y-6 p-8">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <MetricsCard title="Total Workflows" value={summary?.total_workflows ?? 0} icon={Activity} />
          <MetricsCard title="Success Rate" value={`${summary?.success_rate ?? 0}%`} icon={TrendingUp} trend="Last 30 days" />
          <MetricsCard title="Pending Approvals" value={summary?.pending_approvals ?? 0} icon={CheckCircle} />
          <MetricsCard title="Avg Resolution" value={formatMs(summary?.avg_resolution_time_ms)} icon={Clock} />
          <MetricsCard title="Failed Runs" value={summary?.failed_runs ?? 0} icon={AlertTriangle} />
          <MetricsCard title="Documents Indexed" value={summary?.total_documents ?? 0} icon={FileText} />
        </div>

        <WorkflowChart typeData={typeData} statusData={statusData.length ? statusData : [{ name: "No data", value: 1 }]} />

        <Card className="gradient-card">
          <CardHeader>
            <CardTitle className="text-base">Recent Workflows</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-muted-foreground">
                    <th className="pb-3 pr-4 font-medium">ID</th>
                    <th className="pb-3 pr-4 font-medium">Type</th>
                    <th className="pb-3 pr-4 font-medium">Request</th>
                    <th className="pb-3 pr-4 font-medium">Status</th>
                    <th className="pb-3 pr-4 font-medium">Confidence</th>
                    <th className="pb-3 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {workflows.map((w) => (
                    <tr key={w.id} className="border-b border-border/50 hover:bg-secondary/30">
                      <td className="py-3 pr-4">
                        <Link href={`/workflows/${w.id}`} className="font-mono text-xs text-primary hover:underline">
                          {w.id?.slice(0, 8)}...
                        </Link>
                      </td>
                      <td className="py-3 pr-4">{w.workflow_type?.replace(/_/g, " ")}</td>
                      <td className="py-3 pr-4 max-w-xs truncate text-muted-foreground">{w.request_text}</td>
                      <td className="py-3 pr-4"><WorkflowStatusBadge status={w.status} /></td>
                      <td className="py-3 pr-4">{w.confidence_score?.toFixed(2) ?? "—"}</td>
                      <td className="py-3 text-xs text-muted-foreground">{formatDate(w.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
