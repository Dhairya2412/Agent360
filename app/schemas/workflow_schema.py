"""Pydantic schemas for workflow domain."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class WorkflowType(str, Enum):
    AUTO_DETECT = "AUTO_DETECT"
    IT_HELPDESK = "IT_HELPDESK"
    SUPPLY_CHAIN_ORDER = "SUPPLY_CHAIN_ORDER"
    BANKING_SUPPORT = "BANKING_SUPPORT"
    GENERAL_ENTERPRISE = "GENERAL_ENTERPRISE"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowStartRequest(BaseModel):
    workflow_type: WorkflowType = WorkflowType.AUTO_DETECT
    request_text: str = Field(..., min_length=3, max_length=10000)
    document_ids: list[str] = Field(default_factory=list)


class AgentTraceEntry(BaseModel):
    agent_name: str
    status: str
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    latency_ms: Optional[float] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    id: str
    workflow_type: str
    status: str
    request_text: str
    final_response: Optional[str] = None
    risk_level: Optional[str] = None
    confidence_score: Optional[float] = None
    requires_approval: bool = False
    agent_traces: list[AgentTraceEntry] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    total_latency_ms: Optional[float] = None


class WorkflowListItem(BaseModel):
    id: str
    workflow_type: str
    status: str
    request_text: str
    risk_level: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
