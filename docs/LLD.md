# Low-Level Design

## 1. Design goals

PulseResolve is designed around five constraints:

1. Business rules remain testable without a web server or database.
2. AI output may recommend work but cannot authorize money movement.
3. Infrastructure can be replaced without rewriting use cases.
4. each state-changing operation is explicit and auditable.
5. Code paths are short enough for a hackathon reviewer to understand quickly.

## 2. Layer responsibilities

### Domain layer

Location: `backend/app/domain`

Contains pure application concepts:

- `Customer`
- `Transaction`
- `Conversation`
- `Action`
- `Incident`
- `AuditEvent`
- enums and domain exceptions
- repository and provider protocols

The domain layer imports no FastAPI, SQLAlchemy, HTTP, or vendor SDK code.

### Application layer

Location: `backend/app/application`

Contains use cases:

- `ChatOrchestrator`
- `ActionWorkflowService`
- `IncidentDetectionService`
- `QueryService`
- `RefundPolicyEngine`

These classes depend on domain protocols and receive concrete implementations
through constructor injection.

### Infrastructure layer

Location: `backend/app/infrastructure`

Implements external details:

- SQLAlchemy models and repositories
- SQLAlchemy Unit of Work
- local deterministic AI adapters
- OpenAI-compatible HTTP adapter
- mock refund gateway
- seed data

### API layer

Location: `backend/app/api`

Maps HTTP requests to application services. Route handlers contain no business
logic. `dependencies.py` is the composition root that wires interfaces to
implementations.

### Presentation layer

Location: `frontend`

Next.js pages and typed React components call the FastAPI API through one
central client in `frontend/lib/api.ts`.

## 3. Dependency direction

```text
API ----------> Application ----------> Domain
                   ^
                   |
Infrastructure ----+
```

The important rule is that the domain never points outward. Infrastructure
implements contracts owned by the domain.

## 4. SOLID mapping

### Single Responsibility Principle

- `RefundPolicyEngine` only decides authorization mode.
- `ActionWorkflowService` only manages action lifecycle and execution.
- `IncidentDetectionService` only finds related complaints and manages
  incidents.
- repositories only persist one aggregate type.
- API routes only translate HTTP calls into use-case calls.

### Open/Closed Principle

New providers can be introduced by implementing an existing protocol:

- `EmbeddingProvider`
- `ComplaintAnalyzer`
- `AnswerGenerator`
- `ActionGateway`
- repository protocols

The orchestration services do not need modification when an adapter changes.

### Liskov Substitution Principle

The local and OpenAI-compatible implementations satisfy the same provider
contracts. A test or offline environment can substitute local components
without changing use-case behavior.

### Interface Segregation Principle

Provider and repository protocols are intentionally narrow. An answer
generator does not need embedding methods; a transaction repository does not
need incident operations.

### Dependency Inversion Principle

Application services receive `UnitOfWork`, AI-provider, and gateway
abstractions. Concrete SQLAlchemy and HTTP classes are constructed only in the
composition root.

## 5. Domain state machines

### Action

```text
PROPOSED
  ├── request_approval() -> AWAITING_APPROVAL
  ├── start_execution()  -> EXECUTING
  └── reject()           -> REJECTED

AWAITING_APPROVAL
  ├── approve()          -> APPROVED
  └── reject()           -> REJECTED

APPROVED
  └── start_execution()  -> EXECUTING

EXECUTING
  ├── complete()         -> COMPLETED
  └── fail()             -> FAILED
```

Invalid transitions raise `ValueError` and are returned as HTTP `409`.

### Transaction

A transaction may transition to `REFUNDED` only once. A second attempt raises
an error, while the workflow's idempotency lookup normally returns the
existing action before this point.

### Incident

The current MVP creates incidents as `DETECTED` and supports the enum states:

```text
DETECTED -> INVESTIGATING -> CONFIRMED -> RESOLVING -> RESOLVED
```

Further transition methods can be added to the domain entity without changing
persistence contracts.

## 6. Chat sequence

