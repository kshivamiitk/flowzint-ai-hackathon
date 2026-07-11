# Demo Script

Target duration: 3 to 4 minutes.

## 1. Problem — 20 seconds

“Traditional support bots answer one customer at a time. PulseResolve also
detects when many complaints point to one operational failure, while keeping
money movement behind deterministic rules and human approval.”

## 2. Architecture — 25 seconds

Show `docs/LLD.md` or the README architecture diagram. Point out:

- domain rules are framework-independent;
- AI providers are replaceable;
- the LLM cannot authorize refunds;
- every action is audited.

## 3. Automatic resolution — 60 seconds

1. Open Customer Chat.
2. Select Kumar Shivam.
3. Send the Hinglish failed-payment message.
4. Highlight:
   - recognized intent and language;
   - loaded verified transaction;
   - policy source;
   - ₹449 auto-refund;
   - completed action reference.

## 4. Incident detection — 45 seconds

Open Incidents and show:

- three related complaints;
- shared error code;
- app version;
- payment method;
- probable root cause;
- confidence.

Explain that the system moved from one-customer resolution to system-level
operational intelligence.

## 5. Human approval — 45 seconds

1. Select Aarav Mehta.
2. Send the failed-payment message.
3. Open Approvals.
4. Show the ₹1,499 action blocked by policy.
5. Approve it and show completion.

## 6. Audit and safety — 30 seconds

Open Audit Trail. Show:

- classification;
- approval request;
- operator approval;
- refund completion;
- incident event.

Mention idempotency, deterministic policy limits, and the simulated gateway.

## 7. Close — 15 seconds

“PulseResolve combines grounded customer support, safe action automation, and
cross-conversation incident intelligence in one explainable workflow.”
