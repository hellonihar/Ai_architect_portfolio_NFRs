from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import ReliabilityMetric
from ..schemas import ReliabilityMetricOut, ReliabilitySummary

router = APIRouter(prefix="/api/reliability", tags=["reliability"])


@router.get("/metrics")
async def get_metrics(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(ReliabilityMetric)
        .where(ReliabilityMetric.timestamp >= cutoff)
        .order_by(ReliabilityMetric.timestamp.asc())
    )
    metrics = result.scalars().all()
    return [ReliabilityMetricOut.model_validate(m) for m in metrics]


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(ReliabilityMetric).where(ReliabilityMetric.timestamp >= cutoff)
        .order_by(ReliabilityMetric.timestamp.desc())
    )
    recent = result.scalars().all()

    if not recent:
        result = await db.execute(
            select(ReliabilityMetric).order_by(ReliabilityMetric.timestamp.desc()).limit(1)
        )
        recent = list(result.scalars().all())

    if not recent:
        return ReliabilitySummary(
            current_uptime=100.0, avg_latency_ms=0, avg_f1_score=0,
            total_transactions=0, total_false_positives=0, total_false_negatives=0,
            precision=0, recall=0,
        )

    latest = recent[0]
    avg_f1 = sum(m.f1_score for m in recent) / len(recent)
    avg_precision = sum(m.precision for m in recent) / len(recent)
    avg_recall = sum(m.recall for m in recent) / len(recent)

    return ReliabilitySummary(
        current_uptime=latest.uptime_percent,
        avg_latency_ms=round(latest.avg_latency_ms, 2),
        avg_f1_score=round(avg_f1, 4),
        total_transactions=sum(m.total_transactions for m in recent),
        total_false_positives=sum(m.false_positives for m in recent),
        total_false_negatives=sum(m.false_negatives for m in recent),
        precision=round(avg_precision, 4),
        recall=round(avg_recall, 4),
    )
