"""Domain specialist agents for IT, Supply Chain, and Banking."""

import re
from typing import Any

from app.data.mock_data import INVENTORY, PRODUCT_CATALOG
from app.schemas.agent_schema import DomainAction, DomainAgentResult
from app.schemas.workflow_schema import WorkflowType
from app.utils.llm_helper import call_llm_json, detect_keywords


async def run_domain_agent(
    request_text: str,
    workflow_type: WorkflowType,
    context_chunks: list[str],
) -> DomainAgentResult:
    if workflow_type == WorkflowType.IT_HELPDESK:
        return await _it_helpdesk_agent(request_text, context_chunks)
    if workflow_type == WorkflowType.SUPPLY_CHAIN_ORDER:
        return await _supply_chain_agent(request_text, context_chunks)
    if workflow_type == WorkflowType.BANKING_SUPPORT:
        return await _banking_support_agent(request_text, context_chunks)
    return await _general_agent(request_text, context_chunks)


async def _it_helpdesk_agent(request_text: str, context_chunks: list[str]) -> DomainAgentResult:
    text = request_text.lower()
    if detect_keywords(text, ["vpn", "remote access"]):
        action = DomainAction(
            action_type="vpn_reset",
            tool_name="reset_mock_vpn_profile",
            parameters={"employee_id": "EMP-1042", "reason": request_text[:200]},
            summary="Reset VPN profile and require MFA re-enrollment",
        )
        analysis = "VPN connectivity issue detected. Per IT-VPN-SOP, resetting VPN profile."
    elif detect_keywords(text, ["password", "locked out", "login"]):
        action = DomainAction(
            action_type="create_ticket",
            tool_name="create_it_ticket",
            parameters={
                "title": "Password Reset Request",
                "description": request_text,
                "priority": "high",
                "category": "access",
            },
            summary="Create IT ticket for password reset",
        )
        analysis = "Password/access issue. Creating IT service desk ticket per IT-PASSWORD-SOP."
    else:
        action = DomainAction(
            action_type="create_ticket",
            tool_name="create_it_ticket",
            parameters={
                "title": "IT Support Request",
                "description": request_text,
                "priority": "medium",
                "category": "general",
            },
            summary="Create general IT support ticket",
        )
        analysis = "General IT issue routed to service desk."

    mock = {
        "domain": "IT_HELPDESK",
        "analysis": analysis,
        "proposed_action": action.model_dump(),
        "extracted_fields": {"issue_type": action.action_type},
        "confidence": 0.87,
    }
    return await call_llm_json(
        "You are an IT helpdesk specialist.",
        f"Request: {request_text}\nContext: {context_chunks[:2]}",
        DomainAgentResult,
        mock_response=mock,
    )


async def _supply_chain_agent(request_text: str, context_chunks: list[str]) -> DomainAgentResult:
    items = _extract_order_items(request_text)
    customer = _extract_customer(request_text)
    delivery = _extract_delivery_date(request_text)

    inventory_checks = []
    for item in items:
        sku = item.get("sku", "SKU-1001")
        inv = INVENTORY.get(sku, 0)
        inventory_checks.append({"sku": sku, "requested": item.get("quantity", 1), "available": inv})

    action = DomainAction(
        action_type="create_order",
        tool_name="create_supply_order",
        parameters={
            "customer_name": customer,
            "items": items,
            "delivery_date": delivery,
            "notes": request_text[:300],
        },
        summary=f"Create supply order for {customer} with {len(items)} item(s)",
    )

    mock = {
        "domain": "SUPPLY_CHAIN_ORDER",
        "analysis": f"Parsed order for {customer}. Inventory check: {inventory_checks}",
        "proposed_action": action.model_dump(),
        "extracted_fields": {
            "customer_name": customer,
            "items": items,
            "delivery_date": delivery,
            "inventory_checks": inventory_checks,
        },
        "confidence": 0.82,
    }
    return await call_llm_json(
        "You are a supply chain order specialist.",
        f"Request: {request_text}",
        DomainAgentResult,
        mock_response=mock,
    )


