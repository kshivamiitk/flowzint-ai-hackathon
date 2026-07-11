"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  ErrorBanner,
  MetricCard,
  PageHeader,
  Panel,
  StatusBadge,
} from "@/components/ui";
import { api } from "@/lib/api";
import type {
  DashboardMetrics,
  Incident,
} from "@/lib/types";

export function DashboardClient() {
  const [metrics, setMetrics] =
    useState<DashboardMetrics | null>(null);
  const [incidents, setIncidents] =
    useState<Incident[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.metrics(), api.incidents()])
      .then(([nextMetrics, nextIncidents]) => {
        setMetrics(nextMetrics);
        setIncidents(nextIncidents);
      })
      .catch((reason: Error) =>
        setError(reason.message)
      );
  }, []);

  return (
    <>
      <PageHeader
        title="Operations Overview"
        subtitle={
          "Customer resolution, safe actions, and " +
          "incident intelligence in one workspace."
        }
      />
      {error ? <ErrorBanner message={error} /> : null}
      <div className="metric-grid">
        <MetricCard
          label="Conversations"
          value={metrics?.conversations ?? "—"}
          detail="Analyzed support conversations"
        />
        <MetricCard
          label="Open incidents"
          value={metrics?.open_incidents ?? "—"}
          detail="Cross-customer patterns"
        />
        <MetricCard
          label="Pending approvals"
          value={metrics?.pending_approvals ?? "—"}
          detail="Human review required"
        />
        <MetricCard
          label="Completed actions"
          value={metrics?.completed_actions ?? "—"}
          detail="Verified business actions"
        />
        <MetricCard
          label="Automation rate"
          value={
            metrics
              ? `${metrics.automation_rate}%`
              : "—"
          }
          detail="Completed actions / all actions"
        />
      </div>
      <div className="two-column">
        <Panel title="Live demo path">
          <ol className="demo-list">
            <li>
              Open Customer Chat and select
              Kumar Shivam.
            </li>
            <li>
              Send the suggested failed-payment
              message.
            </li>
            <li>
              Watch an automatic refund complete.
            </li>
            <li>
              Inspect the newly detected incident.
            </li>
          </ol>
          <Link
            className="primary-button inline-button"
            href="/chat"
          >
            Start demo
          </Link>
        </Panel>
        <Panel title="Recent incidents">
          {incidents.length === 0 ? (
            <p className="muted">
              No incident yet. The third related
              complaint will create one.
            </p>
          ) : (
            <div className="stack">
              {incidents.slice(0, 3).map((incident) => (
                <div
                  key={incident.id}
                  className="list-row"
                >
                  <div>
                    <strong>{incident.title}</strong>
                    <p className="muted">
                      {incident.affected_customer_count}
                      {" "}affected customers
                    </p>
                  </div>
                  <StatusBadge
                    value={incident.status}
                  />
                </div>
              ))}
            </div>
          )}
        </Panel>
      </div>
    </>
  );
}
