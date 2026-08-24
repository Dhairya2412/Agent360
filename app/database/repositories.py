"""MongoDB + in-memory repository layer for all collections."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.memory_store import get_memory_store, new_id
from app.database.mongo import get_database


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _oid_str(doc: dict[str, Any]) -> dict[str, Any]:
    if doc and "_id" in doc:
        doc = {**doc, "id": str(doc["_id"])}
        del doc["_id"]
    return doc


class WorkflowRepository:
    COLLECTION = "workflow_runs"

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        db = get_database()
        data = {**data, "created_at": _now(), "updated_at": _now()}
        if db is not None:
            result = await db[self.COLLECTION].insert_one(data)
            data["_id"] = result.inserted_id
            return _oid_str(data)
        store = get_memory_store()
        wid = new_id()
        data["id"] = wid
        store.workflows[wid] = data
        return data

    async def get(self, workflow_id: str) -> Optional[dict[str, Any]]:
        db = get_database()
        if db is not None:
            doc = await db[self.COLLECTION].find_one({"_id": ObjectId(workflow_id)} if ObjectId.is_valid(workflow_id) else {"id": workflow_id})
            if not doc and ObjectId.is_valid(workflow_id):
                doc = await db[self.COLLECTION].find_one({"id": workflow_id})
            return _oid_str(doc) if doc else None
        return get_memory_store().workflows.get(workflow_id)

    async def list_all(self, limit: int = 50, skip: int = 0) -> list[dict[str, Any]]:
        db = get_database()
        if db is not None:
            cursor = db[self.COLLECTION].find().sort("created_at", -1).skip(skip).limit(limit)
            return [_oid_str(d) async for d in cursor]
        items = sorted(get_memory_store().workflows.values(), key=lambda x: x.get("created_at", ""), reverse=True)
        return items[skip : skip + limit]

    async def update(self, workflow_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        updates["updated_at"] = _now()
        db = get_database()
        if db is not None:
            filt = {"_id": ObjectId(workflow_id)} if ObjectId.is_valid(workflow_id) else {"id": workflow_id}
            await db[self.COLLECTION].update_one(filt, {"$set": updates})
            return await self.get(workflow_id)
        store = get_memory_store()
        if workflow_id in store.workflows:
            store.workflows[workflow_id].update(updates)
            return store.workflows[workflow_id]
        return None

    async def count(self, filt: Optional[dict] = None) -> int:
        db = get_database()
        filt = filt or {}
        if db is not None:
            return await db[self.COLLECTION].count_documents(filt)
        store = get_memory_store()
        if not filt:
            return len(store.workflows)
        return sum(1 for w in store.workflows.values() if all(w.get(k) == v for k, v in filt.items()))


class ApprovalRepository:
    COLLECTION = "approvals"

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        data = {**data, "status": "pending", "created_at": _now(), "updated_at": _now()}
        db = get_database()
        if db is not None:
            result = await db[self.COLLECTION].insert_one(data)
            data["_id"] = result.inserted_id
            return _oid_str(data)
        aid = new_id()
        data["id"] = aid
        get_memory_store().approvals[aid] = data
        return data

    async def get(self, approval_id: str) -> Optional[dict[str, Any]]:
        db = get_database()
        if db is not None:
            doc = await db[self.COLLECTION].find_one(
                {"_id": ObjectId(approval_id)} if ObjectId.is_valid(approval_id) else {"id": approval_id}
            )
            return _oid_str(doc) if doc else None
        return get_memory_store().approvals.get(approval_id)

    async def list_pending(self) -> list[dict[str, Any]]:
        db = get_database()
        if db is not None:
            cursor = db[self.COLLECTION].find({"status": "pending"}).sort("created_at", -1)
            return [_oid_str(d) async for d in cursor]
        return [a for a in get_memory_store().approvals.values() if a.get("status") == "pending"]

    async def update(self, approval_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        updates["updated_at"] = _now()
        db = get_database()
        if db is not None:
            filt = {"_id": ObjectId(approval_id)} if ObjectId.is_valid(approval_id) else {"id": approval_id}
            await db[self.COLLECTION].update_one(filt, {"$set": updates})
            return await self.get(approval_id)
        store = get_memory_store()
        if approval_id in store.approvals:
            store.approvals[approval_id].update(updates)
            return store.approvals[approval_id]
        return None


class AuditRepository:
    COLLECTION = "audit_logs"

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        data = {**data, "created_at": _now()}
        db = get_database()
        if db is not None:
            result = await db[self.COLLECTION].insert_one(data)
            data["_id"] = result.inserted_id
            return _oid_str(data)
        data["id"] = new_id()
        get_memory_store().audit_logs.append(data)
        return data

    async def list_all(self, workflow_id: Optional[str] = None, limit: int = 100) -> list[dict[str, Any]]:
        db = get_database()
        filt = {"workflow_id": workflow_id} if workflow_id else {}
        if db is not None:
            cursor = db[self.COLLECTION].find(filt).sort("created_at", -1).limit(limit)
            return [_oid_str(d) async for d in cursor]
        logs = get_memory_store().audit_logs
        if workflow_id:
            logs = [l for l in logs if l.get("workflow_id") == workflow_id]
        return sorted(logs, key=lambda x: x.get("created_at", ""), reverse=True)[:limit]


class DocumentRepository:
    COLLECTION = "uploaded_documents"

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        data = {**data, "created_at": _now()}
        db = get_database()
        if db is not None:
            result = await db[self.COLLECTION].insert_one(data)
            data["_id"] = result.inserted_id
            return _oid_str(data)
        did = new_id()
        data["id"] = did
        get_memory_store().documents[did] = data
        return data

    async def list_all(self) -> list[dict[str, Any]]:
        db = get_database()
        if db is not None:
            cursor = db[self.COLLECTION].find().sort("created_at", -1)
            return [_oid_str(d) async for d in cursor]
        return list(get_memory_store().documents.values())

    async def get(self, document_id: str) -> Optional[dict[str, Any]]:
        db = get_database()
        if db is not None:
            doc = await db[self.COLLECTION].find_one(
                {"_id": ObjectId(document_id)} if ObjectId.is_valid(document_id) else {"id": document_id}
            )
            return _oid_str(doc) if doc else None
        return get_memory_store().documents.get(document_id)

    async def delete(self, document_id: str) -> bool:
        db = get_database()
        if db is not None:
            filt = {"_id": ObjectId(document_id)} if ObjectId.is_valid(document_id) else {"id": document_id}
            result = await db[self.COLLECTION].delete_one(filt)
            return result.deleted_count > 0
        store = get_memory_store()
        if document_id in store.documents:
            del store.documents[document_id]
            return True
        return False


class TraceRepository:
    COLLECTION = "agent_traces"

    async def add(self, workflow_id: str, trace: dict[str, Any]) -> None:
        trace = {**trace, "workflow_id": workflow_id, "created_at": _now()}
        db = get_database()
        if db is not None:
            await db[self.COLLECTION].insert_one(trace)
            return
        store = get_memory_store()
        store.agent_traces.setdefault(workflow_id, []).append(trace)

    async def list_for_workflow(self, workflow_id: str) -> list[dict[str, Any]]:
        db = get_database()
        if db is not None:
            cursor = db[self.COLLECTION].find({"workflow_id": workflow_id}).sort("created_at", 1)
            return [_oid_str(d) async for d in cursor]
        return get_memory_store().agent_traces.get(workflow_id, [])


workflow_repo = WorkflowRepository()
approval_repo = ApprovalRepository()
audit_repo = AuditRepository()
document_repo = DocumentRepository()
trace_repo = TraceRepository()
