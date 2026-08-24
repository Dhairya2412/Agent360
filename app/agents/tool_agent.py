"""Tool execution agent — validates and runs allowlisted mock tools."""

import time
from typing import Any

from app.schemas.agent_schema import ToolExecutionResult
from app.tools.tool_registry import execute_tool, is_allowed_tool


async def execute_tool_action(tool_name: str, parameters: dict[str, Any]) -> ToolExecutionResult:
    if not tool_name:
        return ToolExecutionResult(
            tool_name="none",
            success=False,
            result={"error": "No tool specified"},
        )

    if not is_allowed_tool(tool_name):
        return ToolExecutionResult(
            tool_name=tool_name,
            success=False,
            result={"error": f"Tool '{tool_name}' not in allowlist"},
        )

    start = time.perf_counter()
    try:
        result = execute_tool(tool_name, parameters)
        elapsed = (time.perf_counter() - start) * 1000
        return ToolExecutionResult(
            tool_name=tool_name,
            success=True,
            result=result,
            execution_time_ms=round(elapsed, 2),
        )
    except Exception as exc:
        elapsed = (time.perf_counter() - start) * 1000
        return ToolExecutionResult(
            tool_name=tool_name,
            success=False,
            result={"error": str(exc)},
            execution_time_ms=round(elapsed, 2),
        )
