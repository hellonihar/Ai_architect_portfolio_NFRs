export interface FairnessMetric {
  id: string;
  metric_name: string;
  metric_value: number;
  group_a: string | null;
  group_b: string | null;
  threshold: number | null;
  passed: boolean | null;
  computed_at: string;
  batch_id: string | null;
}

export interface BiasAlert {
  id: string;
  alert_type: string;
  title: string;
  description: string | null;
  severity: "Review" | "Investigate" | "Escalate";
  status: string;
  dimension: string | null;
  affected_group: string | null;
  metric_name: string | null;
  metric_value: number | null;
  threshold: number | null;
  created_at: string;
  resolved_at: string | null;
}

export interface DemographicParity {
  id: string;
  group_name: string;
  dimension: string;
  approval_rate: number | null;
  total_applications: number | null;
  approved_count: number | null;
  parity_threshold: number | null;
  below_threshold: boolean | null;
  computed_at: string;
}

export interface ComplianceStatusItem {
  id: string;
  badge_name: string;
  status: "Passed" | "Failed" | "Pending" | "In Progress";
  description: string | null;
  last_audit_date: string | null;
  next_audit_date: string | null;
  evidence_url: string | null;
  requires_retraining: boolean | null;
  retraining_reason: string | null;
  updated_at: string;
}

export interface ActionItem {
  id: string;
  action_type: string;
  title: string;
  description: string | null;
  status: string;
  alert_id: string | null;
  assigned_to: string | null;
  resolution_notes: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface DashboardSummary {
  fairness_index: number;
  disparate_impact: number;
  equalized_odds: number;
  total_alerts: number;
  open_alerts: number;
  critical_alerts: number;
  compliance_passed: number;
  compliance_failed: number;
  groups_monitored: number;
}

const BASE = "/api";

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  fairness: {
    metrics: () => fetchJSON<FairnessMetric[]>("/fairness/metrics"),
    demographics: (dimension?: string) =>
      fetchJSON<DemographicParity[]>(
        `/fairness/demographics${dimension ? `?dimension=${dimension}` : ""}`
      ),
    summary: () => fetchJSON<DashboardSummary>("/fairness/summary"),
  },
  alerts: {
    list: (params?: { severity?: string; status?: string }) => {
      const q = new URLSearchParams();
      if (params?.severity) q.set("severity", params.severity);
      if (params?.status) q.set("status", params.status);
      const qs = q.toString();
      return fetchJSON<BiasAlert[]>(`/alerts${qs ? `?${qs}` : ""}`);
    },
    stats: () =>
      fetchJSON<{
        total: number;
        review: number;
        investigate: number;
        escalate: number;
      }>("/alerts/stats"),
    resolve: (id: string) =>
      fetchJSON<BiasAlert>(`/alerts/${id}/resolve`, { method: "PATCH" }),
  },
  compliance: {
    list: () => fetchJSON<ComplianceStatusItem[]>("/compliance/status"),
  },
  actions: {
    list: (status?: string) =>
      fetchJSON<ActionItem[]>(
        `/actions${status ? `?status=${status}` : ""}`
      ),
    create: (data: {
      action_type: string;
      title: string;
      description?: string;
      alert_id?: string;
      assigned_to?: string;
    }) =>
      fetchJSON<ActionItem>("/actions", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    complete: (id: string) =>
      fetchJSON<ActionItem>(`/actions/${id}/complete`, { method: "PATCH" }),
  },
};
