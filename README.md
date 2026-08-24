# AgentOps360

**Multi-agent enterprise workflow automation platform** — route messy business requests through orchestrator, planner, retrieval, domain specialist, critic, human approval, tool execution, and audit agents.


---

## Why This Project Matters

Enterprise teams receive unstructured requests across IT, supply chain, and customer support. Manual triage is slow, error-prone, and hard to audit. AgentOps360 demonstrates how **LangGraph multi-agent pipelines** with **human-in-the-loop approval**, **RAG policy retrieval**, and **structured tool calling** can automate workflows while maintaining compliance and traceability.

### Real-World Use Cases

- **IT Helpdesk**: VPN resets, MFA issues, password lockouts, software access requests
- **Supply Chain**: Parse natural-language orders, check inventory, create supply orders
- **Banking Support**: Fraud flags, dispute cases, account reviews with mandatory approval gates

---

## Architecture

```
User Request (Next.js UI)
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                    FastAPI Backend                         │
│  POST /api/workflows/start                                 │
└───────────────────────────┬───────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────┐
│              LangGraph Enterprise Workflow                 │
│                                                            │
│  classify_request → plan_workflow → retrieve_context       │
│       → run_domain_agent → critic_check                    │
│              ├─ [approval required] → human_approval_gate  │
│              └─ [auto-approved] → execute_tool           │
│                     → audit_log → final_response           │
└───────────────────────────┬───────────────────────────────┘
                            ▼
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   MongoDB Atlas      ChromaDB (local)    Mock Tools
   (traces, logs)     (RAG embeddings)   (allowlisted)
```

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, ShadCN UI, Framer Motion, Recharts |
| Backend | FastAPI, Python, Pydantic, LangGraph, Uvicorn |
| LLM | OpenAI API (optional — MOCK_MODE available) |
| Databases | MongoDB Atlas (workflow logs), ChromaDB (vector KB) |
| Document Parsing | PyMuPDF |

---

## Features

- **Dashboard** — KPIs, charts, recent workflows
- **Workflow Submission** — Auto-detect or select domain, upload documents
- **Multi-Agent Pipeline** — 9 LangGraph nodes with conditional branching
- **Human Approval Queue** — Approve, reject, or edit-and-approve
- **Agent Timeline UI** — Visual step-by-step execution trace
- **Knowledge Base** — Upload PDF/TXT/CSV/MD, chunk, embed, retrieve
- **Audit Logs** — Searchable, filterable compliance trail
- **Analytics** — Workflow types, success rates, confidence, approval rates
- **MOCK_MODE** — Run fully without OpenAI API key

---

## Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- **MongoDB Atlas** connection string (or local MongoDB via Docker)
- **OpenAI API key** (optional if `MOCK_MODE=true`)

---

## Quick Start

### 1. Clone and configure

```bash
cd Agent360

# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env.local
```

Edit `backend/.env`:

```env
MOCK_MODE=true
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=agentops360
```

> With `MOCK_MODE=true`, no OpenAI API key is required. Agents return deterministic outputs.

### 2. Start MongoDB (optional — if not using Atlas)

```bash
docker compose up mongodb -d
```

### 3. Run backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend health check: http://localhost:8000/api/health

### 4. Run frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### 5. Run with Docker Compose

```bash
docker compose up --build
```

> When using MongoDB Atlas, skip the local `mongodb` service and set `MONGODB_URI` in `backend/.env`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | — |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `agentops360` |
| `CHROMA_PERSIST_DIR` | ChromaDB local storage path | `./chroma_db` |
| `CHROMA_USE_CLOUD` | Use Chroma Cloud instead of local disk | `false` |
| `CHROMA_API_KEY` | Chroma Cloud API key (from trychroma.com) | — |
| `CHROMA_TENANT` | Chroma Cloud tenant ID | — |
| `CHROMA_DATABASE` | Chroma Cloud database name | `AgentOps360` |
| `CHROMA_COLLECTION_NAME` | Vector collection name | `agentops360_knowledge` |
| `OPENAI_MODEL` | Chat model | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `MOCK_MODE` | Skip OpenAI calls | `true` |
| `ENVIRONMENT` | `development`, `staging`, or `production` | `development` |
| `SEED_DEMO_DATA` | Seed demo workflows on startup | `true` |
| `MONGODB_REQUIRED` | Fail if MongoDB unavailable | `false` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` |
| `DOCS_ENABLED` | Expose `/docs` and OpenAPI | `true` |
| `MAX_UPLOAD_SIZE_MB` | Document upload limit | `10` |
| `BACKEND_PORT` | Server port | `8000` |
| `FRONTEND_URL` | CORS origin | `http://localhost:3000` |
| `LANGSMITH_API_KEY` | Optional LangSmith tracing | — |
| `REDIS_URL` | Optional Redis (future) | — |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend URL (`http://localhost:8000`) |

