# API Guide

Base URL: `http://localhost:8000/api/v1`

Interactive OpenAPI documentation is available at `/docs`.

## Health

```http
GET /health
```

## Customers

```http
GET /api/v1/customers
GET /api/v1/transactions
GET /api/v1/transactions?customer_id=cust-kumar
```

## Customer message

```http
POST /api/v1/chat/messages
Content-Type: application/json
```

```json
{
  "customer_id": "cust-kumar",
  "message": "Bhai payment deduct ho gaya but order confirm nahi hua."
}
```

The response includes:

- classification and confidence;
- explicit decision mode and risk level;
- a six-stage explainability trace;
- policy references;
- generated customer response;
- proposed/completed action;
- detected incident, when applicable.

## Operations

```http
GET /api/v1/dashboard/metrics
GET /api/v1/incidents
GET /api/v1/actions
GET /api/v1/actions?status=awaiting_approval
GET /api/v1/audit-events?limit=100
```

## Reset synthetic demo

Available only when `DEMO_MODE=true`:

```http
POST /api/v1/demo/reset
```

This deletes only synthetic conversations, actions, incidents, policies,
transactions, and customers before restoring the original demonstration data.

## Update incident status

```http
POST /api/v1/incidents/{incident_id}/status
Content-Type: application/json
```

```json
{
  "status": "investigating"
}
```

Valid transitions are enforced by the incident domain entity and invalid moves
return HTTP `409`.

## Approve action

```http
POST /api/v1/actions/{action_id}/approve
Content-Type: application/json
```

```json
{
  "comment": "Transaction and policy evidence verified."
}
```

## Reject action

```http
POST /api/v1/actions/{action_id}/reject
Content-Type: application/json
```

```json
{
  "comment": "Evidence is insufficient."
}
```

## Example with curl

```bash
curl -s http://localhost:8000/api/v1/customers

curl -s -X POST http://localhost:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust-kumar",
    "message": "Bhai payment deduct ho gaya but order confirm nahi hua."
  }'
```

## Error behavior

| Status | Meaning |
|---:|---|
| `400` | Domain rule or request cannot be processed |
| `404` | Entity does not exist |
| `409` | Invalid state transition |
| `422` | Request body failed schema validation |
| `500` | Unhandled service/infrastructure failure |
