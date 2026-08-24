export type WorkflowType =
  | "AUTO_DETECT"
  | "IT_HELPDESK"
  | "SUPPLY_CHAIN_ORDER"
  | "BANKING_SUPPORT"
  | "GENERAL_ENTERPRISE";

export type WorkflowStatus =
  | "pending"
  | "running"
  | "awaiting_approval"
  | "completed"
  | "failed"
  | "rejected";

export interface Workflow {
  id: string;
  workflow_type: string;
  status: string;
  request_text: string;
  final_response?: string;
  risk_level?: string;
  confidence_score?: number;
  requires_approval?: boolean;
  agent_traces?: AgentTrace[];
  tool_result?: Record<string, unknown>;
  critic_result?: Record<string, unknown>;
  domain_result?: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
  total_latency_ms?: number;
}

export interface AgentTrace {
  agent_name: string;
  status: string;
  details?: Record<string, unknown>;
  created_at?: string;
  timestamp?: number;
}

export interface Approval {
  id: string;
  workflow_id: string;
  workflow_type: string;
  proposed_action: Record<string, unknown>;
  risk_level: string;
  reason: string;
  agent_reasoning: string;
  status: string;
  created_at: string;
}

export interface AuditLog {
  id?: string;
  workflow_id: string;
  workflow_type: string;
  agent_name: string;
  status: string;
  confidence_score?: number;
  human_approval_required: boolean;
  tool_executed?: string;
  created_at: string;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  chunk_count: number;
  status: string;
  created_at: string;
}

export interface AnalyticsSummary {
  total_workflows: number;
  success_rate: number;
  pending_approvals: number;
  avg_resolution_time_ms: number;
  failed_runs: number;
  total_documents: number;
}
