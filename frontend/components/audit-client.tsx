"use client";

import { useEffect, useState } from "react";

import {
  ErrorBanner,
  PageHeader,
  Panel,
} from "@/components/ui";
import { api } from "@/lib/api";
import type { AuditEvent } from "@/lib/types";

export function AuditClient() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .audits()
      .then(setEvents)
      .catch((reason: Error) =>
        setError(reason.message)
      );
  }, []);

  return (
    <>
      <PageHeader
        title="Audit Trail"
        subtitle={
          "A traceable record of classifications, policy " +
          "decisions, approvals, and external actions."
        }
      />
      {error ? <ErrorBanner message={error} /> : null}
      <Panel>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Event</th>
                <th>Actor</th>
                <th>Context</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={event.id}>
                  <td>
                    {new Date(
                      event.created_at
                    ).toLocaleString()}
                  </td>
                  <td>
                    <strong>
                      {event.event_type.replaceAll("_", " ")}
                    </strong>
                  </td>
                  <td>{event.actor}</td>
                  <td>
                    <code>
                      {JSON.stringify(event.details)}
                    </code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {events.length === 0 ? (
            <p className="empty-state">
              Audit events will appear after a customer
              interaction.
            </p>
          ) : null}
        </div>
      </Panel>
    </>
  );
}
