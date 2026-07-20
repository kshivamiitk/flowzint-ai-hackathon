export type Customer = {
  id: string;
  name: string;
  email: string;
  language: string;
  plan: string;
};

export type Transaction = {
  id: string;
  customer_id: string;
  amount: number;
  payment_method: string;
  status: string;
  order_reference: string;
  app_version: string;
  error_code: string | null;
  refunded_at: string | null;
  created_at: string;
};

export type Action = {
  id: string;
  action_type: string;
  status: string;
  amount: number;
  reason: string;
  policy_reference: string;
  transaction_id: string | null;
  external_reference: string | null;
  reviewer_comment: string | null;
  created_at: string;
  updated_at: string;
};

export type Incident = {
  id: string;
  title: string;
  description: string;
  probable_root_cause: string;
  confidence: number;
  affected_customer_count: number;
  evidence: string[];
  status: string;
  created_at: string;
  updated_at: string;
};

export type ChatResponse = {
  conversation_id: string;
  message: string;
  intent: string;
  severity: string;
  language: string;
  confidence: number;
  decision_mode: string;
  risk_level: string;
  resolution_trace: Array<{
    id: string;
    label: string;
    status: string;
    detail: string;
  }>;
  policy_references: Array<{
    title: string;
    section: string;
  }>;
  action: Action | null;
  incident: Incident | null;
};

export type DashboardMetrics = {
  customers: number;
  conversations: number;
  open_incidents: number;
  pending_approvals: number;
  completed_actions: number;
  automation_rate: number;
};

export type HealthStatus = {
  status: string;
  service: string;
  ai_provider: string;
  database: string;
  chatbot: string;
  demo_mode: string;
};

export type DemoReset = {
  status: string;
  message: string;
  customers: number;
  scenarios: number;
};

export type AuditEvent = {
  id: string;
  event_type: string;
  actor: string;
  details: Record<string, unknown>;
  action_id: string | null;
  conversation_id: string | null;
  created_at: string;
};
