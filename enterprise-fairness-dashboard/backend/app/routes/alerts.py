from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import BiasAlert
from app.schemas import BiasAlertResponse

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=list[BiasAlertResponse])
async def get_alerts(
    severity: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(BiasAlert).order_by(BiasAlert.created_at.desc())
    if severity:
        query = query.where(BiasAlert.severity == severity)
    if status:
        query = query.where(BiasAlert.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats")
async def get_alert_stats(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count(BiasAlert.id)))
    by_severity = await db.execute(
        select(BiasAlert.severity, func.count(BiasAlert.id).label("count"))
        .group_by(BiasAlert.severity)
    )
    severity_counts = {row.severity: row.count for row in by_severity}
    return {
        "total": total or 0,
        "review": severity_counts.get("Review", 0),
        "investigate": severity_counts.get("Investigate", 0),
        "escalate": severity_counts.get("Escalate", 0),
    }


@router.patch("/{alert_id}/resolve", response_model=BiasAlertResponse)
async def resolve_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BiasAlert).where(BiasAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "Resolved"
    alert.resolved_at = func.now()
    await db.commit()
    await db.refresh(alert)
    return alert
