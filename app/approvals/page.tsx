"use client";

import { useEffect, useState } from "react";
import { CheckCircle } from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { ApprovalCard } from "@/components/approvals/ApprovalCard";
import { ErrorState } from "@/components/ui/error-state";
import { api } from "@/lib/api";
import type { Approval } from "@/lib/types";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    api.listPendingApprovals()
      .then(setApprovals)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load approvals"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  return (
    <>
      <Topbar title="Human Approvals" subtitle="Review and approve high-risk agent actions" />
      <div className="p-8">
        {loading ? (
          <p className="text-muted-foreground">Loading approvals...</p>
        ) : error ? (
          <ErrorState message={error} onRetry={load} />
        ) : approvals.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-border py-16 text-muted-foreground">
            <CheckCircle className="mb-4 h-12 w-12 text-emerald-400" />
            <p className="font-medium">No pending approvals</p>
            <p className="mt-1 text-sm">All workflows have been reviewed</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {approvals.map((a) => (
              <ApprovalCard key={a.id} approval={a} onUpdate={load} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
