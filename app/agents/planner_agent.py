"""Planner agent — produces structured execution plans."""

from app.schemas.agent_schema import PlannerResult, PlanStep
from app.schemas.workflow_schema import RiskLevel, WorkflowType
from app.utils.llm_helper import call_llm_json


async def plan_workflow(request_text: str, workflow_type: WorkflowType) -> PlannerResult:
    risk = RiskLevel.LOW
    if workflow_type == WorkflowType.BANKING_SUPPORT:
        risk = RiskLevel.HIGH
    elif workflow_type == WorkflowType.SUPPLY_CHAIN_ORDER:
        risk = RiskLevel.MEDIUM

    steps = [
        PlanStep(step_number=1, agent="retrieval", action="Retrieve relevant SOPs and policies", expected_output="Context chunks"),
        PlanStep(step_number=2, agent="domain", action=f"Run {workflow_type.value} specialist", expected_output="Proposed action"),
        PlanStep(step_number=3, agent="critic", action="QA and risk check", expected_output="Approval decision"),
        PlanStep(step_number=4, agent="tool", action="Execute approved mock tool", expected_output="Tool result"),
        PlanStep(step_number=5, agent="audit", action="Log complete trace", expected_output="Audit entry"),
    ]

    mock = {
        "workflow_type": workflow_type.value,
        "required_agents": ["retrieval", "domain", "critic", "tool", "audit"],
        "steps": [s.model_dump() for s in steps],
        "risk_level": risk.value,
        "expected_outputs": ["context", "domain_analysis", "qa_result", "tool_result", "audit_log"],
        "reasoning": f"Standard {workflow_type.value} workflow with retrieval, domain analysis, QA gate, and tool execution.",
    }

    return await call_llm_json(
        system_prompt="You are a workflow planner for enterprise automation. Produce structured JSON plans.",
        user_prompt=f"Plan workflow for type {workflow_type.value}:\n{request_text}",
        response_model=PlannerResult,
        mock_response=mock,
    )
