from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FairnessMetricResponse(BaseModel):
    id: UUID
    metric_name: str
    metric_value: float
    group_a: Optional[str] = None
    group_b: Optional[str] = None
    threshold: Optional[float] = None
    passed: Optional[bool] = None
    computed_at: datetime
    batch_id: Optional[str] = None

    class Config:
        from_attributes = True


class BiasAlertResponse(BaseModel):
    id: UUID
    alert_type: str
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    dimension: Optional[str] = None
    affected_group: Optional[str] = None
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DemographicParityResponse(BaseModel):
    id: UUID
    group_name: str
    dimension: str
    approval_rate: Optional[float] = None
    total_applications: Optional[int] = None
    approved_count: Optional[int] = None
    parity_threshold: Optional[float] = None
    below_threshold: Optional[bool] = None
    computed_at: datetime

    class Config:
        from_attributes = True


class ComplianceStatusResponse(BaseModel):
    id: UUID
    badge_name: str
    status: str
    description: Optional[str] = None
    last_audit_date: Optional[datetime] = None
    next_audit_date: Optional[datetime] = None
    evidence_url: Optional[str] = None
    requires_retraining: Optional[bool] = None
    retraining_reason: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionResponse(BaseModel):
    id: UUID
    action_type: str
    title: str
    description: Optional[str] = None
    status: str
    alert_id: Optional[UUID] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ActionCreate(BaseModel):
    action_type: str
    title: str
    description: Optional[str] = None
    alert_id: Optional[UUID] = None
    assigned_to: Optional[str] = None


class DashboardSummary(BaseModel):
    fairness_index: float
    disparate_impact: float
    equalized_odds: float
    total_alerts: int
    open_alerts: int
    critical_alerts: int
    compliance_passed: int
    compliance_failed: int
    groups_monitored: int
