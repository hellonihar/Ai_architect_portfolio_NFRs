export interface ReliabilityMetric {
  id: string;
  timestamp: string;
  uptime_percent: number;
  avg_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
  precision: number;
  recall: number;
  f1_score: number;
  false_positives: number;
  false_negatives: number;
  total_transactions: number;
}

export interface ReliabilitySummary {
  current_uptime: number;
  avg_latency_ms: number;
  avg_f1_score: number;
  total_transactions: number;
  total_false_positives: number;
  total_false_negatives: number;
  precision: number;
  recall: number;
}

export interface PipelineHealth {
  id: string;
  name: string;
  tier: string;
  status: string;
  region: string;
  uptime_percent: number;
  active_requests: number;
  last_failover: string | null;
  created_at: string;
}

export interface Topology {
  tiers: { primary: PipelineHealth[]; secondary: PipelineHealth[]; backup: PipelineHealth[] };
  active_tier: string;
}

export interface FailoverEvent {
  id: string;
  timestamp: string;
  from_pipeline: string;
  to_pipeline: string;
  cause: string;
  duration_seconds: number;
  recovered: boolean;
}

export interface DriftEvent {
  id: string;
  timestamp: string;
  feature: string;
  magnitude: number;
  severity: string;
  retraining_triggered: boolean;
  resolved: boolean;
}

export interface SLABadge {
  id: string;
  name: string;
  description: string;
  status: string;
  current_value: number;
  threshold: number;
  unit: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  action: string;
  actor: string;
  pipeline: string | null;
  details: string;
}

export interface Alert {
  id: string;
  timestamp: string;
  type: string;
  severity: string;
  title: string;
  description: string;
  pipeline: string | null;
  resolved: boolean;
}

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

export const api = {
  reliability: {
    metrics: (hours = 24) => fetchJSON<ReliabilityMetric[]>(`/api/reliability/metrics?hours=${hours}`),
    summary: () => fetchJSON<ReliabilitySummary>("/api/reliability/summary"),
  },
  pipelines: {
    health: () => fetchJSON<PipelineHealth[]>("/api/pipelines/health"),
    topology: () => fetchJSON<Topology>("/api/pipelines/topology"),
    failovers: (hours = 72) => fetchJSON<FailoverEvent[]>(`/api/pipelines/failovers?hours=${hours}`),
  },
  governance: {
    slaBadges: () => fetchJSON<SLABadge[]>("/api/governance/sla-badges"),
    auditLogs: (hours = 168) => fetchJSON<AuditLog[]>(`/api/governance/audit-logs?hours=${hours}`),
  },
  alerts: {
    drift: (hours = 168) => fetchJSON<DriftEvent[]>(`/api/alerts/drift?hours=${hours}`),
    feed: (hours = 72) => fetchJSON<Alert[]>(`/api/alerts/feed?hours=${hours}`),
  },
};
