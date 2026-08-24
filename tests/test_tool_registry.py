"""Tests for tool registry allowlist."""

import pytest

from app.tools.tool_registry import TOOL_REGISTRY, execute_tool, is_allowed_tool, list_tools


def test_all_tools_registered():
    expected = {
        "create_it_ticket",
        "reset_mock_vpn_profile",
        "send_internal_notification",
        "create_supply_order",
        "check_inventory",
        "create_support_case",
        "flag_account_for_review",
    }
    assert set(list_tools()) == expected


def test_is_allowed_tool():
    assert is_allowed_tool("create_it_ticket") is True
    assert is_allowed_tool("delete_database") is False


def test_execute_allowed_tool():
    result = execute_tool("create_it_ticket", {
        "title": "Test",
        "description": "Test ticket",
        "priority": "low",
    })
    assert "ticket_id" in result
    assert result["status"] == "open"


def test_execute_disallowed_tool():
    with pytest.raises(ValueError, match="not in the allowlist"):
        execute_tool("rm_rf_everything", {})


def test_check_inventory():
    result = execute_tool("check_inventory", {"sku": "SKU-1001"})
    assert result["sku"] == "SKU-1001"
    assert "available_quantity" in result
