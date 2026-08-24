"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Check, X, Edit, Loader2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toaster";
import { api } from "@/lib/api";
import { RiskBadge } from "@/components/workflows/WorkflowStatusBadge";
import type { Approval } from "@/lib/types";

interface ApprovalCardProps {
  approval: Approval;
  onUpdate: () => void;
}

export function ApprovalCard({ approval, onUpdate }: ApprovalCardProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [editedAction, setEditedAction] = useState(JSON.stringify(approval.proposed_action, null, 2));
  const { toast } = useToast();

  const handleApprove = async () => {
    setLoading("approve");
    try {
      await api.approve(approval.id);
      toast({ title: "Approved", description: "Tool executed successfully" });
      onUpdate();
    } catch (err) {
      toast({ title: "Error", description: String(err), variant: "destructive" });
    } finally {
      setLoading(null);
    }
  };

  const handleReject = async () => {
    setLoading("reject");
    try {
      await api.reject(approval.id);
      toast({ title: "Rejected", description: "Workflow marked as rejected" });
      onUpdate();
    } catch (err) {
      toast({ title: "Error", description: String(err), variant: "destructive" });
    } finally {
      setLoading(null);
    }
  };

  const handleEditApprove = async () => {
    setLoading("edit");
    try {
      const parsed = JSON.parse(editedAction);
      await api.editApprove(approval.id, parsed, "Edited by admin");
      toast({ title: "Edited & Approved", description: "Modified action executed" });
      setEditing(false);
      onUpdate();
    } catch (err) {
      toast({ title: "Error", description: String(err), variant: "destructive" });
    } finally {
      setLoading(null);
    }
  };

  const proposed = approval.proposed_action as { summary?: string; tool_name?: string };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <Card className="gradient-card border-amber-500/20">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                {approval.workflow_type.replace(/_/g, " ")}
              </CardTitle>
              <p className="mt-1 text-xs text-muted-foreground">
                Workflow: {approval.workflow_id?.slice(0, 12)}...
              </p>
            </div>
            <RiskBadge level={approval.risk_level} />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-medium">Proposed Action</p>
            <p className="mt-1 text-sm text-muted-foreground">
              {proposed.summary || proposed.tool_name || "No summary"}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium">Reason</p>
            <p className="mt-1 text-sm text-muted-foreground">{approval.reason}</p>
          </div>
          <div>
            <p className="text-sm font-medium">Agent Reasoning</p>
            <p className="mt-1 text-sm text-muted-foreground">{approval.agent_reasoning}</p>
          </div>

          {editing && (
            <textarea
              value={editedAction}
              onChange={(e) => setEditedAction(e.target.value)}
              rows={6}
              className="w-full rounded-lg border border-border bg-secondary p-3 font-mono text-xs"
            />
          )}

          <div className="flex flex-wrap gap-2">
            <Button size="sm" onClick={handleApprove} disabled={!!loading}>
              {loading === "approve" ? <Loader2 className="mr-1 h-3 w-3 animate-spin" /> : <Check className="mr-1 h-3 w-3" />}
              Approve
            </Button>
            <Button size="sm" variant="destructive" onClick={handleReject} disabled={!!loading}>
              {loading === "reject" ? <Loader2 className="mr-1 h-3 w-3 animate-spin" /> : <X className="mr-1 h-3 w-3" />}
              Reject
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => (editing ? handleEditApprove() : setEditing(true))}
              disabled={!!loading}
            >
              {loading === "edit" ? <Loader2 className="mr-1 h-3 w-3 animate-spin" /> : <Edit className="mr-1 h-3 w-3" />}
              {editing ? "Save & Approve" : "Edit & Approve"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
