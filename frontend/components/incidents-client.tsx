"use client";

import {
  ArrowRight,
  CheckCircle2,
  CircleDot,
  Radar,
  SearchCheck,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import {
  ErrorBanner,
  PageHeader,
  Panel,
  StatusBadge,
  SuccessBanner,
} from "@/components/ui";
import { api } from "@/lib/api";
import type { Incident } from "@/lib/types";

export function IncidentsClient() {
  const [items, setItems] = useState<Incident[]>([]);
  const [workingId, setWorkingId] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    setItems(await api.incidents());
  }

  useEffect(() => {
    api
      .incidents()
      .then(setItems)
      .catch((reason: Error) => setError(reason.message));
  }, []);

  async function moveIncident(incident: Incident, status: string) {
    try {
      setWorkingId(incident.id);
      setError("");
      setNotice("");
      await api.updateIncident(incident.id, status);
      await load();
      setNotice(`${incident.title} moved to ${status.replaceAll("_", " ")}.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to update incident");
    } finally {
      setWorkingId("");
    }
  }

  return (
    <>
      <PageHeader
        title="Incident Intelligence"
        subtitle="Turn repeated customer complaints into an explainable operational signal with shared technical evidence."
        actions={
          <div className="queue-count">
            <Radar aria-hidden="true" size={17} />
            <strong>{items.filter((item) => item.status !== "resolved").length}</strong>
            <span>open</span>
          </div>
        }
      />
      {error ? <ErrorBanner message={error} /> : null}
      {notice ? <SuccessBanner message={notice} /> : null}

      <section className="incident-method">
        <div><CircleDot aria-hidden="true" size={17} /><span><small>Signal</small><strong>Semantic similarity</strong></span></div>
        <div><SearchCheck aria-hidden="true" size={17} /><span><small>Threshold</small><strong>3 related complaints / 60 min</strong></span></div>
        <div><ShieldCheck aria-hidden="true" size={17} /><span><small>Evidence</small><strong>Error, version, payment rail</strong></span></div>
      </section>

      <div className="stack incident-stack">
        {items.length === 0 ? (
          <Panel>
            <div className="empty-state approval-empty-state">
              <Radar aria-hidden="true" size={30} />
              <strong>No active incident</strong>
              <span>The automatic-resolution scenario adds the third matching complaint and creates an incident.</span>
              <Link className="primary-button button-with-icon" href="/chat">
                Trigger guided scenario
                <ArrowRight aria-hidden="true" size={16} />
              </Link>
            </div>
          </Panel>
        ) : null}

        {items.map((incident) => (
          <Panel key={incident.id}>
            <div className="incident-heading">
              <div>
                <p className="section-kicker">CROSS-CUSTOMER SIGNAL</p>
                <h3>{incident.title}</h3>
                <p>{incident.description}</p>
              </div>
              <StatusBadge value={incident.status} />
            </div>

            <div className="incident-grid">
              <div><span className="muted">Affected customers</span><strong>{incident.affected_customer_count}</strong></div>
              <div><span className="muted">Detection confidence</span><strong>{Math.round(incident.confidence * 100)}%</strong></div>
              <div><span className="muted">Probable root cause</span><strong>{incident.probable_root_cause}</strong></div>
            </div>

            <div className="incident-lower-grid">
              <div>
                <h4>Correlated evidence</h4>
                <ul className="evidence-points">
                  {incident.evidence.map((evidence) => (
                    <li key={evidence}><CheckCircle2 aria-hidden="true" size={16} />{evidence}</li>
                  ))}
                </ul>
              </div>
              <div className="incident-actions">
                <h4>Operations response</h4>
                {incident.status === "detected" ? (
                  <button
                    className="primary-button button-with-icon"
                    disabled={workingId === incident.id}
                    onClick={() => void moveIncident(incident, "investigating")}
                  >
                    <SearchCheck aria-hidden="true" size={17} />
                    Begin investigation
                  </button>
                ) : null}
                {incident.status !== "resolved" ? (
                  <button
                    className="secondary-button button-with-icon"
                    disabled={workingId === incident.id}
                    onClick={() => void moveIncident(incident, "resolved")}
                  >
                    <CheckCircle2 aria-hidden="true" size={17} />
                    Mark resolved
                  </button>
                ) : (
                  <p className="resolved-note"><CheckCircle2 aria-hidden="true" size={17} /> Resolution recorded</p>
                )}
                <Link className="text-link" href="/audit">
                  View audit evidence <ArrowRight aria-hidden="true" size={15} />
                </Link>
              </div>
            </div>
          </Panel>
        ))}
      </div>
    </>
  );
}
