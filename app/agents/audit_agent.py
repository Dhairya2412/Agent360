"""Audit agent — persists complete workflow traces."""

from typing import Any

from app.database.repositories import audit_repo, trace_repo


async def log_agent_trace(workflow_id: str, agent_name: str, status: str, details: dict[str, Any]) -> None:
    await trace_repo.add(workflow_id, {
        "agent_name": agent_name,
        "status": status,
        "details": details,
    })


async def log_audit_entry(
    workflow_id: str,
    workflow_type: str,
    agent_name: str,
    status: str,
    confidence_score: float | None = None,
    human_approval_required: bool = False,
    tool_executed: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = {
        "workflow_id": workflow_id,
        "workflow_type": workflow_type,
        "agent_name": agent_name,
        "status": status,
        "confidence_score": confidence_score,
        "human_approval_required": human_approval_required,
        "tool_executed": tool_executed,
        "details": details or {},
    }
    return await audit_repo.create(entry)
