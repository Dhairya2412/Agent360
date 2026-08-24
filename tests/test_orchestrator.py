"""Tests for orchestrator keyword classification."""

import pytest

from app.agents.orchestrator_agent import classify_request
from app.schemas.workflow_schema import WorkflowType


@pytest.mark.asyncio
async def test_classify_it_helpdesk():
    result = await classify_request("My VPN is broken and I can't login with MFA")
    assert result.workflow_type == WorkflowType.IT_HELPDESK


@pytest.mark.asyncio
async def test_classify_supply_chain():
    result = await classify_request("Order 100 bearings for delivery next week")
    assert result.workflow_type == WorkflowType.SUPPLY_CHAIN_ORDER


@pytest.mark.asyncio
async def test_classify_banking():
    result = await classify_request("Customer card blocked due to suspicious transaction")
    assert result.workflow_type == WorkflowType.BANKING_SUPPORT


@pytest.mark.asyncio
async def test_explicit_workflow_type():
    result = await classify_request("anything", WorkflowType.IT_HELPDESK)
    assert result.workflow_type == WorkflowType.IT_HELPDESK
    assert result.confidence >= 0.9
