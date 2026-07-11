"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  ErrorBanner,
  PageHeader,
  Panel,
  StatusBadge,
} from "@/components/ui";
import { api } from "@/lib/api";
import type {
  ChatResponse,
  Customer,
  Transaction,
} from "@/lib/types";

const SUGGESTED =
  "Bhai payment deduct ho gaya but order confirm nahi hua.";

type Message = {
  role: "customer" | "assistant";
  text: string;
  result?: ChatResponse;
};

export function ChatClient() {
  const [customers, setCustomers] =
    useState<Customer[]>([]);
  const [customerId, setCustomerId] =
    useState("cust-kumar");
  const [transactions, setTransactions] =
    useState<Transaction[]>([]);
  const [input, setInput] = useState(SUGGESTED);
  const [messages, setMessages] =
    useState<Message[]>([]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .customers()
      .then(setCustomers)
      .catch((reason: Error) =>
        setError(reason.message)
      );
  }, []);

  useEffect(() => {
    api
      .transactions(customerId)
      .then(setTransactions)
      .catch((reason: Error) =>
        setError(reason.message)
      );
  }, [customerId]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!input.trim() || sending) {
      return;
    }

    const outgoing = input.trim();
    setMessages((items) => [
      ...items,
      { role: "customer", text: outgoing },
    ]);
    setInput("");
    setSending(true);
    setError("");

    try {
      const result = await api.sendMessage(
        customerId,
        outgoing
      );
      setMessages((items) => [
        ...items,
        {
          role: "assistant",
          text: result.message,
          result,
        },
      ]);
      setTransactions(
        await api.transactions(customerId)
      );
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unable to send message"
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <PageHeader
        title="Customer Chat"
        subtitle={
          "Grounded answers, deterministic policy " +
          "checks, and verifiable actions."
        }
      />
      {error ? <ErrorBanner message={error} /> : null}
      <div className="chat-layout">
        <Panel title="Conversation">
          <div className="form-row">
            <label>
              Demo customer
              <select
                value={customerId}
                onChange={(event) =>
                  setCustomerId(event.target.value)
                }
              >
                {customers.map((customer) => (
                  <option
                    key={customer.id}
                    value={customer.id}
                  >
                    {customer.name}
                  </option>
                ))}
              </select>
            </label>
            <button
              className="secondary-button"
              onClick={() => setInput(SUGGESTED)}
            >
              Use demo message
            </button>
          </div>

          <div className="chat-window">
            {messages.length === 0 ? (
              <p className="empty-state">
                Start with the suggested
                failed-payment message.
              </p>
            ) : null}

            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={
                  `bubble bubble-${message.role}`
                }
              >
                <strong>
                  {message.role === "customer"
                    ? "Customer"
                    : "PulseResolve"}
                </strong>
                <p>{message.text}</p>
                {message.result ? (
                  <div className="result-card">
                    <div className="badge-row">
                      <StatusBadge
                        value={message.result.intent}
                      />
                      <StatusBadge
                        value={message.result.severity}
                      />
                    </div>
                    <p>
                      <strong>Confidence:</strong>
                      {" "}
                      {Math.round(
                        message.result.confidence * 100
                      )}
                      %
                    </p>
                    <p>
                      <strong>Sources:</strong>
                      {" "}
                      {message.result.policy_references
                        .map(
                          (item) =>
                            `${item.title} §${item.section}`
                        )
                        .join(", ")}
                    </p>
                    {message.result.action ? (
                      <p>
                        <strong>Action:</strong>
                        {" "}
                        {
                          message.result.action
                            .action_type
                        }
                        {" — "}
                        <StatusBadge
                          value={
                            message.result.action.status
                          }
                        />
                      </p>
                    ) : null}
                    {message.result.incident ? (
                      <p>
                        <strong>Incident:</strong>
                        {" "}
                        {
                          message.result.incident.title
                        }
                        {" ("}
                        {
                          message.result.incident
                            .affected_customer_count
                        }
                        {" customers)"}
                      </p>
                    ) : null}
                  </div>
                ) : null}
              </div>
            ))}
          </div>

          <form
            onSubmit={submit}
            className="composer"
          >
            <textarea
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              rows={3}
              placeholder="Describe the customer issue…"
            />
            <button
              className="primary-button"
              disabled={sending}
            >
              {sending
                ? "Resolving…"
                : "Send and resolve"}
            </button>
          </form>
        </Panel>

        <Panel title="Verified customer context">
          {transactions.map((transaction) => (
            <div
              key={transaction.id}
              className="context-card"
            >
              <div className="list-row">
                <strong>
                  {transaction.order_reference}
                </strong>
                <StatusBadge
                  value={transaction.status}
                />
              </div>
              <dl>
                <dt>Amount</dt>
                <dd>₹{transaction.amount}</dd>
                <dt>Payment</dt>
                <dd>{transaction.payment_method}</dd>
                <dt>App version</dt>
                <dd>{transaction.app_version}</dd>
                <dt>Error</dt>
                <dd>
                  {transaction.error_code ?? "None"}
                </dd>
              </dl>
            </div>
          ))}
        </Panel>
      </div>
    </>
  );
}