---

## Chroma Cloud Setup (optional)

AgentOps360 supports **local ChromaDB** (default) or **Chroma Cloud** (hosted).

1. Get your API key from [https://trychroma.com](https://trychroma.com)
2. Add to `backend/.env`:

```env
CHROMA_USE_CLOUD=true
CHROMA_API_KEY=your-chroma-api-key
CHROMA_TENANT=21b63392-6e72-4f1f-828b-0fb0e9abe21b
CHROMA_DATABASE=AgentOps360
```

3. Restart the backend
4. Verify: `GET http://localhost:8000/api/health` should show `"chroma": { "mode": "cloud", "connected": true }`
5. Upload a document via **Knowledge Base** — chunks are stored in your Chroma Cloud database
6. Submit a workflow — the retrieval agent queries Chroma Cloud for relevant context

> Keep `MOCK_MODE=true` or use the same embedding model consistently. Embeddings are sized to 1536 dimensions (`text-embedding-3-small`).

---

## API Endpoints

### Workflows
- `POST /api/workflows/start` — Start new workflow
- `GET /api/workflows` — List workflows
- `GET /api/workflows/{id}` — Get workflow details
- `POST /api/workflows/{id}/retry` — Retry workflow

### Approvals
- `GET /api/approvals/pending` — List pending approvals
- `POST /api/approvals/{id}/approve` — Approve and execute
- `POST /api/approvals/{id}/reject` — Reject workflow
- `POST /api/approvals/{id}/edit-approve` — Edit action and approve

### Documents
- `POST /api/documents/upload` — Upload and index document
- `GET /api/documents` — List documents
- `DELETE /api/documents/{id}` — Delete document

### Audit & Analytics
- `GET /api/audit-logs` — List audit logs
- `GET /api/audit-logs/{workflow_id}` — Logs for workflow
- `GET /api/analytics/summary` — Dashboard KPIs
- `GET /api/analytics/workflow-types` — Type breakdown
- `GET /api/analytics/agent-performance` — Agent metrics

### Health
- `GET /api/health/live` — Liveness probe (process up)
- `GET /api/health` — Readiness probe (MongoDB + Chroma status; returns 503 if degraded)

---

## Production Deployment

### Recommended settings

```env
ENVIRONMENT=production
MOCK_MODE=false
OPENAI_API_KEY=sk-...
MONGODB_URI=mongodb+srv://...
MONGODB_REQUIRED=true
SEED_DEMO_DATA=false
DOCS_ENABLED=false
CORS_ORIGINS=https://your-frontend-domain.com
CHROMA_USE_CLOUD=true
CHROMA_API_KEY=...
CHROMA_TENANT=...
```

### Docker Compose (full stack)

```bash
docker compose up --build -d
```

- Backend: http://localhost:8000/api/health
- Frontend: http://localhost:3000
- MongoDB runs in-container; for Atlas, remove the `mongodb` service and set `MONGODB_URI` on `backend`.

### End-to-end verification

With the backend running on port 8000:

```bash
cd backend
python tests/e2e_api_test.py
```

Expected: all API checks pass (health, workflows, approvals, documents, audit, analytics).

### CI

GitHub Actions runs backend unit tests and frontend lint/build on push/PR (`.github/workflows/ci.yml`).

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Demo Data

On first startup, the backend seeds:
- 5 IT helpdesk workflows
- 5 supply chain workflows
- 5 banking support workflows
- Several pending approvals
- Mock product catalog, inventory, SOPs, and banking policies

---

## Resume Bullets

- Built AgentOps360, a multi-agent enterprise workflow automation platform using LangGraph, FastAPI, Next.js, MongoDB, and ChromaDB to automate IT helpdesk, supply chain, and customer support workflows with planner, retrieval, critic, approval, tool-execution, and audit agents.

- Implemented human-in-the-loop approval, structured tool calling, RAG-based policy retrieval, workflow tracing, and analytics dashboards to improve reliability, reduce hallucination risk, and provide enterprise-grade auditability.

---

## Future Improvements

- JWT authentication and role-based access control
- Real Jira/ServiceNow/banking API integrations
- LangSmith tracing integration
- Redis queue for async workflow execution
- WebSocket live agent timeline updates
- Multi-tenant organization support

---

## License

MIT
