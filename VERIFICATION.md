# Verification Record

Verified locally on 20 July 2026.

## Backend

```text
ruff check app tests eval           PASS
ruff format --check app tests eval  PASS
pytest -q                            PASS: 19 tests
python -m eval.run_evaluation        PASS: 8/8 labelled cases
```

Covered flows include automatic refund, approval and execution, high-value
escalation, duplicate-refund idempotency, hosted-AI fallback, demo reset,
structured response validation, evidence-assisted incident detection, incident
state transitions, and audit creation.

FastAPI's current test-client compatibility layer emits one deprecation warning.
It does not fail tests or affect runtime behavior.

## Frontend

```text
npm run typecheck  PASS
npm run lint       PASS
npm run build      PASS
npm run test:e2e   PASS: complete browser workflow
npm audit --omit=dev  PASS: 0 vulnerabilities
```

The browser test resets the synthetic environment, completes the automatic
refund, creates a protected approval, approves it, investigates the generated
incident, verifies audit events, and checks a 390px mobile viewport for page
overflow.

The production build generated `/`, `/chat`, `/incidents`, `/approvals`, and
`/audit`.

## Live Smoke Test

The running local system was verified with the hosted OpenAI-compatible chatbot
configuration and local fallback enabled:

- `/health` reported API, database, chatbot, and demo status;
- reset restored three customers and three scenarios;
- ₹449 completed automatically and created a three-customer incident;
- ₹1,499 entered approval and completed after operator review;
- ₹3,299 was labelled high risk with human escalation;
- incident status moved from detected to investigating;
- audit events were visible in the frontend.

## Security and Packaging

- `.env` is ignored and not tracked.
- Tracked files and current Git history were scanned for common API-key shapes.
- Placeholder values do not resemble live provider keys.
- `node_modules`, `.next`, virtual environments, Python caches, test results,
  local databases, and local environment files are excluded from submission.
