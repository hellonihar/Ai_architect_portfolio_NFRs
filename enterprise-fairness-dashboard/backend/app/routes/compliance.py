from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ComplianceStatus
from app.schemas import ComplianceStatusResponse

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


@router.get("/status", response_model=list[ComplianceStatusResponse])
async def get_compliance_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ComplianceStatus).order_by(ComplianceStatus.updated_at.desc())
    )
    return result.scalars().all()
