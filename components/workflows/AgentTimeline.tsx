"use client";

import { motion } from "framer-motion";
import {
  Bot,
  Brain,
  Search,
  Shield,
  UserCheck,
  Wrench,
  FileCheck,
  MessageSquare,
  CheckCircle2,
  Clock,
  XCircle,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Workflow } from "@/lib/types";

const AGENT_ICONS: Record<string, React.ElementType> = {
  orchestrator: Bot,
  planner: Brain,
  retrieval: Search,
  domain_specialist: Bot,
  critic: Shield,
  human_approval: UserCheck,
  tool_execution: Wrench,
  audit: FileCheck,
  final_response: MessageSquare,
};

const TIMELINE_STEPS = [
  { key: "orchestrator", label: "Request Classified" },
  { key: "planner", label: "Plan Generated" },
  { key: "retrieval", label: "Context Retrieved" },
  { key: "domain_specialist", label: "Domain Analysis" },
  { key: "critic", label: "QA Check" },
  { key: "human_approval", label: "Human Approval" },
  { key: "tool_execution", label: "Tool Executed" },
  { key: "final_response", label: "Final Response" },
];

function getStepStatus(workflow: Workflow, stepKey: string): "completed" | "pending" | "skipped" | "failed" {
  const traces = workflow.agent_traces || [];
  const trace = traces.find((t) => t.agent_name === stepKey);

  if (stepKey === "human_approval") {
    if (workflow.status === "awaiting_approval") return "pending";
    if (!workflow.requires_approval && !trace) return "skipped";
  }

  if (trace) {
    if (trace.status === "failed") return "failed";
    if (trace.status === "pending") return "pending";
    return "completed";
  }

  if (workflow.status === "completed" || workflow.status === "failed") {
    const stepIndex = TIMELINE_STEPS.findIndex((s) => s.key === stepKey);
    const completedCount = traces.length;
    if (stepIndex < completedCount) return "completed";
  }

  return "pending";
}

export function AgentTimeline({ workflow }: { workflow: Workflow }) {
  return (
    <Card className="gradient-card">
      <CardHeader>
        <CardTitle className="text-base">Agent Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative space-y-0">
          {TIMELINE_STEPS.map((step, i) => {
            const status = getStepStatus(workflow, step.key);
            const Icon = AGENT_ICONS[step.key] || Bot;
            const trace = workflow.agent_traces?.find((t) => t.agent_name === step.key);

            if (status === "skipped") return null;

            return (
              <motion.div
                key={step.key}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="relative flex gap-4 pb-8 last:pb-0"
              >
                {i < TIMELINE_STEPS.length - 1 && (
                  <div className="absolute left-5 top-10 h-full w-px bg-border" />
                )}
                <div
                  className={`relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 ${
                    status === "completed"
                      ? "border-emerald-500 bg-emerald-500/10"
                      : status === "pending"
                      ? "border-amber-500 bg-amber-500/10"
                      : status === "failed"
                      ? "border-red-500 bg-red-500/10"
                      : "border-border bg-secondary"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 pt-1">
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{step.label}</p>
                    {status === "completed" && (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    )}
                    {status === "pending" && <Clock className="h-4 w-4 text-amber-400" />}
                    {status === "failed" && <XCircle className="h-4 w-4 text-red-400" />}
                    <Badge variant={status === "completed" ? "success" : status === "pending" ? "warning" : "danger"}>
                      {status}
                    </Badge>
                  </div>
                  {trace?.details && (
                    <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                      {JSON.stringify(trace.details).slice(0, 120)}...
                    </p>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
