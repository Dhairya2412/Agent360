"""MongoDB connection and lifecycle management."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None
_connected: bool = False


async def connect_mongo() -> AsyncIOMotorDatabase | None:
    global _client, _db, _connected
    settings = get_settings()
    _connected = False
    try:
        _client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        await _client.admin.command("ping")
        _db = _client[settings.mongodb_database]
        _connected = True
        logger.info("Connected to MongoDB: %s", settings.mongodb_database)
        return _db
    except Exception as exc:
        err = str(exc)
        if settings.mongodb_required or settings.is_production:
            logger.error("MongoDB connection required but failed: %s", exc)
            raise RuntimeError(f"MongoDB connection failed: {exc}") from exc
        if "bad auth" in err.lower() or "authentication failed" in err.lower():
            logger.warning(
                "MongoDB authentication failed — check MONGODB_URI. Using in-memory fallback."
            )
        else:
            logger.warning("MongoDB connection failed: %s — using in-memory fallback", exc)
        _db = None
        return None


async def disconnect_mongo() -> None:
    global _client, _db, _connected
    if _client:
        _client.close()
        _client = None
        _db = None
        _connected = False
        logger.info("Disconnected from MongoDB")


def get_database() -> AsyncIOMotorDatabase | None:
    return _db


def is_mongo_connected() -> bool:
    return _connected and _db is not None


async def ping_mongo() -> bool:
    if not _client:
        return False
    try:
        await _client.admin.command("ping")
        return True
    except Exception:
        return False
