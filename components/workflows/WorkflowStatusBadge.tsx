import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const statusMap: Record<string, { variant: "success" | "warning" | "danger" | "secondary" | "default"; label: string }> = {
  completed: { variant: "success", label: "Completed" },
  running: { variant: "default", label: "Running" },
  awaiting_approval: { variant: "warning", label: "Awaiting Approval" },
  failed: { variant: "danger", label: "Failed" },
  rejected: { variant: "danger", label: "Rejected" },
  pending: { variant: "secondary", label: "Pending" },
};

export function WorkflowStatusBadge({ status }: { status: string }) {
  const config = statusMap[status] || { variant: "secondary" as const, label: status };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}

export function RiskBadge({ level }: { level?: string }) {
  const variant = level === "high" || level === "critical" ? "danger" : level === "medium" ? "warning" : "success";
  return (
    <Badge variant={variant} className={cn("capitalize")}>
      {level || "low"}
    </Badge>
  );
}
