"""Seed demo workflows, approvals, and audit logs for portfolio demo."""

from datetime import datetime, timedelta, timezone

from app.database.memory_store import get_memory_store
from app.database.repositories import approval_repo, audit_repo, workflow_repo

_seeded = False


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def seed_demo_data() -> None:
    global _seeded
    if _seeded:
        return

    existing = await workflow_repo.count()
    if existing > 0:
        _seeded = True
        return

    store = get_memory_store()
    if len(store.workflows) > 0:
        _seeded = True
        return

    it_requests = [
        "My VPN keeps disconnecting every 10 minutes, can't access internal tools",
        "Locked out of my account, password reset not working after MFA change",
        "Need access to Figma and Jira for the new product team",
        "Laptop fan is extremely loud and overheating during video calls",
        "Corporate email not syncing on mobile after iOS update",
    ]

    supply_requests = [
        "Order 200 units of Industrial Bearing 6205 for Acme Industries, delivery by 2026-07-15",
        "Need 50 boxes of Safety Gloves for warehouse team, deliver ASAP",
        "Place order for 15 Conveyor Belt Segments for MegaCorp, delivery 2026-08-01",
        "Urgent: 500 Steel Bolt M12x50 packs for construction site",
        "Order 100 cans of Lubricant Oil 5L for maintenance dept",
    ]

    banking_requests = [
        "Customer reports unauthorized $2,400 charge from overseas merchant — possible fraud",
        "Card blocked after 3 failed PIN attempts, customer needs immediate unblock",
        "Refund dispute for $750 double charge at electronics store",
        "Account shows suspicious wire transfer to unknown beneficiary",
        "Customer wants to dispute a $1,200 subscription charge they didn't authorize",
    ]

    base_time = _now()
    workflow_ids: list[str] = []

    for i, req in enumerate(it_requests):
        wf = await workflow_repo.create({
            "workflow_type": "IT_HELPDESK",
            "request_text": req,
            "status": "completed" if i < 4 else "failed",
            "final_response": f"IT ticket created and resolved for: {req[:50]}...",
            "confidence_score": 0.85 + (i * 0.02),
            "risk_level": "low",
            "total_latency_ms": 1200 + i * 200,
            "created_at": base_time - timedelta(hours=i + 1),
        })
        workflow_ids.append(wf.get("id", ""))
        await audit_repo.create({
            "workflow_id": wf.get("id"),
            "workflow_type": "IT_HELPDESK",
            "agent_name": "audit",
            "status": "completed",
            "confidence_score": 0.87,
            "human_approval_required": False,
            "tool_executed": "create_it_ticket",
        })

    for i, req in enumerate(supply_requests):
        wf = await workflow_repo.create({
            "workflow_type": "SUPPLY_CHAIN_ORDER",
            "request_text": req,
            "status": "completed" if i != 2 else "awaiting_approval",
            "final_response": f"Supply order processed: {req[:50]}...",
            "confidence_score": 0.80 + (i * 0.02),
            "risk_level": "medium",
            "total_latency_ms": 1800 + i * 150,
            "created_at": base_time - timedelta(hours=i + 6),
        })
        workflow_ids.append(wf.get("id", ""))
        if i == 2:
            await approval_repo.create({
                "workflow_id": wf.get("id"),
                "workflow_type": "SUPPLY_CHAIN_ORDER",
                "proposed_action": {
                    "tool_name": "create_supply_order",
                    "parameters": {"customer_name": "MegaCorp", "items": [{"sku": "SKU-1005", "quantity": 15}], "delivery_date": "2026-08-01"},
                    "summary": "Large conveyor belt order — low inventory",
                },
                "risk_level": "medium",
                "reason": "Insufficient inventory for SKU-1005 (12 available, 15 requested)",
                "agent_reasoning": "Inventory check shows backorder required for 3 units",
            })

    for i, req in enumerate(banking_requests):
        status = "awaiting_approval" if i in (0, 2, 4) else "completed"
        wf = await workflow_repo.create({
            "workflow_type": "BANKING_SUPPORT",
            "request_text": req,
            "status": status,
            "final_response": f"Banking case handled: {req[:50]}..." if status == "completed" else "Pending human approval",
            "confidence_score": 0.75 + (i * 0.02),
            "risk_level": "high" if i in (0, 3) else "medium",
            "total_latency_ms": 2200 + i * 180,
            "requires_approval": status == "awaiting_approval",
            "created_at": base_time - timedelta(hours=i + 12),
        })
        workflow_ids.append(wf.get("id", ""))

        if status == "awaiting_approval":
            await approval_repo.create({
                "workflow_id": wf.get("id"),
                "workflow_type": "BANKING_SUPPORT",
                "proposed_action": {
                    "tool_name": "flag_account_for_review" if i == 0 else "create_support_case",
                    "parameters": {"account_id": "ACC-78234", "reason": req[:100], "risk_level": "critical"},
                    "summary": "High-risk banking action requires approval",
                },
                "risk_level": "high",
                "reason": "Banking compliance requires human approval for fraud/dispute actions",
                "agent_reasoning": "Detected high-risk financial indicators per BANK-DISPUTE policy",
            })

        await audit_repo.create({
            "workflow_id": wf.get("id"),
            "workflow_type": "BANKING_SUPPORT",
            "agent_name": "critic",
            "status": status,
            "confidence_score": 0.78,
            "human_approval_required": status == "awaiting_approval",
            "tool_executed": None if status == "awaiting_approval" else "create_support_case",
        })

    _seeded = True
