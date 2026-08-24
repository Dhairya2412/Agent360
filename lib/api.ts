import type {
  AnalyticsSummary,
  Approval,
  AuditLog,
  Document,
  Workflow,
  WorkflowType,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const REQUEST_TIMEOUT_MS = 30000;

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

function parseErrorDetail(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== "object") return fallback;
  const detail = (payload as { detail?: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === "object" && d && "msg" in d ? String((d as { msg: string }).msg) : String(d)))
      .join("; ");
  }
  return fallback;
}

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        ...(options?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...options?.headers,
      },
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(parseErrorDetail(err, `API error: ${res.status}`), res.status, err);
    }
    return res.json();
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError("Request timed out — is the backend running?", 408);
    }
    throw new ApiError(
      "Cannot reach backend API. Start the backend on port 8000.",
      0,
      err,
    );
  } finally {
    clearTimeout(timeout);
  }
}

export const api = {
  health: () => fetchApi<{ status: string; mock_mode: boolean; chroma?: Record<string, unknown> }>("/api/health"),

  startWorkflow: (data: { workflow_type: WorkflowType; request_text: string }) =>
    fetchApi<Workflow>("/api/workflows/start", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  listWorkflows: () => fetchApi<Workflow[]>("/api/workflows"),
  getWorkflow: (id: string) => fetchApi<Workflow>(`/api/workflows/${id}`),
  retryWorkflow: (id: string) =>
    fetchApi<Workflow>(`/api/workflows/${id}/retry`, { method: "POST" }),

  listPendingApprovals: () => fetchApi<Approval[]>("/api/approvals/pending"),
  approve: (id: string) =>
    fetchApi<unknown>(`/api/approvals/${id}/approve`, { method: "POST" }),
  reject: (id: string, reason?: string) =>
    fetchApi<unknown>(`/api/approvals/${id}/reject?reason=${encodeURIComponent(reason || "Rejected")}`, {
      method: "POST",
    }),
  editApprove: (id: string, edited_action: Record<string, unknown>, notes?: string) =>
    fetchApi<unknown>(`/api/approvals/${id}/edit-approve`, {
      method: "POST",
      body: JSON.stringify({ edited_action, notes }),
    }),

  uploadDocument: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetchApi<{ id: string; filename: string; chunk_count: number; message: string }>(
      "/api/documents/upload",
      { method: "POST", body: form }
    );
  },
  listDocuments: () => fetchApi<Document[]>("/api/documents"),
  deleteDocument: (id: string) =>
    fetchApi<{ message: string }>(`/api/documents/${id}`, { method: "DELETE" }),

  listAuditLogs: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi<AuditLog[]>(`/api/audit-logs${qs}`);
  },

  analyticsSummary: () => fetchApi<AnalyticsSummary>("/api/analytics/summary"),
  analyticsWorkflowTypes: () => fetchApi<{ type: string; count: number }[]>("/api/analytics/workflow-types"),
  analyticsAgentPerformance: () => fetchApi<Record<string, unknown>>("/api/analytics/agent-performance"),
};
