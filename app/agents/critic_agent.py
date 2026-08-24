"""Critic / QA agent — validates grounding, completeness, and risk."""

from app.schemas.agent_schema import CriticResult, QAStatus
from app.schemas.workflow_schema import RiskLevel, WorkflowType
from app.utils.llm_helper import call_llm_json


async def critic_check(
    request_text: str,
    workflow_type: WorkflowType,
    domain_result: dict,
    retrieval_result: dict,
) -> CriticResult:
    proposed = domain_result.get("proposed_action", {})
    tool_name = proposed.get("tool_name", "")
    extracted = domain_result.get("extracted_fields", {})
    missing: list[str] = []
    requires_approval = False
    hallucination_risk = RiskLevel.LOW
    qa_status = QAStatus.PASS
    reason_parts: list[str] = []

    # Banking always needs extra scrutiny
    if workflow_type == WorkflowType.BANKING_SUPPORT:
        requires_approval = True
        hallucination_risk = RiskLevel.MEDIUM
        reason_parts.append("Banking workflows require human approval per compliance policy")

    if tool_name == "flag_account_for_review":
        requires_approval = True
        hallucination_risk = RiskLevel.HIGH
        qa_status = QAStatus.WARN
        reason_parts.append("Account flagging is a high-risk action")

    if workflow_type == WorkflowType.SUPPLY_CHAIN_ORDER:
        items = extracted.get("items", [])
        if not items:
            missing.append("order_items")
            qa_status = QAStatus.WARN
        inv_checks = extracted.get("inventory_checks", [])
        for check in inv_checks:
            if check.get("requested", 0) > check.get("available", 0):
                requires_approval = True
                reason_parts.append(f"Insufficient inventory for {check.get('sku')}")

    if retrieval_result.get("fallback_used"):
        reason_parts.append("Used fallback SOP data — no uploaded documents matched")

    if not proposed.get("tool_name"):
        missing.append("tool_name")
        qa_status = QAStatus.FAIL
        requires_approval = True

    confidence = domain_result.get("confidence", 0.75)
    if confidence < 0.7:
        requires_approval = True
        qa_status = QAStatus.WARN
        reason_parts.append("Low domain agent confidence")

    mock = {
        "qa_status": qa_status.value,
        "hallucination_risk": hallucination_risk.value,
        "missing_fields": missing,
        "requires_human_approval": requires_approval,
        "confidence_score": round(confidence, 2),
        "reason": "; ".join(reason_parts) if reason_parts else "QA checks passed",
    }

    return await call_llm_json(
        "You are a QA critic agent. Check grounding, missing fields, and risk.",
        f"Request: {request_text}\nDomain: {domain_result}\nRetrieval: {retrieval_result}",
        CriticResult,
        mock_response=mock,
    )
