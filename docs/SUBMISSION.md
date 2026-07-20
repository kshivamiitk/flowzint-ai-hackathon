# FlowZint AI Hackathon 2026 Submission

## Project

**PulseResolve AI**

## Category

**Customer Care Bot**

## One-line Pitch

PulseResolve turns a customer complaint into a verified, policy-authorized
resolution and turns repeated complaints into operational incident intelligence.

## Portal Description

PulseResolve AI is an incident-aware customer-care platform for failed-payment
and refund workflows. It understands English, Hindi, and Hinglish messages,
verifies customer and transaction data, retrieves applicable policy evidence,
and produces an explainable resolution trace. Deterministic rules, rather than
the language model, authorize monetary actions: low-risk refunds can execute
automatically, medium-risk actions require operator approval, and high-value
cases are explicitly escalated. PulseResolve also correlates semantically
similar complaints with shared technical signals to detect operational
incidents, estimate a probable root cause, and preserve every material decision
in a human-readable audit trail.

## Problem

Customer-care teams repeatedly interpret the same payment complaint, search
transaction systems, check refund policy, request approvals, and manually notice
outage patterns. Traditional chatbots answer one conversation at a time and do
not safely connect that conversation to business action or system-level insight.

## Solution

PulseResolve provides one governed workflow:

1. Classify the customer request and language.
2. Load verified customer and transaction evidence.
3. Retrieve the most relevant support policies.
4. Apply deterministic refund and escalation rules.
5. Execute a safe mock action or wait for human approval.
6. Correlate the complaint with recent operational signals.
7. Record the complete event history for review.

## Innovation

- Separates AI interpretation from deterministic financial authorization.
- Combines semantic complaint similarity with shared error codes, app versions,
  and payment rails for provider-independent incident detection.
- Exposes a six-stage resolution trace without revealing hidden model reasoning.
- Continues operating through free-provider outages using local deterministic
  fallback.
- Restores the full synthetic demo dataset with one click for repeatable judging.

## Real-World Value

- Shortens repetitive failed-payment handling.
- Prevents unsafe or duplicate refunds.
- Gives operators evidence before approval.
- Identifies service failures from customer signals earlier.
- Produces an auditable history of AI and human decisions.

## Technical Architecture

- Frontend: Next.js 16, React 19, TypeScript, Lucide icons.
- Backend: FastAPI, Pydantic, application services, domain entities, ports, and
  infrastructure adapters.
- Database: async SQLAlchemy with SQLite locally and PostgreSQL through Docker.
- AI: free deterministic local mode plus an OpenAI-compatible hosted adapter
  with schema validation and local fallback.
- Quality: 19 backend tests, 8 labelled evaluation cases, Ruff, ESLint,
  TypeScript, production build, and a complete Playwright browser workflow.

## Three-Minute Demo

1. Reset the synthetic environment from the Command Center.
2. Run **Automatic resolution** and show verified ₹449 transaction evidence,
   policy sources, completed mock refund, and the six-stage trace.
3. Open **Incident Intelligence** and show three correlated customers, shared
   error code, app version, payment rail, root cause, and confidence.
4. Run **Human approval**, open the queue, add an evidence note, and approve the
   ₹1,499 action.
5. Show **Protected escalation** for the ₹3,299 case.
6. Open **Audit Trail** and filter AI decisions, actions, and incidents.

## Safety and Scope

- All customers and transactions are synthetic.
- `MockRefundGateway` simulates payment movement; no real refund is sent.
- API keys remain in an ignored local `.env` file and are never committed.
- The application works without any paid API using `AI_PROVIDER=local`.

## Submission Fields

- Project title: `PulseResolve AI`
- Track: `Customer Care Bot`
- Source repository: `https://github.com/kshivamiitk/flowzint-ai-hackathon`
- Demo video: add the public YouTube or Google Drive URL after recording.
- Live project URL: optional; submit the repository and video first.

## Final Checklist

- [ ] Latest code is pushed to the public repository.
- [ ] Repository opens in an incognito window.
- [ ] Public demo video is between two and five minutes.
- [ ] Automatic, approval, escalation, incident, and audit paths are shown.
- [ ] Local secrets and database files are absent from Git.
- [ ] Portal description exceeds 50 words.
- [ ] Submission receipt is exported after final submission.
