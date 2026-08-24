"""Audit log API routes."""

from typing import Optional

from fastapi import APIRouter

from app.database.repositories import audit_repo

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])


@router.get("")
async def list_audit_logs(
    workflow_id: Optional[str] = None,
    workflow_type: Optional[str] = None,
    agent_name: Optional[str] = None,
    limit: int = 100,
):
    logs = await audit_repo.list_all(workflow_id=workflow_id, limit=limit)

    if workflow_type:
        logs = [l for l in logs if l.get("workflow_type") == workflow_type]
    if agent_name:
        logs = [l for l in logs if l.get("agent_name") == agent_name]

    return logs


@router.get("/{workflow_id}")
async def get_audit_logs_for_workflow(workflow_id: str):
    return await audit_repo.list_all(workflow_id=workflow_id)
