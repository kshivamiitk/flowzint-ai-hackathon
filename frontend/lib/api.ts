import type {
  Action,
  AuditEvent,
  ChatResponse,
  Customer,
  DashboardMetrics,
  DemoReset,
  HealthStatus,
  Incident,
  Transaction,
} from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000/api/v1";
const API_ORIGIN = API_BASE.replace(/\/api\/v1\/?$/, "");

function friendlyError(reason: unknown): Error {
  if (
    reason instanceof TypeError &&
    reason.message.toLowerCase().includes("fetch")
  ) {
    return new Error(
      "Backend API is not reachable. Start FastAPI on http://localhost:8000 and refresh this page."
    );
  }
  return reason instanceof Error
    ? reason
    : new Error("Request failed");
}

async function request<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });
  } catch (reason) {
    throw friendlyError(reason);
  }

  if (!response.ok) {
    const payload = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(payload.detail ?? "Request failed");
  }
  return response.json() as Promise<T>;
}

async function health(): Promise<HealthStatus> {
  try {
    const response = await fetch(`${API_ORIGIN}/health`, {
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    return response.json() as Promise<HealthStatus>;
  } catch (reason) {
    throw friendlyError(reason);
  }
}

export const api = {
  health,
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
  resetDemo: () =>
    request<DemoReset>("/demo/reset", {
      method: "POST",
    }),
  updateIncident: (id: string, status: string) =>
    request<Incident>(`/incidents/${id}/status`, {
      method: "POST",
      body: JSON.stringify({ status }),
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
