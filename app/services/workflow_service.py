"""Workflow execution service."""

import time
from typing import Any, Optional

from app.database.repositories import trace_repo, workflow_repo
from app.schemas.workflow_schema import WorkflowStartRequest, WorkflowStatus
from app.workflows.enterprise_graph import enterprise_graph


class WorkflowService:
    async def start_workflow(self, request: WorkflowStartRequest) -> dict[str, Any]:
        record = await workflow_repo.create({
            "workflow_type": request.workflow_type.value,
            "request_text": request.request_text,
            "status": WorkflowStatus.RUNNING.value,
            "document_ids": request.document_ids,
            "agent_traces": [],
            "tool_calls": [],
        })

        workflow_id = record.get("id") or str(record.get("_id", ""))

        initial_state = {
            "workflow_id": workflow_id,
            "request_text": request.request_text,
            "workflow_type_hint": request.workflow_type.value,
            "status": WorkflowStatus.RUNNING.value,
            "agent_traces": [],
            "started_at": time.perf_counter(),
        }

        try:
            final_state = await enterprise_graph.ainvoke(initial_state)
        except Exception as exc:
            await workflow_repo.update(workflow_id, {
                "status": WorkflowStatus.FAILED.value,
                "final_response": f"Workflow failed: {exc}",
            })
            raise

        # Persist traces
        for trace in final_state.get("agent_traces", []):
            await trace_repo.add(workflow_id, trace)

        updated = await workflow_repo.update(workflow_id, {
            "workflow_type": final_state.get("workflow_type", request.workflow_type.value),
            "status": final_state.get("status", WorkflowStatus.COMPLETED.value),
            "final_response": final_state.get("final_response"),
            "classification": final_state.get("classification"),
            "plan": final_state.get("plan"),
            "retrieval": final_state.get("retrieval"),
            "domain_result": final_state.get("domain_result"),
            "critic_result": final_state.get("critic_result"),
            "tool_result": final_state.get("tool_result"),
            "approval_id": final_state.get("approval_id"),
            "requires_approval": final_state.get("requires_approval", False),
            "confidence_score": final_state.get("critic_result", {}).get("confidence_score"),
            "risk_level": final_state.get("critic_result", {}).get("hallucination_risk"),
            "total_latency_ms": final_state.get("total_latency_ms"),
        })

        return updated or record

    async def get_workflow(self, workflow_id: str) -> Optional[dict[str, Any]]:
        wf = await workflow_repo.get(workflow_id)
        if wf:
            traces = await trace_repo.list_for_workflow(workflow_id)
            wf["agent_traces"] = traces
        return wf

    async def list_workflows(self, limit: int = 50) -> list[dict[str, Any]]:
        return await workflow_repo.list_all(limit=limit)

    async def retry_workflow(self, workflow_id: str) -> Optional[dict[str, Any]]:
        wf = await workflow_repo.get(workflow_id)
        if not wf:
            return None
        from app.schemas.workflow_schema import WorkflowType

        request = WorkflowStartRequest(
            workflow_type=WorkflowType(wf.get("workflow_type", "AUTO_DETECT")),
            request_text=wf.get("request_text", ""),
        )
        return await self.start_workflow(request)


workflow_service = WorkflowService()
