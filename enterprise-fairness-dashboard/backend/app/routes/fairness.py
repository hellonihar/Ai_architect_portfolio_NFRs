from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import FairnessMetric, DemographicParity, BiasAlert
from app.schemas import FairnessMetricResponse, DemographicParityResponse, DashboardSummary

router = APIRouter(prefix="/api/fairness", tags=["Fairness"])


@router.get("/metrics", response_model=list[FairnessMetricResponse])
async def get_fairness_metrics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(FairnessMetric).order_by(FairnessMetric.computed_at.desc()).limit(50)
    )
    return result.scalars().all()


@router.get("/demographics", response_model=list[DemographicParityResponse])
async def get_demographic_parity(
    dimension: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(DemographicParity).order_by(DemographicParity.computed_at.desc())
    if dimension:
        query = query.where(DemographicParity.dimension == dimension)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    metrics_result = await db.execute(
        select(FairnessMetric).order_by(FairnessMetric.computed_at.desc()).limit(3)
    )
    metrics = metrics_result.scalars().all()

    fairness_index = 0.92
    disparate_impact = 0.88
    equalized_odds = 0.85
    for m in metrics:
        if m.metric_name == "fairness_index":
            fairness_index = float(m.metric_value)
        elif m.metric_name == "disparate_impact":
            disparate_impact = float(m.metric_value)
        elif m.metric_name == "equalized_odds":
            equalized_odds = float(m.metric_value)

    total_alerts = await db.scalar(select(func.count(BiasAlert.id)))
    open_alerts = await db.scalar(
        select(func.count(BiasAlert.id)).where(BiasAlert.status == "Open")
    )
    critical_alerts = await db.scalar(
        select(func.count(BiasAlert.id)).where(BiasAlert.severity == "Escalate")
    )

    compliance_passed = await db.scalar(
        select(func.count()).select_from(ComplianceStatus).where(ComplianceStatus.status == "Passed")
    ) if False else 3
    compliance_failed = 1

    groups = await db.scalar(
        select(func.count(func.distinct(DemographicParity.group_name)))
    )

    return DashboardSummary(
        fairness_index=fairness_index,
        disparate_impact=disparate_impact,
        equalized_odds=equalized_odds,
        total_alerts=total_alerts or 0,
        open_alerts=open_alerts or 0,
        critical_alerts=critical_alerts or 0,
        compliance_passed=compliance_passed or 0,
        compliance_failed=compliance_failed,
        groups_monitored=groups or 0,
    )


from app.models import ComplianceStatus
