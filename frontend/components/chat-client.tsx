"use client";

import {
  ArrowRight,
  CheckCircle2,
  Database,
  FileCheck2,
  MessageSquareText,
  RefreshCw,
  RotateCcw,
  Send,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  ErrorBanner,
  PageHeader,
  Panel,
  StatusBadge,
  SuccessBanner,
} from "@/components/ui";
import { api } from "@/lib/api";
import type {
  ChatResponse,
  Customer,
  HealthStatus,
  Transaction,
} from "@/lib/types";

type Message = {
  role: "customer" | "assistant";
  text: string;
  result?: ChatResponse;
};

type DemoScenario = {
  id: string;
  label: string;
  customerId: string;
  message: string;
  amount: string;
  outcome: string;
  risk: string;
};

const scenarios: DemoScenario[] = [
  {
    id: "auto-refund",
    label: "Automatic resolution",
    customerId: "cust-kumar",
    message: "Bhai payment deduct ho gaya but order confirm nahi hua.",
    amount: "₹449",
    outcome: "Verify and execute refund",
    risk: "Low risk",
  },
  {
    id: "approval",
    label: "Human approval",
    customerId: "cust-aarav",
    message: "UPI charged me but the order was not created.",
    amount: "₹1,499",
    outcome: "Hold for operator approval",
    risk: "Medium risk",
  },
  {
    id: "human-review",
    label: "Protected escalation",
    customerId: "cust-neha",
    message: "Payment ho gaya lekin booking confirm nahi hui.",
    amount: "₹3,299",
    outcome: "Block automatic execution",
    risk: "High risk",
  },
];

function formatCurrency(amount: number) {
  return `₹${amount.toLocaleString("en-IN")}`;
}

function providerLabel(health: HealthStatus | null) {
  if (!health) return "Checking";
  return health.ai_provider === "local"
    ? "Local deterministic"
    : "Hosted + local fallback";
}

