"""Workflow API routes."""

from fastapi import APIRouter, HTTPException

from app.schemas.workflow_schema import WorkflowStartRequest
from app.services.workflow_service import workflow_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("/start")
async def start_workflow(request: WorkflowStartRequest):
    try:
        return await workflow_service.start_workflow(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Workflow start failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to start workflow") from exc


@router.get("")
async def list_workflows(limit: int = 50):
    return await workflow_service.list_workflows(limit=limit)


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    wf = await workflow_service.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.post("/{workflow_id}/retry")
async def retry_workflow(workflow_id: str):
    result = await workflow_service.retry_workflow(workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return result
