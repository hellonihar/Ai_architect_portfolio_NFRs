import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _uuid():
    return str(uuid.uuid4())


class PipelineHealth(Base):
    __tablename__ = "pipeline_health"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    tier: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default="healthy")
    region: Mapped[str] = mapped_column(String(32))
    uptime_percent: Mapped[float] = mapped_column(Float, default=100.0)
    active_requests: Mapped[int] = mapped_column(Integer, default=0)
    last_failover: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReliabilityMetric(Base):
    __tablename__ = "reliability_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    uptime_percent: Mapped[float] = mapped_column(Float)
    avg_latency_ms: Mapped[float] = mapped_column(Float)
    p50_latency_ms: Mapped[float] = mapped_column(Float)
    p95_latency_ms: Mapped[float] = mapped_column(Float)
    p99_latency_ms: Mapped[float] = mapped_column(Float)
    precision: Mapped[float] = mapped_column(Float)
    recall: Mapped[float] = mapped_column(Float)
    f1_score: Mapped[float] = mapped_column(Float)
    false_positives: Mapped[int] = mapped_column(Integer)
    false_negatives: Mapped[int] = mapped_column(Integer)
    total_transactions: Mapped[int] = mapped_column(Integer)


class FailoverEvent(Base):
    __tablename__ = "failover_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    from_pipeline: Mapped[str] = mapped_column(String(64))
    to_pipeline: Mapped[str] = mapped_column(String(64))
    cause: Mapped[str] = mapped_column(String(128))
    duration_seconds: Mapped[float] = mapped_column(Float)
    recovered: Mapped[bool] = mapped_column(default=True)


class DriftEvent(Base):
    __tablename__ = "drift_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    feature: Mapped[str] = mapped_column(String(64))
    magnitude: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(16))
    retraining_triggered: Mapped[bool] = mapped_column(default=False)
    resolved: Mapped[bool] = mapped_column(default=False)


class SLABadge(Base):
    __tablename__ = "sla_badges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="met")
    current_value: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(16), default="%")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    action: Mapped[str] = mapped_column(String(64))
    actor: Mapped[str] = mapped_column(String(64))
    pipeline: Mapped[str] = mapped_column(String(64), nullable=True)
    details: Mapped[str] = mapped_column(Text)