export function ChatClient() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState(scenarios[0].customerId);
  const [scenarioId, setScenarioId] = useState(scenarios[0].id);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [input, setInput] = useState(scenarios[0].message);
  const [messages, setMessages] = useState<Message[]>([]);
  const [sending, setSending] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const selectedScenario = useMemo(
    () => scenarios.find((item) => item.id === scenarioId) ?? scenarios[0],
    [scenarioId]
  );
  const latestResult = [...messages]
    .reverse()
    .find((message) => message.result)?.result;

  useEffect(() => {
    Promise.all([api.health(), api.customers()])
      .then(([nextHealth, nextCustomers]) => {
        setHealth(nextHealth);
        setCustomers(nextCustomers);
      })
      .catch((reason: Error) => setError(reason.message));
  }, []);

  useEffect(() => {
    api
      .transactions(customerId)
      .then(setTransactions)
      .catch((reason: Error) => setError(reason.message));
  }, [customerId]);

  function applyScenario(nextId: string) {
    const scenario =
      scenarios.find((item) => item.id === nextId) ?? scenarios[0];
    setScenarioId(scenario.id);
    setCustomerId(scenario.customerId);
    setInput(scenario.message);
    setMessages([]);
    setError("");
    setNotice("");
  }

  async function resetDemo() {
    try {
      setResetting(true);
      setError("");
      const result = await api.resetDemo();
      applyScenario(scenarios[0].id);
      setTransactions(await api.transactions(scenarios[0].customerId));
      setNotice(result.message);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to reset demo");
    } finally {
      setResetting(false);
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!input.trim() || sending) return;

    const outgoing = input.trim();
    setMessages((items) => [...items, { role: "customer", text: outgoing }]);
    setInput("");
    setSending(true);
    setError("");
    setNotice("");

    try {
      const result = await api.sendMessage(customerId, outgoing);
      setMessages((items) => [
        ...items,
        { role: "assistant", text: result.message, result },
      ]);
      setTransactions(await api.transactions(customerId));
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Unable to send message"
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <PageHeader
        title="Resolution Console"
        subtitle="Resolve a customer problem with verified context, grounded policy, guarded actions, and operational intelligence."
        actions={
          <button
            className="secondary-button button-with-icon"
            type="button"
            disabled={resetting || sending}
            onClick={() => void resetDemo()}
          >
            <RotateCcw aria-hidden="true" size={17} />
            {resetting ? "Resetting" : "Reset demo"}
          </button>
        }
      />
      {error ? <ErrorBanner message={error} /> : null}
      {notice ? <SuccessBanner message={notice} /> : null}

      <section className="runtime-strip" aria-label="Runtime status">
        <div>
          <span className="runtime-icon runtime-icon-success">
            <CheckCircle2 aria-hidden="true" size={18} />
          </span>
          <span>
            <small>Backend</small>
            <strong>{health?.status === "ok" ? "Connected" : "Checking"}</strong>
          </span>
        </div>
        <div>
          <span className="runtime-icon">
            <Sparkles aria-hidden="true" size={18} />
          </span>
          <span>
            <small>AI runtime</small>
            <strong>{providerLabel(health)}</strong>
          </span>
        </div>
        <div>
          <span className="runtime-icon">
            <Database aria-hidden="true" size={18} />
          </span>
          <span>
            <small>Evidence store</small>
            <strong>{health?.database ?? "Checking"}</strong>
          </span>
        </div>
        <div>
          <span className="runtime-icon">
            <ShieldCheck aria-hidden="true" size={18} />
          </span>
          <span>
            <small>Authorization</small>
            <strong>Deterministic policy</strong>
          </span>
        </div>
      </section>

      <section className="scenario-section" aria-labelledby="scenario-heading">
        <div className="section-heading-row">
          <div>
            <p className="section-kicker">GUIDED DEMO</p>
            <h3 id="scenario-heading">Choose a resolution path</h3>
          </div>
          <p className="muted">Three risk tiers. One governed workflow.</p>
        </div>
        <div className="scenario-grid">
          {scenarios.map((scenario, index) => (
            <button
              key={scenario.id}
              className={
                scenario.id === scenarioId
                  ? "scenario-card scenario-card-active"
                  : "scenario-card"
              }
              type="button"
              onClick={() => applyScenario(scenario.id)}
            >
              <span className="scenario-number">0{index + 1}</span>
              <span className="scenario-copy">
                <strong>{scenario.label}</strong>
                <small>{scenario.outcome}</small>
              </span>
              <span className="scenario-meta">
                <b>{scenario.amount}</b>
                <small>{scenario.risk}</small>
              </span>
              <ArrowRight aria-hidden="true" size={18} />
            </button>
          ))}
        </div>
      </section>

      {latestResult ? (
        <section className="trace-section" aria-labelledby="trace-heading">
          <div className="section-heading-row compact-heading">
            <div>
              <p className="section-kicker">EXPLAINABLE EXECUTION</p>
              <h3 id="trace-heading">Resolution trace</h3>
            </div>
            <div className="badge-row">
              <StatusBadge value={latestResult.decision_mode} />
              <StatusBadge value={`${latestResult.risk_level}_risk`} />
            </div>
          </div>
          <div className="resolution-trace">
            {latestResult.resolution_trace.map((step, index) => (
              <div className="trace-step" key={step.id}>
                <div className="trace-marker">
                  <span>{index + 1}</span>
                  {index < latestResult.resolution_trace.length - 1 ? (
                    <i aria-hidden="true" />
                  ) : null}
                </div>
                <div>
                  <div className="trace-title-row">
                    <strong>{step.label}</strong>
                    <StatusBadge value={step.status} />
                  </div>
                  <p>{step.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      <div className="chat-layout">
        <Panel title="Customer conversation">
          <div className="form-row">
            <label>
              Demo customer
              <select
                value={customerId}
                onChange={(event) => {
                  setCustomerId(event.target.value);
                  setScenarioId("");
                  setMessages([]);
                }}
              >
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name} · {customer.plan}
                  </option>
                ))}
              </select>
            </label>
            <button
              className="secondary-button icon-button"
              type="button"
              title="Restore scenario message"
              aria-label="Restore scenario message"
              onClick={() => setInput(selectedScenario.message)}
            >
              <RefreshCw aria-hidden="true" size={18} />
            </button>
          </div>

          <div className="chat-window" aria-live="polite">
            {messages.length === 0 ? (
              <div className="empty-state rich-empty-state">
                <MessageSquareText aria-hidden="true" size={28} />
                <strong>Ready for a customer issue</strong>
                <span>Send the prepared message to run the complete workflow.</span>
              </div>
            ) : null}
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`bubble bubble-${message.role}`}
              >
                <strong>
                  {message.role === "customer" ? "Customer" : "PulseResolve AI"}
                </strong>
                <p>{message.text}</p>
              </div>
            ))}
          </div>

          <form onSubmit={submit} className="composer">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              rows={3}
              placeholder="Describe the customer issue..."
              aria-label="Customer message"
            />
            <button
              className="primary-button button-with-icon composer-button"
              disabled={sending || !input.trim()}
            >
              {sending ? (
                <RefreshCw className="spin" aria-hidden="true" size={18} />
              ) : (
                <Send aria-hidden="true" size={18} />
              )}
              {sending ? "Resolving" : "Resolve issue"}
            </button>
          </form>
        </Panel>

        <div className="side-stack">
          <Panel title="Verified evidence">
            {transactions.length === 0 ? (
              <p className="muted">No verified transaction was found.</p>
            ) : null}
            {transactions.map((transaction) => (
              <div key={transaction.id} className="evidence-block">
                <div className="list-row">
                  <span>
                    <small className="muted">ORDER</small>
                    <strong>{transaction.order_reference}</strong>
                  </span>
                  <StatusBadge value={transaction.status} />
                </div>
                <dl className="evidence-list">
                  <dt>Amount</dt>
                  <dd>{formatCurrency(transaction.amount)}</dd>
                  <dt>Payment rail</dt>
                  <dd>{transaction.payment_method}</dd>
                  <dt>App version</dt>
                  <dd>{transaction.app_version}</dd>
                  <dt>Error signal</dt>
                  <dd>{transaction.error_code ?? "None"}</dd>
                </dl>
                <p className="verified-note">
                  <FileCheck2 aria-hidden="true" size={16} />
                  Loaded from the transaction store, not generated by AI.
                </p>
              </div>
            ))}
          </Panel>

          <Panel title="Decision and outcome">
            {latestResult ? (
              <div className="decision-stack">
                <div className="decision-summary">
                  <span>
                    <small>Classified intent</small>
                    <strong>{latestResult.intent.replaceAll("_", " ")}</strong>
                  </span>
                  <b>{Math.round(latestResult.confidence * 100)}%</b>
                </div>
                <dl className="evidence-list compact-list">
                  <dt>Language</dt>
                  <dd>{latestResult.language}</dd>
                  <dt>Risk tier</dt>
                  <dd><StatusBadge value={latestResult.risk_level} /></dd>
                  <dt>Decision</dt>
                  <dd><StatusBadge value={latestResult.decision_mode} /></dd>
                </dl>
                {latestResult.action ? (
                  <div className="outcome-block">
                    <small>ACTION OUTCOME</small>
                    <div className="list-row">
                      <strong>
                        {latestResult.action.action_type.replaceAll("_", " ")}
                      </strong>
                      <StatusBadge value={latestResult.action.status} />
                    </div>
                    <p>{latestResult.action.reason}</p>
                    {latestResult.action.external_reference ? (
                      <code>{latestResult.action.external_reference}</code>
                    ) : null}
                  </div>
                ) : null}
                <div className="policy-sources">
                  <small>POLICY EVIDENCE</small>
                  {latestResult.policy_references.map((item) => (
                    <span key={`${item.title}-${item.section}`}>
                      <ShieldCheck aria-hidden="true" size={15} />
                      {item.title} §{item.section}
                    </span>
                  ))}
                </div>
                {latestResult.incident ? (
                  <div className="incident-alert">
                    <TriangleAlert aria-hidden="true" size={18} />
                    <span>
                      <strong>{latestResult.incident.title}</strong>
                      <small>{latestResult.incident.description}</small>
                    </span>
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="empty-state compact-empty-state">
                <ShieldCheck aria-hidden="true" size={26} />
                <span>Policy evidence and action results will appear here.</span>
              </div>
            )}
          </Panel>
        </div>
      </div>
    </>
  );
}
