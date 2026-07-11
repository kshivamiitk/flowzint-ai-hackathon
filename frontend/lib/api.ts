import type {
  Action,
  AuditEvent,
  ChatResponse,
  Customer,
  DashboardMetrics,
  Incident,
  Transaction,
} from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000/api/v1";

async function request<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const payload = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(payload.detail ?? "Request failed");
  }
  return response.json() as Promise<T>;
}

export const api = {
  customers: () => request<Customer[]>("/customers"),
  transactions: (customerId?: string) =>
    request<Transaction[]>(
      `/transactions${
        customerId ? `?customer_id=${customerId}` : ""
      }`
    ),
  metrics: () =>
    request<DashboardMetrics>("/dashboard/metrics"),
  incidents: () => request<Incident[]>("/incidents"),
  actions: (status?: string) =>
    request<Action[]>(
      `/actions${status ? `?status=${status}` : ""}`
    ),
  audits: () =>
    request<AuditEvent[]>("/audit-events?limit=100"),
  sendMessage: (customerId: string, message: string) =>
    request<ChatResponse>("/chat/messages", {
      method: "POST",
      body: JSON.stringify({
        customer_id: customerId,
        message,
      }),
    }),
  approveAction: (
    id: string,
    comment = "Evidence verified by operator"
  ) =>
    request<Action>(`/actions/${id}/approve`, {
      method: "POST",
      body: JSON.stringify({ comment }),
    }),
  rejectAction: (
    id: string,
    comment = "Rejected by operator"
  ) =>
    request<Action>(`/actions/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ comment }),
    }),
};
