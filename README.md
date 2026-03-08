# AI Agent Runtime

Production-style FastAPI runtime for building domain-specific AI workflows with routing, retrieval context, memory, observability, and a built-in demo UI.

## Why this is now production-oriented

- Hardened multi-stage Docker image (non-root runtime, healthcheck, slim final image)
- Structured runtime configuration via environment variables
- Request logging middleware with request IDs and latency
- CORS support for frontend integrations
- Automated CI (tests + Docker build) via GitHub Actions
- Reusable real-world domain templates and demo scenarios
- Interactive web UI at `/ui` for product-style demos

## Real-world use cases included

- Customer support automation (billing, refunds, account access)
- Healthcare communication copilot (symptom and follow-up guidance)
- Enterprise knowledge assistant (policy/process retrieval)
- Research assistant (literature/methodology support)
- Sales assistant (qualification and pricing workflows)
- HR assistant (leave, benefits, onboarding)
- IT helpdesk (access and troubleshooting)
- Operations assistant (exceptions and escalations)

## Quick start (local)

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- API docs: `http://localhost:8000/docs`
- Interactive UI: `http://localhost:8000/ui`

## Run with Docker

```bash
docker build -t ai-agent-runtime:latest .
docker run --rm -p 8000:8000 ai-agent-runtime:latest
```

Or with compose:

```bash
docker compose up --build
```

## Environment variables

- `APP_NAME` default: `AI Agent Runtime`
- `APP_VERSION` default: `2.0.0`
- `APP_ENV` default: `production`
- `HOST` default: `0.0.0.0`
- `PORT` default: `8000`
- `LOG_LEVEL` default: `info`
- `ALLOWED_ORIGINS` default: `*` (comma-separated)

## API endpoints

- `GET /` runtime metadata
- `GET /health` health + uptime
- `GET /use-cases` domain templates
- `GET /demo-scenarios` curated demos for UI/product demos
- `GET /memory/{session_id}` inspect short-term session memory
- `DELETE /memory/{session_id}` clear session memory
- `POST /agent/run` execute workflow

Sample payload:

```json
{
  "user_id": "user_001",
  "session_id": "session_001",
  "message": "I was charged twice and need a refund.",
  "use_case": "customer_support",
  "use_retrieval": true,
  "metadata": { "channel": "web" }
}
```

## Testing and CI

Local tests:

```bash
pip install -r requirements-dev.txt
pytest -q
```

CI workflow lives in `.github/workflows/ci.yml` and runs:

- unit/API tests
- Docker image build validation

## Repository hygiene recommendations

- Do not commit local virtual environments (`myvenv`, `.venv`)
- Tag releases (for example `v2.0.0`, `v2.1.0`) for stable adoption
- Add issue templates and contribution guidelines for external users

## Suggested next product steps (to push toward large adoption)

1. Add real LLM provider integration with fallback + retry policies.
2. Add persistent memory and vector retrieval (PostgreSQL + pgvector).
3. Add auth, tenant isolation, usage analytics, and rate limiting.
4. Publish benchmark demos and a hosted playground.

