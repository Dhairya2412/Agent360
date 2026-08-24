"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import { Topbar } from "@/components/layout/Topbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";
import { api } from "@/lib/api";

export default function AnalyticsPage() {
  const [typeData, setTypeData] = useState<{ type: string; count: number }[]>([]);
  const [perf, setPerf] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    Promise.all([api.analyticsWorkflowTypes(), api.analyticsAgentPerformance()])
      .then(([t, p]) => {
        setTypeData(t);
        setPerf(p);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load analytics"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const statusBreakdown = (perf?.status_breakdown as Record<string, number>) || {};
  const statusChart = Object.entries(statusBreakdown).map(([name, value]) => ({
    name: name.replace(/_/g, " "),
    value,
  }));

  const confidenceData = Object.entries(
    (perf?.avg_confidence_by_agent as Record<string, number>) || {}
  ).map(([agent, confidence]) => ({ agent, confidence }));

  const agentLatency = (perf?.agent_latency as { agent: string; avg_confidence: number }[]) || [];

  if (loading) {
    return (
      <>
        <Topbar title="Analytics" />
        <div className="flex h-96 items-center justify-center text-muted-foreground">Loading analytics...</div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Topbar title="Analytics" />
        <div className="p-8">
          <ErrorState message={error} onRetry={load} />
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar title="Analytics" subtitle="Workflow performance and agent metrics" />
      <div className="grid gap-6 p-8 lg:grid-cols-2">
        <Card className="gradient-card">
          <CardHeader>
            <CardTitle className="text-base">Workflows by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={typeData.map((d) => ({ ...d, label: d.type.replace(/_/g, " ") }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8" }} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }} />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="gradient-card">
          <CardHeader>
            <CardTitle className="text-base">Success vs Failed Workflows</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={statusChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8" }} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }} />
                <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="gradient-card">
          <CardHeader>
            <CardTitle className="text-base">Average Confidence by Workflow Type</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={confidenceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="agent" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis domain={[0, 1]} tick={{ fill: "#94a3b8" }} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }} />
                <Bar dataKey="confidence" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="gradient-card">
          <CardHeader>
            <CardTitle className="text-base">
              Human Approval Rate: {(perf?.human_approval_rate as number) ?? 0}%
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={agentLatency}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="agent" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis domain={[0, 1]} tick={{ fill: "#94a3b8" }} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }} />
                <Line type="monotone" dataKey="avg_confidence" stroke="#f59e0b" strokeWidth={2} dot={{ fill: "#f59e0b" }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
