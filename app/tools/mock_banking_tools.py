"""Mock banking support tools."""

from datetime import datetime, timezone
from uuid import uuid4


def create_support_case(
    customer_id: str,
    case_type: str,
    description: str,
    priority: str = "medium",
) -> dict:
    return {
        "case_id": f"BANK-{uuid4().hex[:8].upper()}",
        "customer_id": customer_id,
        "case_type": case_type,
        "description": description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "assigned_team": "Customer Support",
    }


def flag_account_for_review(account_id: str, reason: str, risk_level: str = "high") -> dict:
    return {
        "account_id": account_id,
        "flag_id": f"FLAG-{uuid4().hex[:8]}",
        "reason": reason,
        "risk_level": risk_level,
        "status": "flagged",
        "review_required": True,
        "flagged_at": datetime.now(timezone.utc).isoformat(),
        "message": "Account flagged for compliance review. No automated transactions until cleared.",
    }
