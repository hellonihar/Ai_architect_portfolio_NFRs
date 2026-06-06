from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import DriftEvent, FailoverEvent
from ..schemas import AlertOut, DriftEventOut

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/drift")
async def get_drift_events(
    hours: int = Query(168, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(DriftEvent)
        .where(DriftEvent.timestamp >= cutoff)
        .order_by(DriftEvent.timestamp.desc())
    )
    events = result.scalars().all()
    return [DriftEventOut.model_validate(e) for e in events]


@router.get("/feed")
async def get_alert_feed(
    hours: int = Query(72, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    alerts: list[AlertOut] = []

    drift_result = await db.execute(
        select(DriftEvent).where(DriftEvent.timestamp >= cutoff)
        .order_by(DriftEvent.timestamp.desc()).limit(50)
    )
    for de in drift_result.scalars().all():
        alerts.append(AlertOut(
            id=f"drift-{de.id}",
            timestamp=de.timestamp,
            type="drift",
            severity=de.severity,
            title=f"Drift detected in {de.feature}",
            description=f"Feature drift magnitude: {de.magnitude}. Retraining {'triggered' if de.retraining_triggered else 'pending'}.",
            pipeline="all",
            resolved=de.resolved,
        ))

    failover_result = await db.execute(
        select(FailoverEvent).where(FailoverEvent.timestamp >= cutoff)
        .order_by(FailoverEvent.timestamp.desc()).limit(50)
    )
    for fe in failover_result.scalars().all():
        alerts.append(AlertOut(
            id=f"failover-{fe.id}",
            timestamp=fe.timestamp,
            type="failover",
            severity="critical",
            title=f"Failover: {fe.from_pipeline} → {fe.to_pipeline}",
            description=f"Cause: {fe.cause}. Downtime: {fe.duration_seconds}s.",
            pipeline=f"{fe.from_pipeline}",
            resolved=fe.recovered,
        ))

    alerts.sort(key=lambda a: a.timestamp, reverse=True)
    return alerts[:100]
