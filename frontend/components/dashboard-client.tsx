"use client";

import {
  ArrowRight,
  Bot,
  CheckCircle2,
  Database,
  Radar,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import {
  ErrorBanner,
  MetricCard,
  PageHeader,
  Panel,
  StatusBadge,
  SuccessBanner,
} from "@/components/ui";
import { api } from "@/lib/api";
import type { DashboardMetrics, HealthStatus, Incident } from "@/lib/types";

const workflow = [
  ["Understand", "AI classifies English, Hindi, and Hinglish requests."],
  ["Verify", "Customer and transaction facts come from the database."],
  ["Ground", "Relevant support policy is retrieved as evidence."],
  ["Authorize", "Deterministic rules calculate the permitted action."],
  ["Act", "Safe refunds execute; sensitive cases wait for approval."],
  ["Detect", "Related complaints become an operational incident."],
];

const roadmap = [
  "Connect payment, order, and CRM adapters behind existing ports.",
  "Add identity and role-based access for agents and approvers.",
  "Move action execution and notifications onto durable queues.",
  "Add production observability, retention controls, and reconciliation.",
];

export function DashboardClient() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [resetting, setResetting] = useState(false);

  async function load() {
    const [nextMetrics, nextIncidents, nextHealth] = await Promise.all([
      api.metrics(),
      api.incidents(),
      api.health(),
    ]);
    setMetrics(nextMetrics);
    setIncidents(nextIncidents);
    setHealth(nextHealth);
  }

  useEffect(() => {
    Promise.all([api.metrics(), api.incidents(), api.health()])
      .then(([nextMetrics, nextIncidents, nextHealth]) => {
        setMetrics(nextMetrics);
        setIncidents(nextIncidents);
        setHealth(nextHealth);
      })
      .catch((reason: Error) => setError(reason.message));
  }, []);

  async function resetDemo() {
    try {
      setResetting(true);
      setError("");
      const result = await api.resetDemo();
      await load();
      setNotice(result.message);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to reset demo");
    } finally {
      setResetting(false);
    }
  }

  return (
    <>
      <PageHeader
        title="Resolution Command Center"
        subtitle="One operational view for customer resolutions, protected actions, and cross-customer incident intelligence."
        actions={
          <button
            className="secondary-button button-with-icon"
            type="button"
            disabled={resetting}
            onClick={() => void resetDemo()}
          >
            <RotateCcw aria-hidden="true" size={17} />
            {resetting ? "Resetting" : "Reset demo"}
          </button>
        }
      />
      {error ? <ErrorBanner message={error} /> : null}
      {notice ? <SuccessBanner message={notice} /> : null}

      <section className="command-summary">
        <div className="command-summary-copy">
          <span className="summary-icon">
            <Zap aria-hidden="true" size={22} />
          </span>
          <div>
            <p className="section-kicker">CUSTOMER CARE BOT</p>
            <h3>Resolve the customer. Protect the business. Detect the incident.</h3>
            <p>
              PulseResolve combines conversational AI with verified data and
              deterministic controls, so automation remains explainable.
            </p>
          </div>
        </div>
        <div className="command-status">
          <div>
            <CheckCircle2 aria-hidden="true" size={17} />
            <span><small>Platform</small><strong>{health ? "Operational" : "Checking"}</strong></span>
          </div>
          <div>
            <Sparkles aria-hidden="true" size={17} />
            <span><small>AI mode</small><strong>{health?.ai_provider.replaceAll("_", " ") ?? "Checking"}</strong></span>
          </div>
          <div>
            <Database aria-hidden="true" size={17} />
            <span><small>Database</small><strong>{health?.database ?? "Checking"}</strong></span>
          </div>
        </div>
      </section>

      <div className="metric-grid">
        <MetricCard
          label="Customers"
          value={metrics?.customers ?? "—"}
          detail="Verified synthetic profiles"
        />
        <MetricCard
          label="Analyzed conversations"
          value={metrics?.conversations ?? "—"}
          detail="Including incident evidence"
        />
        <MetricCard
          label="Open incidents"
          value={metrics?.open_incidents ?? "—"}
          detail="Cross-customer patterns"
        />
        <MetricCard
          label="Protected actions"
          value={metrics?.pending_approvals ?? "—"}
          detail="Waiting for human review"
        />
        <MetricCard
          label="Automation rate"
          value={metrics ? `${metrics.automation_rate}%` : "—"}
          detail="Completed actions / proposed actions"
        />
      </div>

      <section className="workflow-section">
        <div className="section-heading-row">
          <div>
            <p className="section-kicker">HOW IT WORKS</p>
            <h3>Evidence-to-action workflow</h3>
          </div>
          <p className="muted">The language model never authorizes money movement.</p>
        </div>
        <div className="workflow-grid">
          {workflow.map(([label, detail], index) => (
            <div className="workflow-step" key={label}>
              <span>{index + 1}</span>
              <strong>{label}</strong>
              <p>{detail}</p>
              {index < workflow.length - 1 ? (
                <ArrowRight aria-hidden="true" size={15} />
              ) : null}
            </div>
          ))}
        </div>
      </section>

      <div className="two-column dashboard-columns">
        <Panel title="Three-minute demonstration">
          <div className="demo-path">
            <div>
              <Bot aria-hidden="true" size={18} />
              <span><strong>Automatic resolution</strong><small>₹449 refund executed from verified evidence.</small></span>
            </div>
            <div>
              <ShieldCheck aria-hidden="true" size={18} />
              <span><strong>Protected approval</strong><small>₹1,499 action waits for an operator.</small></span>
            </div>
            <div>
              <Radar aria-hidden="true" size={18} />
              <span><strong>Incident intelligence</strong><small>Related complaints reveal a shared failure.</small></span>
            </div>
          </div>
          <Link className="primary-button inline-button button-with-icon" href="/chat">
            Start guided demo
            <ArrowRight aria-hidden="true" size={17} />
          </Link>
        </Panel>

        <Panel title="Live operational signal">
          {incidents.length === 0 ? (
            <div className="empty-state compact-empty-state">
              <Radar aria-hidden="true" size={25} />
              <span>The next matching complaint will trigger the seeded incident.</span>
            </div>
          ) : (
            <div className="stack">
              {incidents.slice(0, 3).map((incident) => (
                <div key={incident.id} className="incident-summary-row">
                  <div>
                    <strong>{incident.title}</strong>
                    <p>{incident.probable_root_cause}</p>
                    <small>{incident.affected_customer_count} affected · {Math.round(incident.confidence * 100)}% confidence</small>
                  </div>
                  <StatusBadge value={incident.status} />
                </div>
              ))}
              <Link className="text-link" href="/incidents">
                Open incident intelligence <ArrowRight aria-hidden="true" size={15} />
              </Link>
            </div>
          )}
        </Panel>
      </div>

      <Panel title="Production roadmap">
        <div className="roadmap-grid">
          {roadmap.map((priority, index) => (
            <div className="roadmap-item" key={priority}>
              <span>{index + 1}</span>
              <p>{priority}</p>
            </div>
          ))}
        </div>
      </Panel>
    </>
  );
}
