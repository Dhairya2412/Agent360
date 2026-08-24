"""Mock IT helpdesk tools — no real external API calls."""

from datetime import datetime, timezone
from uuid import uuid4


def create_it_ticket(title: str, description: str, priority: str = "medium", category: str = "general") -> dict:
    return {
        "ticket_id": f"IT-{uuid4().hex[:8].upper()}",
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "assigned_team": "IT Service Desk",
    }


def reset_mock_vpn_profile(employee_id: str, reason: str) -> dict:
    return {
        "employee_id": employee_id,
        "vpn_profile_reset": True,
        "mfa_reenrollment_required": True,
        "reset_token": f"VPN-{uuid4().hex[:6].upper()}",
        "reason": reason,
        "status": "completed",
        "message": "VPN profile reset successfully. User must re-enroll MFA within 24 hours.",
    }


def send_internal_notification(recipient: str, subject: str, body: str) -> dict:
    return {
        "notification_id": f"NOTIF-{uuid4().hex[:8]}",
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "status": "delivered",
    }
