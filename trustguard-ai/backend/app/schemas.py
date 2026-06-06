from datetime import datetime

from pydantic import BaseModel, Field


class PipelineHealthOut(BaseModel):
    id: str
    name: str
    tier: str
    status: str
    region: str
    uptime_percent: float
    active_requests: int
    last_failover: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReliabilityMetricOut(BaseModel):
    id: str
    timestamp: datetime
    uptime_percent: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    precision: float
    recall: float
    f1_score: float
    false_positives: int
    false_negatives: int
    total_transactions: int

    model_config = {"from_attributes": True}


class ReliabilitySummary(BaseModel):
    current_uptime: float
    avg_latency_ms: float
    avg_f1_score: float
    total_transactions: int
    total_false_positives: int
    total_false_negatives: int
    precision: float
    recall: float


class FailoverEventOut(BaseModel):
    id: str
    timestamp: datetime
    from_pipeline: str
    to_pipeline: str
    cause: str
    duration_seconds: float
    recovered: bool

    model_config = {"from_attributes": True}


class DriftEventOut(BaseModel):
    id: str
    timestamp: datetime
    feature: str
    magnitude: float
    severity: str
    retraining_triggered: bool
    resolved: bool

    model_config = {"from_attributes": True}


class SLABadgeOut(BaseModel):
    id: str
    name: str
    description: str
    status: str
    current_value: float
    threshold: float
    unit: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: str
    timestamp: datetime
    action: str
    actor: str
    pipeline: str | None = None
    details: str

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: str
    timestamp: datetime
    type: str = Field(..., description="drift | anomaly | failover")
    severity: str = Field(..., description="critical | warning | info")
    title: str
    description: str
    pipeline: str | None = None
    resolved: bool = False
