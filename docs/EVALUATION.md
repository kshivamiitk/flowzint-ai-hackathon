# Evaluation Plan

## Objectives

The system should be evaluated as both software and an AI-assisted workflow.

## Core scenarios

| Scenario | Expected result |
|---|---|
| ₹449 failed payment | Automatic completed refund |
| ₹1,499 failed payment | Awaiting approval |
| ₹3,299 failed payment | High-value human review |
| Repeat ₹449 request | Existing action returned; no second refund |
| Unrelated FAQ | No monetary action |
| Missing transaction | Escalation, no refund |
| Third similar complaint | Incident created |
| Unrelated complaint | Not attached to failed-payment incident |

## AI and retrieval metrics

- intent accuracy;
- severity accuracy;
- top-k policy retrieval accuracy;
- unsupported-claim rate;
- correct tool/action recommendation rate;
- response groundedness;
- latency.

## Workflow metrics

- unauthorized-action rate;
- duplicate-refund rate;
- approval-routing accuracy;
- valid state-transition rate;
- audit completeness;
- incident precision;
- incident recall;
- mean resolution time.

## Automated tests included

- refund policy thresholds;
- action state transitions;
- complete API flow;
- duplicate-message idempotency;
- human approval flow;
- incident creation.

Run:

```bash
cd backend
pytest -q
```

## Suggested hackathon benchmark

Create at least 40 labelled cases:

- 10 FAQs;
- 10 failed payments/refunds;
- 8 unsafe or unsupported requests;
- 8 messages belonging to two incident clusters;
- 4 unrelated complaints.

Store the expected intent, policy section, action mode, and incident group.
Report both successes and limitations in the submission.
