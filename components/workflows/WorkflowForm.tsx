"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Send, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useToast } from "@/components/ui/toaster";
import { api } from "@/lib/api";
import type { WorkflowType } from "@/lib/types";

const WORKFLOW_TYPES: { value: WorkflowType; label: string }[] = [
  { value: "AUTO_DETECT", label: "Auto Detect" },
  { value: "IT_HELPDESK", label: "IT Helpdesk" },
  { value: "SUPPLY_CHAIN_ORDER", label: "Supply Chain Order" },
  { value: "BANKING_SUPPORT", label: "Banking Support" },
];

const EXAMPLES = [
  "My VPN keeps disconnecting and I can't access internal tools",
  "Order 200 Industrial Bearing 6205 for Acme Industries, delivery 2026-07-15",
  "Customer reports unauthorized $2,400 charge — possible fraud on card ending 4521",
];

export function WorkflowForm() {
  const [workflowType, setWorkflowType] = useState<WorkflowType>("AUTO_DETECT");
  const [requestText, setRequestText] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!requestText.trim()) {
      toast({ title: "Error", description: "Please enter a request", variant: "destructive" });
      return;
    }
    setLoading(true);
    try {
      const result = await api.startWorkflow({ workflow_type: workflowType, request_text: requestText });
      toast({ title: "Workflow started", description: `ID: ${result.id?.slice(0, 8)}...` });
      router.push(`/workflows/${result.id}`);
    } catch (err) {
      toast({ title: "Failed to start workflow", description: String(err), variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const result = await api.uploadDocument(file);
      toast({ title: "Document uploaded", description: result.message });
    } catch (err) {
      toast({ title: "Upload failed", description: String(err), variant: "destructive" });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card className="gradient-card">
      <CardHeader>
        <CardTitle>Submit Workflow Request</CardTitle>
        <CardDescription>
          Enter a messy business request — agents will classify, plan, retrieve context, and execute.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium">Workflow Type</label>
            <div className="flex flex-wrap gap-2">
              {WORKFLOW_TYPES.map((t) => (
                <button
                  key={t.value}
                  type="button"
                  onClick={() => setWorkflowType(t.value)}
                  className={`rounded-lg border px-4 py-2 text-sm transition-all ${
                    workflowType === t.value
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border hover:bg-secondary"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Request</label>
            <textarea
              value={requestText}
              onChange={(e) => setRequestText(e.target.value)}
              rows={5}
              placeholder="Describe your issue in natural language..."
              className="w-full rounded-lg border border-border bg-secondary p-4 text-sm outline-none focus:ring-2 focus:ring-primary/50"
            />
            <div className="mt-2 flex flex-wrap gap-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  type="button"
                  onClick={() => setRequestText(ex)}
                  className="rounded-md bg-secondary px-2 py-1 text-xs text-muted-foreground hover:text-foreground"
                >
                  {ex.slice(0, 40)}...
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Optional Document (PDF, TXT, CSV, MD)</label>
            <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-dashed border-border p-4 hover:bg-secondary/50">
              <Upload className="h-5 w-5 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                {uploading ? "Uploading..." : "Click to upload knowledge document"}
              </span>
              <input type="file" className="hidden" accept=".pdf,.txt,.csv,.md" onChange={handleFileUpload} />
            </label>
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
            Start Workflow
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
