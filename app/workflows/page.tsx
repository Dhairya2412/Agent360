"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Topbar } from "@/components/layout/Topbar";
import { WorkflowForm } from "@/components/workflows/WorkflowForm";
import { WorkflowStatusBadge } from "@/components/workflows/WorkflowStatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { Workflow } from "@/lib/types";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    api.listWorkflows()
      .then(setWorkflows)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load workflows"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  return (
    <>
      <Topbar title="Workflows" subtitle="Submit and monitor multi-agent workflow executions" />
      <div className="grid gap-6 p-8 lg:grid-cols-2">
        <WorkflowForm />
        <Card className="gradient-card">
          <CardHeader>
            <CardTitle className="text-base">All Workflows</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-muted-foreground">Loading...</p>
            ) : error ? (
              <ErrorState message={error} onRetry={load} />
            ) : workflows.length === 0 ? (
              <p className="text-muted-foreground">No workflows yet. Submit one to get started.</p>
            ) : (
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {workflows.map((w) => (
                  <Link
                    key={w.id}
                    href={`/workflows/${w.id}`}
                    className="block rounded-lg border border-border p-4 transition-colors hover:bg-secondary/50"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono text-primary">{w.id?.slice(0, 12)}...</span>
                      <WorkflowStatusBadge status={w.status} />
                    </div>
                    <p className="mt-2 text-sm line-clamp-2">{w.request_text}</p>
                    <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                      <span>{w.workflow_type?.replace(/_/g, " ")}</span>
                      <span>{formatDate(w.created_at)}</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
