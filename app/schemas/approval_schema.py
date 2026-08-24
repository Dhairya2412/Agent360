"""Approval request/response schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ApprovalCreate(BaseModel):
    workflow_id: str
    workflow_type: str
    proposed_action: dict[str, Any]
    risk_level: str
    reason: str
    agent_reasoning: str


class ApprovalResponse(BaseModel):
    id: str
    workflow_id: str
    workflow_type: str
    proposed_action: dict[str, Any]
    risk_level: str
    reason: str
    agent_reasoning: str
    status: str = "pending"
    created_at: datetime
    updated_at: datetime


class ApprovalEditRequest(BaseModel):
    edited_action: dict[str, Any]
    notes: Optional[str] = None
