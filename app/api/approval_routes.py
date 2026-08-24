"""Approval API routes."""

from fastapi import APIRouter, HTTPException

from app.schemas.approval_schema import ApprovalEditRequest
from app.services.approval_service import approval_service

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


@router.get("/pending")
async def list_pending_approvals():
    return await approval_service.list_pending()


@router.post("/{approval_id}/approve")
async def approve(approval_id: str):
    try:
        return await approval_service.approve(approval_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{approval_id}/reject")
async def reject(approval_id: str, reason: str = "Rejected by admin"):
    try:
        return await approval_service.reject(approval_id, reason=reason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{approval_id}/edit-approve")
async def edit_approve(approval_id: str, body: ApprovalEditRequest):
    try:
        return await approval_service.edit_and_approve(
            approval_id,
            body.edited_action,
            notes=body.notes or "",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
