"""Analytics aggregation service."""

from typing import Any

from app.database.repositories import approval_repo, audit_repo, document_repo, workflow_repo


class AnalyticsService:
    async def summary(self) -> dict[str, Any]:
        workflows = await workflow_repo.list_all(limit=1000)
        total = len(workflows)
        completed = sum(1 for w in workflows if w.get("status") == "completed")
        failed = sum(1 for w in workflows if w.get("status") == "failed")
        pending_approvals = len(await approval_repo.list_pending())
        docs = await document_repo.list_all()

        latencies = [w.get("total_latency_ms", 0) for w in workflows if w.get("total_latency_ms")]
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0

        success_rate = round((completed / total) * 100, 1) if total else 0

        return {
            "total_workflows": total,
            "success_rate": success_rate,
            "pending_approvals": pending_approvals,
            "avg_resolution_time_ms": avg_latency,
            "failed_runs": failed,
            "total_documents": len(docs),
        }

    async def workflow_types(self) -> list[dict[str, Any]]:
        workflows = await workflow_repo.list_all(limit=1000)
        counts: dict[str, int] = {}
        for w in workflows:
            wt = w.get("workflow_type", "UNKNOWN")
            counts[wt] = counts.get(wt, 0) + 1
        return [{"type": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: -x[1])]

    async def agent_performance(self) -> dict[str, Any]:
        logs = await audit_repo.list_all(limit=500)
        by_agent: dict[str, list[float]] = {}
        approval_count = 0
        total_logs = len(logs)

        for log in logs:
            agent = log.get("agent_name", "unknown")
            conf = log.get("confidence_score")
            if conf is not None:
                by_agent.setdefault(agent, []).append(conf)
            if log.get("human_approval_required"):
                approval_count += 1

        avg_confidence = {
            agent: round(sum(scores) / len(scores), 2)
            for agent, scores in by_agent.items()
            if scores
        }

        workflows = await workflow_repo.list_all(limit=1000)
        status_breakdown = {
            "completed": sum(1 for w in workflows if w.get("status") == "completed"),
            "failed": sum(1 for w in workflows if w.get("status") == "failed"),
            "awaiting_approval": sum(1 for w in workflows if w.get("status") == "awaiting_approval"),
            "rejected": sum(1 for w in workflows if w.get("status") == "rejected"),
        }

        return {
            "avg_confidence_by_agent": avg_confidence,
            "human_approval_rate": round((approval_count / total_logs) * 100, 1) if total_logs else 0,
            "status_breakdown": status_breakdown,
            "agent_latency": [
                {"agent": agent, "avg_confidence": conf}
                for agent, conf in avg_confidence.items()
            ],
        }


analytics_service = AnalyticsService()
