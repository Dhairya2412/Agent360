"""In-memory fallback store when MongoDB is unavailable."""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _now() -> datetime:
    return datetime.now(timezone.utc)


class InMemoryStore:
    """Simple dict-backed store for local dev without Atlas."""

    def __init__(self) -> None:
        self.workflows: dict[str, dict[str, Any]] = {}
        self.approvals: dict[str, dict[str, Any]] = {}
        self.audit_logs: list[dict[str, Any]] = []
        self.documents: dict[str, dict[str, Any]] = {}
        self.agent_traces: dict[str, list[dict[str, Any]]] = {}
        self.tool_calls: dict[str, list[dict[str, Any]]] = {}


_memory = InMemoryStore()


def get_memory_store() -> InMemoryStore:
    return _memory


def new_id() -> str:
    return str(uuid4())


def serialize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(doc)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    elif "id" not in result and "workflow_id" not in result:
        pass
    for key, val in list(result.items()):
        if isinstance(val, datetime):
            result[key] = val.isoformat()
    return result
