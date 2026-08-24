"""Pydantic schemas for agent outputs — all agents return structured JSON."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.workflow_schema import RiskLevel, WorkflowType


class ClassificationResult(BaseModel):
    workflow_type: WorkflowType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class PlanStep(BaseModel):
    step_number: int
    agent: str
    action: str
    expected_output: str


class PlannerResult(BaseModel):
    workflow_type: WorkflowType
    required_agents: list[str]
    steps: list[PlanStep]
    risk_level: RiskLevel
    expected_outputs: list[str]
    reasoning: str


class RetrievedChunk(BaseModel):
    content: str
    source: str
    score: float = 0.0


class RetrievalResult(BaseModel):
    chunks: list[RetrievedChunk]
    sources_used: list[str]
    fallback_used: bool = False


class DomainAction(BaseModel):
    action_type: str
    tool_name: Optional[str] = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    summary: str


class DomainAgentResult(BaseModel):
    domain: str
    analysis: str
    proposed_action: DomainAction
    extracted_fields: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)


class QAStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class CriticResult(BaseModel):
    qa_status: QAStatus
    hallucination_risk: RiskLevel
    missing_fields: list[str] = Field(default_factory=list)
    requires_human_approval: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    reason: str


class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    result: dict[str, Any]
    execution_time_ms: float = 0.0


class AuditLogEntry(BaseModel):
    workflow_id: str
    workflow_type: str
    agent_name: str
    status: str
    confidence_score: Optional[float] = None
    human_approval_required: bool = False
    tool_executed: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
