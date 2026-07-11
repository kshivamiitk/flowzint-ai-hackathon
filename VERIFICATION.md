# Verification Record

Verified in the artifact-generation environment on 11 July 2026.

## Backend

```text
ruff check app tests eval           PASS
ruff format --check app tests eval  PASS
pytest -q                            PASS: 10 tests
python -m eval.run_evaluation        PASS: 8/8 labelled cases
```

Covered flows include:

- automatic refund;
- approval-required refund;
- high-value escalation rule;
- duplicate refund idempotency;
- action state transitions;
- incident creation;
- API health and read endpoints.

A deprecation warning is emitted by FastAPI's current test-client compatibility
layer; it does not fail tests or affect application behavior.

## Frontend

```text
npm run typecheck  PASS
npm run lint       PASS
npm run build      PASS
```

The production build generated:

- `/`
- `/chat`
- `/incidents`
- `/approvals`
- `/audit`

## Configuration

`docker-compose.yml` was parsed successfully and contains health-gated `db`,
`api`, and `web` services. Docker is not installed in the artifact-generation
environment, so container image execution could not be performed here.

## Packaging

The ZIP excludes:

- `node_modules`;
- `.next`;
- virtual environments;
- Python caches;
- test databases;
- local environment files.
