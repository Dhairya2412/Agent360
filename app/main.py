"""AgentOps360 FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics_routes import router as analytics_router
from app.api.approval_routes import router as approval_router
from app.api.audit_routes import router as audit_router
from app.api.document_routes import router as document_router
from app.api.workflow_routes import router as workflow_router
from app.config import get_settings
from app.database.mongo import connect_mongo, disconnect_mongo, is_mongo_connected, ping_mongo
from app.data.seed import seed_demo_data
from app.middleware.request_middleware import RequestIdMiddleware, global_exception_handler
from app.utils.logger import configure_logging, get_logger
from app.vectorstore.chroma_client import get_chroma_status

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    if settings.mock_mode:
        logger.info("MOCK_MODE=true — using deterministic agent outputs (no OpenAI calls)")
    elif not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY not set — set MOCK_MODE=true or provide a valid key")

    logger.info("Starting %s [%s]", settings.app_name, settings.environment)

    await connect_mongo()

    if settings.seed_demo_data:
        await seed_demo_data()
    else:
        logger.info("Demo seeding disabled (SEED_DEMO_DATA=false)")

    chroma_status = get_chroma_status()
    if chroma_status.get("connected"):
        logger.info("Chroma ready — mode=%s docs=%s", chroma_status.get("mode"), chroma_status.get("document_count"))
    elif settings.chroma_use_cloud:
        logger.error("Chroma Cloud connection failed: %s", chroma_status.get("error"))

    yield
    await disconnect_mongo()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=f"{settings.app_name} API",
        description="Multi-agent enterprise workflow automation platform",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    app.add_middleware(RequestIdMiddleware)
    app.add_exception_handler(Exception, global_exception_handler)

    app.include_router(workflow_router)
    app.include_router(approval_router)
    app.include_router(document_router)
    app.include_router(audit_router)
    app.include_router(analytics_router)

    @app.get("/api/health/live")
    async def liveness():
        return {"status": "alive", "service": "agentops360-backend"}

    @app.get("/api/health")
    async def readiness(response: Response):
        settings = get_settings()
        chroma = get_chroma_status()
        mongo_ok = await ping_mongo() if is_mongo_connected() else not settings.mongodb_required

        chroma_ok = chroma.get("connected", False)
        if not settings.chroma_use_cloud:
            chroma_ok = chroma.get("connected", False) or chroma.get("mode") == "local"

        healthy = mongo_ok and chroma_ok
        if not healthy:
            response.status_code = 503

        return {
            "status": "healthy" if healthy else "degraded",
            "environment": settings.environment,
            "mock_mode": settings.mock_mode,
            "service": "agentops360-backend",
            "version": settings.app_version,
            "mongodb": {"connected": is_mongo_connected(), "ping": mongo_ok},
            "chroma": chroma,
        }

    return app


app = create_app()
