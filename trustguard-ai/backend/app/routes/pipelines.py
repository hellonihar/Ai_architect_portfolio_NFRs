from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import FailoverEvent, PipelineHealth
from ..schemas import FailoverEventOut, PipelineHealthOut

router = APIRouter(prefix="/api/pipelines", tags=["pipelines"])


@router.get("/health")
async def get_pipeline_health(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PipelineHealth))
    pipelines = result.scalars().all()
    return [PipelineHealthOut.model_validate(p) for p in pipelines]


@router.get("/topology")
async def get_topology(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PipelineHealth))
    pipelines = result.scalars().all()
    tiers = {"primary": [], "secondary": [], "backup": []}
    for p in pipelines:
        if p.tier in tiers:
            tiers[p.tier].append(PipelineHealthOut.model_validate(p))
    active_tier = None
    for tier in ["primary", "secondary", "backup"]:
        if any(p.status == "healthy" for p in tiers[tier]):
            active_tier = tier
            break
    return {"tiers": tiers, "active_tier": active_tier}


@router.get("/failovers")
async def get_failovers(hours: int = 72, db: AsyncSession = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(FailoverEvent)
        .where(FailoverEvent.timestamp >= cutoff)
        .order_by(FailoverEvent.timestamp.desc())
    )
    events = result.scalars().all()
    return [FailoverEventOut.model_validate(e) for e in events]
