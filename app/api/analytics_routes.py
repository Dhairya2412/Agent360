"""Analytics API routes."""

from fastapi import APIRouter

from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def analytics_summary():
    return await analytics_service.summary()


@router.get("/workflow-types")
async def workflow_types():
    return await analytics_service.workflow_types()


@router.get("/agent-performance")
async def agent_performance():
    return await analytics_service.agent_performance()
