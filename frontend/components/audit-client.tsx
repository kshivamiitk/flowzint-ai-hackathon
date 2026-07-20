"use client";

import {
  Bot,
  CheckCircle2,
  ClipboardCheck,
  Radar,
  ScrollText,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { ErrorBanner, PageHeader, Panel } from "@/components/ui";
import { api } from "@/lib/api";
import type { AuditEvent } from "@/lib/types";

const filters = [
  ["all", "All events"],
  ["ai", "AI decisions"],
  ["action", "Actions"],
  ["incident", "Incidents"],
];

function category(event: AuditEvent) {
  if (event.event_type.includes("incident")) return "incident";
  if (event.event_type === "complaint_classified") return "ai";
  return "action";
}

function label(event: AuditEvent) {
  const labels: Record<string, string> = {
    complaint_classified: "Complaint classified",
    refund_completed: "Refund completed",
    action_approval_requested: "Approval requested",
    action_rejected_by_operator: "Action rejected",
    action_rejected_by_policy: "Action blocked by policy",
    incident_detected: "Incident detected",
    incident_status_changed: "Incident status changed",
  };
  return labels[event.event_type] ?? event.event_type.replaceAll("_", " ");
}

function summary(event: AuditEvent) {
  const details = event.details;
  if (event.event_type === "complaint_classified") {
    return `${String(details.intent ?? "Request").replaceAll("_", " ")} · ${Math.round(Number(details.confidence ?? 0) * 100)}% confidence`;
  }
  if (event.event_type === "refund_completed") {
    return `₹${Number(details.amount ?? 0).toLocaleString("en-IN")} sent for ${String(details.transaction_id ?? "verified transaction")}`;
  }
  if (event.event_type === "action_approval_requested") {
    return `${String(details.mode ?? "protected").replaceAll("_", " ")} · ${String(details.policy_reference ?? "policy verified")}`;
  }
  if (event.event_type === "incident_detected") {
    return `${String(details.related_complaints ?? 0)} related complaints · ${Math.round(Number(details.confidence ?? 0) * 100)}% confidence`;
  }
  if (event.event_type === "incident_status_changed") {
    return `${String(details.from ?? "detected")} → ${String(details.to ?? "updated")}`;
  }
  return String(details.reason ?? details.comment ?? "Recorded business event");
}

function EventIcon({ event }: { event: AuditEvent }) {
  const kind = category(event);
  if (kind === "incident") return <Radar aria-hidden="true" size={17} />;
  if (kind === "ai") return <Bot aria-hidden="true" size={17} />;
  if (event.event_type === "refund_completed") {
    return <CheckCircle2 aria-hidden="true" size={17} />;
  }
  return <ClipboardCheck aria-hidden="true" size={17} />;
}

export function AuditClient() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [activeFilter, setActiveFilter] = useState("all");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .audits()
      .then(setEvents)
      .catch((reason: Error) => setError(reason.message));
  }, []);

  const visibleEvents = useMemo(
    () =>
      activeFilter === "all"
        ? events
        : events.filter((event) => category(event) === activeFilter),
    [activeFilter, events]
  );

  return (
    <>
      <PageHeader
        title="Explainable Audit Trail"
        subtitle="A human-readable record of AI classifications, policy decisions, approvals, actions, and incident changes."
        actions={
          <div className="queue-count">
            <ScrollText aria-hidden="true" size={17} />
            <strong>{events.length}</strong>
            <span>events</span>
          </div>
        }
      />
      {error ? <ErrorBanner message={error} /> : null}

      <section className="audit-assurance">
        <ShieldCheck aria-hidden="true" size={20} />
        <span><strong>Traceability by design</strong><small>Every material state change records the actor, evidence, timestamp, and linked workflow identifiers.</small></span>
      </section>

      <div className="filter-tabs" role="tablist" aria-label="Audit event filters">
        {filters.map(([value, text]) => (
          <button
            key={value}
            type="button"
            role="tab"
            aria-selected={activeFilter === value}
            className={activeFilter === value ? "filter-tab filter-tab-active" : "filter-tab"}
            onClick={() => setActiveFilter(value)}
          >
            {text}
            <span>{value === "all" ? events.length : events.filter((event) => category(event) === value).length}</span>
          </button>
        ))}
      </div>

      <Panel>
        {visibleEvents.length === 0 ? (
          <div className="empty-state approval-empty-state">
            <ScrollText aria-hidden="true" size={30} />
            <strong>No events in this view</strong>
            <span>Run a guided resolution to produce classification, action, and incident evidence.</span>
          </div>
        ) : (
          <div className="audit-timeline">
            {visibleEvents.map((event) => (
              <article className="audit-event" key={event.id}>
                <div className={`audit-icon audit-icon-${category(event)}`}>
                  <EventIcon event={event} />
                </div>
                <div className="audit-event-copy">
                  <div className="audit-event-heading">
                    <div>
                      <strong>{label(event)}</strong>
                      <p>{summary(event)}</p>
                    </div>
                    <time dateTime={event.created_at}>{new Date(event.created_at).toLocaleString()}</time>
                  </div>
                  <div className="audit-meta">
                    <span>Actor <b>{event.actor.replaceAll("_", " ")}</b></span>
                    {event.action_id ? <span>Action <code>{event.action_id.slice(0, 8)}</code></span> : null}
                    {event.conversation_id ? <span>Conversation <code>{event.conversation_id.slice(0, 8)}</code></span> : null}
                  </div>
                  <details>
                    <summary>Inspect recorded evidence</summary>
                    <pre>{JSON.stringify(event.details, null, 2)}</pre>
                  </details>
                </div>
              </article>
            ))}
          </div>
        )}
      </Panel>
    </>
  );
}
