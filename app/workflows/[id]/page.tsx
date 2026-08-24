"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { RefreshCw, AlertTriangle } from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { AgentTimeline } from "@/components/workflows/AgentTimeline";
import { WorkflowStatusBadge, RiskBadge } from "@/components/workflows/WorkflowStatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatDate, formatMs } from "@/lib/utils";
import type { Workflow } from "@/lib/types";

export default function WorkflowDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    api.getWorkflow(id)
      .then(setWorkflow)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [id]);

  if (loading) {
    return (
      <>
        <Topbar title="Workflow Details" />
        <div className="flex h-96 items-center justify-center text-muted-foreground">Loading workflow...</div>
      </>
    );
  }

  if (error || !workflow) {
    return (
      <>
        <Topbar title="Workflow Details" />
        <div className="flex h-96 flex-col items-center justify-center gap-2 text-red-400">
          <AlertTriangle className="h-8 w-8" />
          <p>{error || "Workflow not found"}</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar
        title="Workflow Details"
        subtitle={`${workflow.workflow_type?.replace(/_/g, " ")} — ${workflow.id?.slice(0, 12)}...`}
      />
      <div className="space-y-6 p-8">
        <div className="flex flex-wrap items-center gap-4">
          <WorkflowStatusBadge status={workflow.status} />
          <RiskBadge level={workflow.risk_level} />
          {workflow.confidence_score && (
            <span className="text-sm text-muted-foreground">
              Confidence: {(workflow.confidence_score * 100).toFixed(0)}%
            </span>
          )}
          {workflow.total_latency_ms && (
            <span className="text-sm text-muted-foreground">
              Latency: {formatMs(workflow.total_latency_ms)}
            </span>
          )}
          <span className="text-sm text-muted-foreground">{formatDate(workflow.created_at)}</span>
          <Button size="sm" variant="outline" onClick={load}>
            <RefreshCw className="mr-1 h-3 w-3" /> Refresh
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-6">
            <Card className="gradient-card">
              <CardHeader>
                <CardTitle className="text-base">Request</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">{workflow.request_text}</p>
              </CardContent>
            </Card>

            {workflow.final_response && (
              <Card className="gradient-card">
                <CardHeader>
                  <CardTitle className="text-base">Final Response</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="whitespace-pre-wrap text-sm">{workflow.final_response}</p>
                </CardContent>
              </Card>
            )}

            {workflow.tool_result && (
              <Card className="gradient-card">
                <CardHeader>
                  <CardTitle className="text-base">Tool Result</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="overflow-x-auto rounded-lg bg-secondary p-4 text-xs">
                    {JSON.stringify(workflow.tool_result, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            )}
          </div>

          <AgentTimeline workflow={workflow} />
        </div>
      </div>
    </>
  );
}