```text
Customer
  |
  | POST /chat/messages
  v
ChatOrchestrator
  |-- ComplaintAnalyzer.analyze()
  |-- EmbeddingProvider.embed()
  |-- UnitOfWork
  |     |-- load customer
  |     |-- load latest transaction
  |     |-- retrieve policy evidence
  |     |-- save conversation and classification audit
  |
  |-- ActionWorkflowService.propose_and_process()
  |     |-- RefundPolicyEngine.evaluate()
  |     |-- idempotency lookup
  |     |-- execute automatically OR request approval
  |     |-- save audit event
  |
  |-- AnswerGenerator.generate()
  |-- save grounded response
  |-- IncidentDetectionService.detect()
  |     |-- recent-conversation lookup
  |     |-- cosine similarity
  |     |-- create/update incident
  |     |-- attach conversations and save audit event
  v
ChatResponse
```

## 7. Refund authorization table

| Condition | Decision |
|---|---|
| No verified transaction | Human escalation |
| Already refunded | Reject |
| No failed-payment evidence | Reject |
| Eligible amount ≤ ₹500 | Automatic execution |
| ₹500 < amount ≤ ₹2,000 | Human approval |
| Amount > ₹2,000 | High-value human review |

The LLM is not part of this authorization table.

## 8. Idempotency

An action idempotency key is generated from:

```text
{action_type}:{transaction_id}
```

Before creating an action, the workflow queries the action repository by this
key. Repeated chat requests return the existing action instead of invoking the
refund gateway again. The database also places a unique constraint on the key.

## 9. Unit of Work

`SqlAlchemyUnitOfWork` owns one asynchronous database session and exposes
repositories. Application services call `commit()` only after all related
changes are ready.

Example refund transaction:

1. mark action executing;
2. call gateway;
3. mark transaction refunded;
4. mark action completed;
5. create audit event;
6. commit.

Any uncaught error exits the context and rolls back uncommitted database work.

## 10. Policy retrieval

Each policy section has an embedding. The repository loads candidates and
uses cosine similarity in the application process. This keeps SQLite mode
portable and understandable.

For larger production data:

- PostgreSQL with pgvector should perform nearest-neighbor search in SQL;
- metadata filters should limit documents by tenant and policy version;
- indexing and retrieval evaluation should be added.

## 11. Incident algorithm

For each new conversation:

1. load conversations in the configured time window;
2. keep conversations with the same intent;
3. calculate cosine similarity;
4. retain results above the threshold;
5. require the minimum complaint count;
6. group by a stable intent fingerprint;
7. aggregate error codes, app versions, and payment methods;
8. create or refresh an incident;
9. attach related conversations;
10. write an audit event.

The algorithm is intentionally deterministic and inspectable. A production
version could replace it with DBSCAN, streaming aggregation, or a vector index
behind the same service boundary.

## 12. Main classes

| Class | Responsibility |
|---|---|
| `ChatOrchestrator` | Coordinates one support turn |
| `RefundPolicyEngine` | Pure deterministic decision logic |
| `ActionWorkflowService` | Action state, approval, execution, audit |
| `IncidentDetectionService` | Complaint correlation and incident lifecycle |
| `QueryService` | Read-oriented dashboard data |
| `SqlAlchemyUnitOfWork` | Transaction boundary and repositories |
| `LocalComplaintAnalyzer` | Offline deterministic classification |
| `OpenAICompatibleComplaintAnalyzer` | Remote model classification |
| `MockRefundGateway` | Safe simulated external action |

## 13. Extension examples

### Add a wallet-credit action

1. Add a domain action type.
2. Add a `WalletCreditGateway` protocol.
3. Implement the gateway in infrastructure.
4. Add deterministic eligibility rules.
5. Route execution in a focused workflow strategy.
6. Add tests before wiring the endpoint.

### Add a new AI provider

Implement the three narrow contracts:

```python
class ProviderAnalyzer(ComplaintAnalyzer): ...
class ProviderAnswerGenerator(AnswerGenerator): ...
class ProviderEmbeddingProvider(EmbeddingProvider): ...
```

Select them in `infrastructure/ai/factory.py`. Application code remains
unchanged.
