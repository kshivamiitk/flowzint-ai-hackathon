"use client";

import { useEffect, useState } from "react";

import {
  ErrorBanner,
  PageHeader,
  Panel,
  StatusBadge,
} from "@/components/ui";
import { api } from "@/lib/api";
import type { Action } from "@/lib/types";

export function ApprovalsClient() {
  const [actions, setActions] = useState<Action[]>([]);
  const [comment, setComment] = useState(
    "Evidence and policy reference verified by operator"
  );
  const [workingId, setWorkingId] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try {
      setError("");
      setActions(await api.actions("awaiting_approval"));
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unable to load approvals"
      );
    }
  }

  useEffect(() => {
    api
      .actions("awaiting_approval")
      .then(setActions)
      .catch((reason: Error) =>
        setError(reason.message)
      );
  }, []);

  async function review(
    action: Action,
    decision: "approve" | "reject"
  ) {
    try {
      setWorkingId(action.id);
      setError("");
      if (decision === "approve") {
        await api.approveAction(action.id, comment);
      } else {
        await api.rejectAction(action.id, comment);
      }
      await load();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unable to review action"
      );
    } finally {
      setWorkingId("");
    }
  }

  return (
    <>
      <PageHeader
        title="Human Approval Queue"
        subtitle={
          "Sensitive actions remain blocked until an operator " +
          "verifies the evidence and policy rule."
        }
      />
      {error ? <ErrorBanner message={error} /> : null}
      <Panel>
        <label className="full-width-label">
          Reviewer comment
          <input
            value={comment}
            onChange={(event) =>
              setComment(event.target.value)
            }
          />
        </label>
      </Panel>
      <div className="stack">
        {actions.length === 0 ? (
          <Panel>
            <p className="empty-state">
              No actions are waiting for approval. Send a
              failed-payment message for the ₹1,499 demo
              transaction to create one.
            </p>
          </Panel>
        ) : (
          actions.map((action) => (
            <Panel key={action.id}>
              <div className="approval-card">
                <div>
                  <div className="badge-row">
                    <StatusBadge value={action.action_type} />
                    <StatusBadge value={action.status} />
                  </div>
                  <h3>
                    Refund recommendation: ₹{action.amount}
                  </h3>
                  <p>{action.reason}</p>
                  <dl className="detail-grid">
                    <dt>Transaction</dt>
                    <dd>{action.transaction_id ?? "Not linked"}</dd>
                    <dt>Policy</dt>
                    <dd>{action.policy_reference}</dd>
                    <dt>Created</dt>
                    <dd>
                      {new Date(
                        action.created_at
                      ).toLocaleString()}
                    </dd>
                  </dl>
                </div>
                <div className="action-buttons">
                  <button
                    className="primary-button"
                    disabled={workingId === action.id}
                    onClick={() =>
                      void review(action, "approve")
                    }
                  >
                    Approve and execute
                  </button>
                  <button
                    className="danger-button"
                    disabled={workingId === action.id}
                    onClick={() =>
                      void review(action, "reject")
                    }
                  >
                    Reject
                  </button>
                </div>
              </div>
            </Panel>
          ))
        )}
      </div>
    </>
  );
}
