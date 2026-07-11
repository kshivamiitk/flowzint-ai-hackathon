# PulseResolve AI

PulseResolve is a complete hackathon-ready reference implementation of an
**incident-aware customer-care platform**. It resolves individual support
requests, checks deterministic refund rules, executes safe mock actions,
routes sensitive actions to human approval, detects cross-customer incidents,
and records an audit trail.

The repository is intentionally structured for readability. Domain rules do
not depend on FastAPI, SQLAlchemy, HTTP clients, or a particular AI provider.

## What is included

- Customer chat with English/Hinglish issue classification
- Policy retrieval using embeddings
- Automatic refund for eligible transactions up to ₹500
- Approval workflow for refunds from ₹500 to ₹2,000
- Human-review workflow above ₹2,000
- Idempotency protection against duplicate refunds
- Similar-complaint detection and automatic incident creation
- Evidence-based probable root-cause summary
- Operations dashboard, approvals page, incidents page, and audit trail
- Deterministic local AI mode requiring no API key
- Optional OpenAI-compatible chat-completions and embeddings adapter
- SQLite development mode and PostgreSQL Docker mode
- Automated backend tests, frontend type checking, linting, and CI

## Architecture

```text
Browser / Next.js
       |
       v
FastAPI controllers
       |
       v
Application services
  - ChatOrchestrator
  - ActionWorkflowService
  - IncidentDetectionService
  - QueryService
       |
       v
Domain entities + ports + deterministic rules
       ^
       |
Infrastructure adapters
  - SQLAlchemy repositories / Unit of Work
  - Local or remote AI provider
  - Mock refund gateway
```

Read [docs/LLD.md](docs/LLD.md) for the component-level design and SOLID
mapping.

## Quick start with Docker

Requirements: Docker Desktop or Docker Engine with Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Web application: http://localhost:3000
- API documentation: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/health

The Docker setup uses PostgreSQL. The first API startup creates the schema and
seeds demonstration data.

## Quick start without Docker

Requirements:

- Python 3.11+
- Node.js 22+
- npm

Terminal 1:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Terminal 2:

```bash
cd frontend
npm install
npm run dev
```

The local backend defaults to SQLite and creates `backend/pulseresolve.db`.

## Demonstration flow

### Automatic refund and incident detection

1. Open **Customer Chat**.
2. Select **Kumar Shivam**.
3. Send the pre-filled Hinglish message:
   `Bhai payment deduct ho gaya but order confirm nahi hua.`
4. The application:
   - classifies the complaint;
   - retrieves relevant policy sections;
   - verifies the ₹449 transaction;
   - applies the deterministic refund policy;
   - completes a mock refund;
   - detects the third related failed-payment complaint;
   - creates an incident with shared error, app-version, and payment evidence.
5. Open **Incidents** and **Audit Trail**.

### Human approval

1. Select **Aarav Mehta**.
2. Send:
   `UPI charged me but the order was not created.`
3. The ₹1,499 refund enters `awaiting_approval`.
4. Open **Approvals**, review the evidence, and approve or reject it.

### High-value review

1. Select **Neha Singh**.
2. Send:
   `Payment ho gaya lekin booking confirm nahi hui.`
3. The ₹3,299 request remains blocked for explicit human review.

> All money movement is simulated through `MockRefundGateway`. No real payment
> provider is contacted.

## AI modes

### Local mode (default)

```env
AI_PROVIDER=local
```

This mode uses:

- a deterministic, readable complaint analyzer;
- a local hashing-vector embedding implementation;
- a deterministic grounded response generator.

It is ideal for demos, tests, offline development, and predictable judging.

### OpenAI-compatible mode

```env
AI_PROVIDER=openai_compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_key
LLM_MODEL=your_chat_model
EMBEDDING_MODEL=your_embedding_model
```

The adapter uses standard `/chat/completions` and `/embeddings` endpoints.
Provider-specific changes remain inside `backend/app/infrastructure/ai`.

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `DATABASE_URL` | SQLite URL | Async SQLAlchemy connection |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed frontend origins |
| `AI_PROVIDER` | `local` | `local` or `openai_compatible` |
| `AUTO_REFUND_LIMIT` | `500` | Highest automatic refund amount |
| `APPROVAL_REFUND_LIMIT` | `2000` | Highest normal approval amount |
| `INCIDENT_SIMILARITY_THRESHOLD` | `0.68` | Complaint similarity cutoff |
| `INCIDENT_MIN_COMPLAINTS` | `3` | Complaints needed for an incident |
| `INCIDENT_WINDOW_MINUTES` | `60` | Detection lookback window |

## Quality checks

From the repository root:

```bash
make test
make lint
```

Or run individually:

```bash
cd backend
pytest -q
ruff check app tests eval
ruff format --check app tests

cd ../frontend
npm run typecheck
npm run lint
npm run build
```

## Repository map

```text
pulseresolve-ai/
├── backend/
│   ├── app/
│   │   ├── api/              # HTTP controllers and composition
│   │   ├── application/      # Use cases and orchestration
│   │   ├── core/             # Configuration and logging
│   │   ├── domain/           # Entities, enums, ports, exceptions
│   │   └── infrastructure/   # DB, AI, and gateway adapters
│   └── tests/
├── frontend/
│   ├── app/                  # Next.js App Router pages
│   ├── components/           # Typed, focused UI components
│   └── lib/                  # API client and shared types
├── docs/
├── .github/workflows/ci.yml
├── docker-compose.yml
└── Makefile
```

## Important production work

This repository is complete for a hackathon demo, but real production use must
add:

- identity provider integration and role-based access control;
- real payment-provider signatures, reconciliation, and secrets management;
- production migrations such as Alembic instead of startup schema creation;
- queue-backed retries and outbox/event delivery;
- PII redaction, retention controls, and security review;
- provider-specific structured-output validation;
- monitoring, tracing, backups, and disaster recovery.

See [docs/SECURITY.md](docs/SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
