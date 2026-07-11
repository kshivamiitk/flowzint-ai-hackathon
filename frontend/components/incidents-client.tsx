"use client";

import { useEffect, useState } from "react";

import {
  ErrorBanner,
  PageHeader,
  Panel,
  StatusBadge,
} from "@/components/ui";
import { api } from "@/lib/api";
import type { Incident } from "@/lib/types";

export function IncidentsClient() {
  const [items, setItems] =
    useState<Incident[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .incidents()
      .then(setItems)
      .catch((reason: Error) =>
        setError(reason.message)
      );
  }, []);

  return (
    <>
      <PageHeader
        title="Incident Intelligence"
        subtitle={
          "Semantically related complaints grouped " +
          "into operational incidents."
        }
      />
      {error ? <ErrorBanner message={error} /> : null}
      <div className="stack">
        {items.length === 0 ? (
          <Panel>
            <p className="empty-state">
              No incident yet. Send the Kumar demo
              message to cross the threshold.
            </p>
          </Panel>
        ) : null}

        {items.map((incident) => (
          <Panel key={incident.id}>
            <div className="list-row">
              <div>
                <h3>{incident.title}</h3>
                <p className="muted">
                  {incident.description}
                </p>
              </div>
              <StatusBadge
                value={incident.status}
              />
            </div>

            <div className="incident-grid">
              <div>
                <span className="muted">
                  Affected customers
                </span>
                <strong>
                  {
                    incident
                      .affected_customer_count
                  }
                </strong>
              </div>
              <div>
                <span className="muted">
                  Confidence
                </span>
                <strong>
                  {Math.round(
                    incident.confidence * 100
                  )}
                  %
                </strong>
              </div>
              <div>
                <span className="muted">
                  Probable root cause
                </span>
                <strong>
                  {
                    incident
                      .probable_root_cause
                  }
                </strong>
              </div>
            </div>

            <h4>Evidence</h4>
            <ul>
              {incident.evidence.map((evidence) => (
                <li key={evidence}>{evidence}</li>
              ))}
            </ul>
          </Panel>
        ))}
      </div>
    </>
  );
}
