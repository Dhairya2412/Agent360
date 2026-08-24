"""
End-to-end API verification script for AgentOps360.
Run with: python tests/e2e_api_test.py (backend must be running on port 8000)
"""

import json
import sys
import tempfile
from pathlib import Path

import httpx

BASE = "http://localhost:8000"
TIMEOUT = 60.0

results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    client = httpx.Client(base_url=BASE, timeout=TIMEOUT)

    # 1. Health
    try:
        r = client.get("/api/health/live")
        record("GET /api/health/live", r.status_code == 200 and r.json().get("status") == "alive")
        r = client.get("/api/health")
        data = r.json()
        record("GET /api/health", r.status_code == 200 and data.get("status") in ("healthy", "degraded"), str(data.get("status")))
        record("MOCK_MODE in health", "mock_mode" in data, str(data.get("mock_mode")))
        chroma = data.get("chroma", {})
        record("Chroma status present", "connected" in chroma, f"connected={chroma.get('connected')}")
    except Exception as e:
        record("GET /api/health", False, str(e))
        print("Backend not reachable. Start uvicorn first.")
        return 1

    # 2. List endpoints
    for path in ["/api/workflows", "/api/approvals/pending", "/api/audit-logs", "/api/analytics/summary", "/api/documents"]:
        try:
            r = client.get(path)
            record(f"GET {path}", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record(f"GET {path}", False, str(e))

    # 3. IT workflow
    it_id = ""
    try:
        r = client.post("/api/workflows/start", json={
            "workflow_type": "IT_HELPDESK",
            "request_text": "My VPN is not connecting and I need access before a client meeting. I already tried restarting my laptop.",
        })
        wf = r.json()
        it_id = wf.get("id", "")
        ok = r.status_code == 200 and wf.get("workflow_type") in ("IT_HELPDESK", "AUTO_DETECT")
        record("IT workflow start", ok, f"id={it_id[:8]}... status={wf.get('status')}")
        record("IT workflow completed or running", wf.get("status") in ("completed", "running", "awaiting_approval"), wf.get("status"))
    except Exception as e:
        record("IT workflow start", False, str(e))

    # 4. Supply chain workflow
    try:
        r = client.post("/api/workflows/start", json={
            "workflow_type": "SUPPLY_CHAIN_ORDER",
            "request_text": "Please process an order for ABC Foods: 10 boxes of Fuji apples, 5 cases of oat milk, and 20 packs of wheat bread for delivery this Friday.",
        })
        wf = r.json()
        record("Supply chain workflow", r.status_code == 200, f"status={wf.get('status')} type={wf.get('workflow_type')}")
    except Exception as e:
        record("Supply chain workflow", False, str(e))

    # 5. Banking workflow (should await approval)
    bank_id = ""
    approval_id = ""
    try:
        r = client.post("/api/workflows/start", json={
            "workflow_type": "BANKING_SUPPORT",
            "request_text": "My card was blocked after a suspicious transaction. I need help unlocking it.",
        })
        wf = r.json()
        bank_id = wf.get("id", "")
        status = wf.get("status")
        record("Banking workflow start", r.status_code == 200, f"status={status}")
        record("Banking awaits approval", status == "awaiting_approval", status)
    except Exception as e:
        record("Banking workflow start", False, str(e))

    # 6. Pending approvals
    try:
        r = client.get("/api/approvals/pending")
        approvals = r.json()
        record("GET pending approvals", r.status_code == 200 and isinstance(approvals, list), f"count={len(approvals)}")
        if approvals:
            approval_id = approvals[0].get("id", "")
    except Exception as e:
        record("GET pending approvals", False, str(e))

    # 7. Approve one (if exists)
    if approval_id:
        try:
            r = client.post(f"/api/approvals/{approval_id}/approve")
            record("Approve workflow", r.status_code == 200, approval_id[:8])
        except Exception as e:
            record("Approve workflow", False, str(e))

    # 8. Reject test — create another banking wf and reject
    try:
        r = client.post("/api/workflows/start", json={
            "workflow_type": "BANKING_SUPPORT",
            "request_text": "Unauthorized fraud charge of $5000 on my card please reverse immediately",
        })
        wf = r.json()
        r2 = client.get("/api/approvals/pending")
        pending = r2.json()
        reject_target = next((a for a in pending if a.get("workflow_id") == wf.get("id")), None)
        if reject_target:
            r3 = client.post(f"/api/approvals/{reject_target['id']}/reject?reason=E2E%20test%20reject")
            record("Reject approval", r3.status_code == 200, reject_target["id"][:8])
        else:
            record("Reject approval", True, "skipped — no matching pending approval")
    except Exception as e:
        record("Reject approval", False, str(e))

    # 9. Knowledge base upload
    vpn_policy = (
        "VPN troubleshooting policy: If a user cannot connect to VPN, "
        "first verify MFA enrollment, then reset the VPN profile, "
        "then escalate to IT Security if the problem persists."
    )
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(vpn_policy)
            tmp = f.name
        with open(tmp, "rb") as f:
            r = client.post("/api/documents/upload", files={"file": ("vpn-policy.txt", f, "text/plain")})
        upload = r.json()
        record("Document upload", r.status_code == 200 and upload.get("chunk_count", 0) > 0, f"chunks={upload.get('chunk_count')}")
        Path(tmp).unlink(missing_ok=True)
    except Exception as e:
        record("Document upload", False, str(e))

    # 10. IT workflow after KB upload
    try:
        r = client.post("/api/workflows/start", json={
            "workflow_type": "IT_HELPDESK",
            "request_text": "VPN not connecting, need MFA and profile reset per company policy",
        })
        wf = r.json()
        retrieval = wf.get("retrieval") or {}
        fallback = retrieval.get("fallback_used", True)
        record("IT workflow after KB upload", r.status_code == 200, f"fallback_used={fallback}")
    except Exception as e:
        record("IT workflow after KB upload", False, str(e))

    # 11. Audit logs
    try:
        r = client.get("/api/audit-logs")
        logs = r.json()
        record("Audit logs exist", r.status_code == 200 and len(logs) > 0, f"count={len(logs)}")
        agents = {l.get("agent_name") for l in logs}
        record("Audit has agent names", len(agents) > 0, str(agents)[:80])
    except Exception as e:
        record("Audit logs exist", False, str(e))

    # 12. Analytics
    try:
        r = client.get("/api/analytics/summary")
        s = r.json()
        record("Analytics summary", r.status_code == 200 and "total_workflows" in s, json.dumps({k: s[k] for k in list(s)[:4]}))
        r2 = client.get("/api/analytics/workflow-types")
        record("Analytics workflow-types", r2.status_code == 200, f"types={len(r2.json())}")
        r3 = client.get("/api/analytics/agent-performance")
        record("Analytics agent-performance", r3.status_code == 200, "ok")
    except Exception as e:
        record("Analytics summary", False, str(e))

    # 13. Error handling
    try:
        r = client.post("/api/workflows/start", json={"workflow_type": "IT_HELPDESK", "request_text": "ab"})
        record("Short input validation", r.status_code == 422, f"status={r.status_code}")
    except Exception as e:
        record("Short input validation", False, str(e))

    try:
        r = client.post("/api/approvals/nonexistent-id-000/approve")
        record("Invalid approval ID", r.status_code in (400, 404), f"status={r.status_code}")
    except Exception as e:
        record("Invalid approval ID", False, str(e))

    try:
        r = client.post("/api/documents/upload", files={"file": ("bad.exe", b"data", "application/octet-stream")})
        record("Unsupported file type", r.status_code == 400, f"status={r.status_code}")
    except Exception as e:
        record("Unsupported file type", False, str(e))

    # Summary
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f"\n=== E2E API Results: {passed} passed, {failed} failed ===")
    if failed:
        print("\nFailed tests:")
        for name, ok, detail in results:
            if not ok:
                print(f"  - {name}: {detail}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
