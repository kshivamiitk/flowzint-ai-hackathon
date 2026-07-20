# Security Model

## Implemented safeguards

- Monetary authorization is deterministic, not delegated to the LLM.
- Tool arguments originate from verified database records.
- Duplicate refund actions are blocked by an idempotency key and unique
  database constraint.
- Human approval is required for configured monetary thresholds.
- Prompts tell remote models to treat customer content as untrusted data.
- Remote responses are mapped into typed domain values.
- Invalid or unavailable hosted chatbot responses fall back to local,
  deterministic components.
- Environment variables hold provider credentials.
- CORS origins are configurable.
- Every classification, approval, rejection, refund, and incident creates an
  audit event.
- Generated answers may not claim success unless the workflow reports a
  completed action.
- The local default uses no external provider and sends no customer data away.

## Threat boundaries

### Customer input

Customer messages are untrusted. They may contain prompt injection, false
claims, or attempts to access another account. The workflow loads customer and
transaction data from the authenticated customer identifier, not from IDs
asserted inside free text.

### AI provider

Model output is advisory and potentially malformed. It cannot directly:

- update a transaction;
- create a refund;
- bypass approval;
- choose an arbitrary refund amount;
- access a repository.

### External action gateway

The included gateway is simulated. A real adapter must verify:

- payment-provider signatures;
- transaction ownership and amount;
- idempotency at the provider;
- provider response authenticity;
- reconciliation and eventual consistency.

## Required before real deployment

1. Add authentication and tenant-aware authorization.
2. Introduce operator roles and least-privilege permissions.
3. Use a secrets manager rather than local environment files.
4. Encrypt sensitive fields and define data-retention rules.
5. Add PII redaction to logs, prompts, and analytics.
6. Rate-limit customer and approval endpoints.
7. Add CSRF protection where cookie-based auth is used.
8. Add database migrations and reviewed rollback procedures.
9. Add an outbox pattern for reliable side effects.
10. Perform dependency, SAST, DAST, and penetration testing.
11. Add immutable audit storage and alerting for suspicious actions.
12. Validate model output against strict provider-supported JSON schemas.
13. Add content moderation and abuse controls appropriate to the business.

## Demo disclaimer

Seed customers, transactions, policies, logs, refund references, and incident
results are synthetic. No real money is transferred. The reset endpoint is
available only when `DEMO_MODE=true` and must be disabled outside a synthetic
demonstration environment.
