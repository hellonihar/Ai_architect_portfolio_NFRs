import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, DECIMAL, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(String(50), nullable=False)
    gender = Column(String(20))
    age = Column(Integer)
    income = Column(DECIMAL(12, 2))
    region = Column(String(100))
    loan_amount = Column(DECIMAL(12, 2))
    loan_purpose = Column(String(100))
    approved = Column(Boolean)
    decision_date = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(DECIMAL(5, 2))
    actual_default = Column(Boolean)
    predicted_default = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)


class FairnessMetric(Base):
    __tablename__ = "fairness_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(10, 6), nullable=False)
    group_a = Column(String(100))
    group_b = Column(String(100))
    threshold = Column(DECIMAL(10, 6))
    passed = Column(Boolean)
    computed_at = Column(DateTime, default=datetime.utcnow)
    batch_id = Column(String(50))


class BiasAlert(Base):
    __tablename__ = "bias_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20))
    status = Column(String(20), default="Open")
    dimension = Column(String(50))
    affected_group = Column(String(100))
    metric_name = Column(String(100))
    metric_value = Column(DECIMAL(10, 6))
    threshold = Column(DECIMAL(10, 6))
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    actions = relationship("Action", back_populates="alert")


class DemographicParity(Base):
    __tablename__ = "demographic_parity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_name = Column(String(100), nullable=False)
    dimension = Column(String(50), nullable=False)
    approval_rate = Column(DECIMAL(5, 2))
    total_applications = Column(Integer)
    approved_count = Column(Integer)
    parity_threshold = Column(DECIMAL(5, 2))
    below_threshold = Column(Boolean)
    computed_at = Column(DateTime, default=datetime.utcnow)


class ComplianceStatus(Base):
    __tablename__ = "compliance_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    badge_name = Column(String(100), nullable=False)
    status = Column(String(20))
    description = Column(Text)
    last_audit_date = Column(DateTime)
    next_audit_date = Column(DateTime)
    evidence_url = Column(Text)
    requires_retraining = Column(Boolean, default=False)
    retraining_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Action(Base):
    __tablename__ = "actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="Pending")
    alert_id = Column(UUID(as_uuid=True), ForeignKey("bias_alerts.id"))
    assigned_to = Column(String(100))
    resolution_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    alert = relationship("BiasAlert", back_populates="actions")
