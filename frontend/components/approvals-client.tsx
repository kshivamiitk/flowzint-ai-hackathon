"use client";

import {
  ArrowRight,
  Check,
  ClipboardCheck,
  FileCheck2,
  ShieldAlert,
  X,
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
import type { Action } from "@/lib/types";

function formatCurrency(amount: number) {
  return `₹${amount.toLocaleString("en-IN")}`;
}

function reviewTier(action: Action) {
  return action.amount > 2000
    ? { label: "Escalated human review", risk: "high" }
    : { label: "Standard policy approval", risk: "medium" };
}

export function ApprovalsClient() {
  const [actions, setActions] = useState<Action[]>([]);
  const [comment, setComment] = useState(
    "Verified transaction evidence and applicable refund policy."
  );
  const [workingId, setWorkingId] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    setActions(await api.actions("awaiting_approval"));
  }

  useEffect(() => {
    api
      .actions("awaiting_approval")
      .then(setActions)
      .catch((reason: Error) => setError(reason.message));
  }, []);

  async function review(action: Action, decision: "approve" | "reject") {
    try {
      setWorkingId(action.id);
      setError("");
      setNotice("");
      if (decision === "approve") {
        await api.approveAction(action.id, comment);
        setNotice(`${formatCurrency(action.amount)} refund approved and executed.`);
      } else {
        await api.rejectAction(action.id, comment);
        setNotice(`${formatCurrency(action.amount)} recommendation rejected safely.`);
      }
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to review action");
    } finally {
      setWorkingId("");
    }
  }

  return (
    <>
      <PageHeader
        title="Human Approval Queue"
        subtitle="Review verified evidence before a sensitive customer-care action can change business state."
        actions={
          <div className="queue-count">
            <ClipboardCheck aria-hidden="true" size={17} />
            <strong>{actions.length}</strong>
            <span>pending</span>
          </div>
        }
      />
      {error ? <ErrorBanner message={error} /> : null}
      {notice ? <SuccessBanner message={notice} /> : null}

      <section className="review-principle">
        <ShieldAlert aria-hidden="true" size={20} />
        <div>
          <strong>Human-in-the-loop control</strong>
          <p>
            AI supplies classification and evidence. Policy selects the review
            tier. Only the operator can release a protected action.
          </p>
        </div>
      </section>

      <Panel title="Reviewer evidence note">
        <label className="full-width-label">
          This note becomes part of the immutable audit record
          <input value={comment} onChange={(event) => setComment(event.target.value)} />
        </label>
      </Panel>

      <div className="stack approval-stack">
        {actions.length === 0 ? (
          <Panel>
            <div className="empty-state approval-empty-state">
              <FileCheck2 aria-hidden="true" size={30} />
              <strong>Approval queue is clear</strong>
              <span>Run the ₹1,499 or ₹3,299 guided scenario to create a protected action.</span>
              <Link className="primary-button button-with-icon" href="/chat">
                Open resolution console
                <ArrowRight aria-hidden="true" size={16} />
              </Link>
            </div>
          </Panel>
        ) : (
          actions.map((action) => {
            const tier = reviewTier(action);
            return (
              <Panel key={action.id}>
                <div className="approval-card">
                  <div className="approval-evidence">
                    <div className="approval-heading">
                      <div>
                        <p className="section-kicker">REFUND RECOMMENDATION</p>
                        <h3>{formatCurrency(action.amount)}</h3>
                      </div>
                      <div className="badge-row">
                        <StatusBadge value={tier.risk} />
                        <StatusBadge value={action.status} />
                      </div>
                    </div>
                    <p className="approval-reason">{action.reason}</p>
                    <div className="approval-facts">
                      <div><span>Review tier</span><strong>{tier.label}</strong></div>
                      <div><span>Transaction</span><strong>{action.transaction_id ?? "Not linked"}</strong></div>
                      <div><span>Policy authority</span><strong>{action.policy_reference}</strong></div>
                      <div><span>Requested</span><strong>{new Date(action.created_at).toLocaleString()}</strong></div>
                    </div>
                  </div>
                  <div className="action-buttons">
                    <button
                      className="primary-button button-with-icon"
                      disabled={workingId === action.id || !comment.trim()}
                      onClick={() => void review(action, "approve")}
                    >
                      <Check aria-hidden="true" size={17} />
                      Approve and execute
                    </button>
                    <button
                      className="danger-button button-with-icon"
                      disabled={workingId === action.id || !comment.trim()}
                      onClick={() => void review(action, "reject")}
                    >
                      <X aria-hidden="true" size={17} />
                      Reject action
                    </button>
                    <small>Both decisions are recorded in the audit trail.</small>
                  </div>
                </div>
              </Panel>
            );
          })
        )}
      </div>
    </>
  );
}
