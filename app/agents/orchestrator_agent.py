"""Orchestrator agent — classifies incoming requests into workflow types."""

from app.schemas.agent_schema import ClassificationResult
from app.schemas.workflow_schema import WorkflowType
from app.utils.llm_helper import call_llm_json, detect_keywords


async def classify_request(request_text: str, hint_type: WorkflowType = WorkflowType.AUTO_DETECT) -> ClassificationResult:
    if hint_type != WorkflowType.AUTO_DETECT:
        return ClassificationResult(
            workflow_type=hint_type,
            confidence=0.95,
            reasoning=f"User selected workflow type: {hint_type.value}",
        )

    # Deterministic keyword classification for MOCK_MODE
    text = request_text.lower()
    if detect_keywords(text, ["vpn", "password", "mfa", "laptop", "email", "software", "hardware", "ticket", "login"]):
        wf = WorkflowType.IT_HELPDESK
        reasoning = "Detected IT helpdesk keywords (VPN, password, MFA, hardware, etc.)"
    elif detect_keywords(text, ["order", "inventory", "sku", "delivery", "supply", "shipment", "warehouse", "bearing", "bolt"]):
        wf = WorkflowType.SUPPLY_CHAIN_ORDER
        reasoning = "Detected supply chain keywords (order, inventory, SKU, delivery)"
    elif detect_keywords(text, ["card", "bank", "account", "transaction", "refund", "dispute", "fraud", "blocked", "charge"]):
        wf = WorkflowType.BANKING_SUPPORT
        reasoning = "Detected banking support keywords (card, account, transaction, refund)"
    else:
        wf = WorkflowType.GENERAL_ENTERPRISE
        reasoning = "No specific domain keywords detected; routing to general enterprise workflow"

    mock = {
        "workflow_type": wf.value,
        "confidence": 0.88,
        "reasoning": reasoning,
    }

    return await call_llm_json(
        system_prompt="You are an enterprise workflow orchestrator. Classify requests into IT_HELPDESK, SUPPLY_CHAIN_ORDER, BANKING_SUPPORT, or GENERAL_ENTERPRISE.",
        user_prompt=f"Classify this request:\n{request_text}",
        response_model=ClassificationResult,
        mock_response=mock,
    )
