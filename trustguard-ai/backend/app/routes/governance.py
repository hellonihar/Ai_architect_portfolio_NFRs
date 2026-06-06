from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import AuditLog, SLABadge
from ..schemas import AuditLogOut, SLABadgeOut

router = APIRouter(prefix="/api/governance", tags=["governance"])


@router.get("/sla-badges")
async def get_sla_badges(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SLABadge))
    badges = result.scalars().all()
    return [SLABadgeOut.model_validate(b) for b in badges]


@router.get("/audit-logs")
async def get_audit_logs(
    hours: int = Query(168, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.timestamp >= cutoff)
        .order_by(AuditLog.timestamp.desc())
        .limit(200)
    )
    logs = result.scalars().all()
    return [AuditLogOut.model_validate(l) for l in logs]
