"""Human approval service — approve, reject, edit-and-approve flows."""

from typing import Any, Optional

from app.agents.audit_agent import log_audit_entry
from app.agents.tool_agent import execute_tool_action
from app.database.repositories import approval_repo, workflow_repo
from app.schemas.workflow_schema import WorkflowStatus


class ApprovalService:
    async def list_pending(self) -> list[dict[str, Any]]:
        return await approval_repo.list_pending()

    async def approve(self, approval_id: str) -> dict[str, Any]:
        approval = await approval_repo.get(approval_id)
        if not approval:
            raise ValueError("Approval not found")
        if approval.get("status") != "pending":
            raise ValueError("Approval already processed")

        proposed = approval.get("proposed_action", {})
        tool_name = proposed.get("tool_name", "")
        params = proposed.get("parameters", {})

        tool_result = await execute_tool_action(tool_name, params)

        await approval_repo.update(approval_id, {"status": "approved"})
        workflow_id = approval.get("workflow_id", "")

        final = f"Approved and executed '{tool_name}'. Result: {tool_result.result}"
        await workflow_repo.update(workflow_id, {
            "status": WorkflowStatus.COMPLETED.value if tool_result.success else WorkflowStatus.FAILED.value,
            "final_response": final,
            "tool_result": tool_result.model_dump(),
        })

        await log_audit_entry(
            workflow_id,
            approval.get("workflow_type", ""),
            "human_approval",
            "approved",
            tool_executed=tool_name,
            human_approval_required=True,
            details={"approval_id": approval_id, "tool_result": tool_result.model_dump()},
        )

        return {"approval": await approval_repo.get(approval_id), "tool_result": tool_result.model_dump()}

    async def reject(self, approval_id: str, reason: str = "Rejected by admin") -> dict[str, Any]:
        approval = await approval_repo.get(approval_id)
        if not approval:
            raise ValueError("Approval not found")

        await approval_repo.update(approval_id, {"status": "rejected", "rejection_reason": reason})
        workflow_id = approval.get("workflow_id", "")

        await workflow_repo.update(workflow_id, {
            "status": WorkflowStatus.REJECTED.value,
            "final_response": f"Rejected: {reason}",
        })

        await log_audit_entry(
            workflow_id,
            approval.get("workflow_type", ""),
            "human_approval",
            "rejected",
            human_approval_required=True,
            details={"approval_id": approval_id, "reason": reason},
        )

        return await approval_repo.get(approval_id)  # type: ignore

    async def edit_and_approve(self, approval_id: str, edited_action: dict[str, Any], notes: str = "") -> dict[str, Any]:
        approval = await approval_repo.get(approval_id)
        if not approval:
            raise ValueError("Approval not found")

        tool_name = edited_action.get("tool_name", "")
        params = edited_action.get("parameters", {})
        tool_result = await execute_tool_action(tool_name, params)

        await approval_repo.update(approval_id, {
            "status": "approved",
            "edited_action": edited_action,
            "notes": notes,
        })

        workflow_id = approval.get("workflow_id", "")
        final = f"Edited and approved. Executed '{tool_name}'. Notes: {notes}"
        await workflow_repo.update(workflow_id, {
            "status": WorkflowStatus.COMPLETED.value if tool_result.success else WorkflowStatus.FAILED.value,
            "final_response": final,
            "tool_result": tool_result.model_dump(),
        })

        await log_audit_entry(
            workflow_id,
            approval.get("workflow_type", ""),
            "human_approval",
            "edit_approved",
            tool_executed=tool_name,
            human_approval_required=True,
            details={"edited_action": edited_action, "notes": notes},
        )

        return {"approval": await approval_repo.get(approval_id), "tool_result": tool_result.model_dump()}


approval_service = ApprovalService()