async def _banking_support_agent(request_text: str, context_chunks: list[str]) -> DomainAgentResult:
    text = request_text.lower()
    if detect_keywords(text, ["fraud", "suspicious", "unauthorized", "stolen"]):
        action = DomainAction(
            action_type="flag_account",
            tool_name="flag_account_for_review",
            parameters={
                "account_id": "ACC-78234",
                "reason": request_text[:200],
                "risk_level": "critical",
            },
            summary="Flag account for compliance review due to suspected fraud",
        )
        analysis = "High-risk fraud indicators detected. Account must be flagged per BANK-CARD-BLOCK policy."
    elif detect_keywords(text, ["refund", "dispute", "charge"]):
        action = DomainAction(
            action_type="create_case",
            tool_name="create_support_case",
            parameters={
                "customer_id": "CUST-5521",
                "case_type": "dispute",
                "description": request_text,
                "priority": "high",
            },
            summary="Create dispute support case — requires human approval for amounts > $500",
        )
        analysis = "Dispute/refund request. Per BANK-DISPUTE policy, human approval required."
    else:
        action = DomainAction(
            action_type="create_case",
            tool_name="create_support_case",
            parameters={
                "customer_id": "CUST-5521",
                "case_type": "general",
                "description": request_text,
                "priority": "medium",
            },
            summary="Create general banking support case",
        )
        analysis = "General banking inquiry routed to customer support."

    mock = {
        "domain": "BANKING_SUPPORT",
        "analysis": analysis,
        "proposed_action": action.model_dump(),
        "extracted_fields": {"case_type": action.action_type},
        "confidence": 0.79,
    }
    return await call_llm_json(
        "You are a cautious banking support specialist.",
        f"Request: {request_text}\nPolicies: {context_chunks[:2]}",
        DomainAgentResult,
        mock_response=mock,
    )


async def _general_agent(request_text: str, context_chunks: list[str]) -> DomainAgentResult:
    action = DomainAction(
        action_type="notify",
        tool_name="send_internal_notification",
        parameters={
            "recipient": "ops-team@company.com",
            "subject": "Enterprise Request",
            "body": request_text[:500],
        },
        summary="Route to operations team via internal notification",
    )
    mock = {
        "domain": "GENERAL_ENTERPRISE",
        "analysis": "General enterprise request — notifying operations team.",
        "proposed_action": action.model_dump(),
        "extracted_fields": {},
        "confidence": 0.7,
    }
    return await call_llm_json(
        "You are a general enterprise assistant.",
        request_text,
        DomainAgentResult,
        mock_response=mock,
    )


def _extract_order_items(text: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    qty_match = re.search(r"(\d+)\s*(units?|boxes?|packs?|each|meters?|cans?)?", text, re.I)
    qty = int(qty_match.group(1)) if qty_match else 10

    sku = "SKU-1001"
    for code, info in PRODUCT_CATALOG.items():
        if info["name"].lower().split()[0] in text.lower() or code.lower() in text.lower():
            sku = code
            break

    if detect_keywords(text, ["bearing"]):
        sku = "SKU-1001"
    elif detect_keywords(text, ["hose", "hydraulic"]):
        sku = "SKU-1002"
    elif detect_keywords(text, ["glove", "safety"]):
        sku = "SKU-1003"
    elif detect_keywords(text, ["bolt", "steel"]):
        sku = "SKU-1004"
    elif detect_keywords(text, ["conveyor", "belt"]):
        sku = "SKU-1005"

    product = PRODUCT_CATALOG.get(sku, {})
    items.append({
        "sku": sku,
        "name": product.get("name", "Item"),
        "quantity": qty,
        "unit": product.get("unit", "each"),
    })
    return items


def _extract_customer(text: str) -> str:
    match = re.search(r"(?:for|customer|client)\s+([A-Z][a-zA-Z\s&]+?)(?:\.|,|$|\n)", text)
    if match:
        return match.group(1).strip()
    return "Acme Industries"


def _extract_delivery_date(text: str) -> str:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if match:
        return match.group(1)
    match = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}", text, re.I)
    if match:
        return match.group(0)
    return "2026-07-01"
