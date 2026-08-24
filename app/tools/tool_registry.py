"""Allowlisted tool registry — only registered tools can execute."""

from typing import Any, Callable

from app.tools.mock_banking_tools import create_support_case, flag_account_for_review
from app.tools.mock_it_tools import create_it_ticket, reset_mock_vpn_profile, send_internal_notification
from app.tools.mock_supply_tools import check_inventory, create_supply_order

# Security: tools must be explicitly registered — no free-form execution
TOOL_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "create_it_ticket": create_it_ticket,
    "reset_mock_vpn_profile": reset_mock_vpn_profile,
    "send_internal_notification": send_internal_notification,
    "create_supply_order": create_supply_order,
    "check_inventory": check_inventory,
    "create_support_case": create_support_case,
    "flag_account_for_review": flag_account_for_review,
}


def is_allowed_tool(tool_name: str) -> bool:
    return tool_name in TOOL_REGISTRY


def execute_tool(tool_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
    if not is_allowed_tool(tool_name):
        raise ValueError(f"Tool '{tool_name}' is not in the allowlist")
    fn = TOOL_REGISTRY[tool_name]
    return fn(**parameters)


def list_tools() -> list[str]:
    return list(TOOL_REGISTRY.keys())
