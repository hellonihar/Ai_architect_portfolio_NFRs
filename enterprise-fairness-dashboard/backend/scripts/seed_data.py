"""Seed the database with sample loan application data and fairness metrics."""

import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.models import (
    Base,
    LoanApplication,
    FairnessMetric,
    BiasAlert,
    DemographicParity,
    ComplianceStatus,
    Action,
)

engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

REGIONS = ["North", "South", "East", "West", "Central"]
GENDERS = ["Male", "Female", "Non-Binary"]
LOAN_PURPOSES = ["Home", "Auto", "Education", "Business", "Personal"]
INCOME_BRACKETS = ["Low", "Medium-Low", "Medium", "Medium-High", "High"]


def _generate_applications(n: int = 200) -> list[LoanApplication]:
    apps = []
    for i in range(n):
        gender = random.choices(
            GENDERS, weights=[45, 45, 10]
        )[0]
        region = random.choice(REGIONS)
        age = random.randint(22, 70)
        income = round(random.uniform(20_000, 200_000), 2)

        loan_amount = round(random.uniform(5_000, 100_000), 2)
        risk_score = round(random.uniform(0.1, 0.9), 2)

        approved = risk_score < (0.7 if gender == "Male" else 0.6)

        apps.append(LoanApplication(
            applicant_id=f"APP-{2024000 + i}",
            gender=gender,
            age=age,
            income=income,
            region=region,
            loan_amount=loan_amount,
            loan_purpose=random.choice(LOAN_PURPOSES),
            approved=approved,
            risk_score=risk_score,
            actual_default=random.random() < 0.15,
            predicted_default=risk_score > 0.65,
        ))
    return apps


def _generate_fairness_metrics() -> list[FairnessMetric]:
    now = datetime.utcnow()
    return [
        FairnessMetric(metric_name="fairness_index", metric_value=0.87, group_a="All", group_b="All", threshold=0.80, passed=True, computed_at=now, batch_id="batch-001"),
        FairnessMetric(metric_name="disparate_impact", metric_value=0.82, group_a="Female", group_b="Male", threshold=0.80, passed=True, computed_at=now, batch_id="batch-001"),
        FairnessMetric(metric_name="equalized_odds", metric_value=0.79, group_a="Female", group_b="Male", threshold=0.75, passed=True, computed_at=now, batch_id="batch-001"),
        FairnessMetric(metric_name="disparate_impact", metric_value=0.72, group_a="Non-Binary", group_b="Male", threshold=0.80, passed=False, computed_at=now, batch_id="batch-001"),
        FairnessMetric(metric_name="equalized_odds", metric_value=0.68, group_a="Low Income", group_b="High Income", threshold=0.75, passed=False, computed_at=now, batch_id="batch-001"),
    ]


def _generate_alerts() -> list[BiasAlert]:
    now = datetime.utcnow()
    return [
        BiasAlert(
            alert_type="gender_bias", title="Gender bias detected in loan approvals",
            description="Female applicants have a 14% lower approval rate than male applicants with similar credit profiles.",
            severity="Escalate", dimension="Gender", affected_group="Female",
            metric_name="disparate_impact", metric_value=0.72, threshold=0.80,
            created_at=now - timedelta(hours=2),
        ),
        BiasAlert(
            alert_type="income_bias", title="Income disparity in approval rates",
            description="Low-income applicants face 22% lower approval rates compared to high-income applicants.",
            severity="Investigate", dimension="Income", affected_group="Low Income",
            metric_name="equalized_odds", metric_value=0.68, threshold=0.75,
            created_at=now - timedelta(hours=5),
        ),
        BiasAlert(
            alert_type="regional_bias", title="Regional approval variance detected",
            description="Applicants from the South region show 8% lower approval rates than the average.",
            severity="Review", dimension="Region", affected_group="South",
            metric_name="fairness_index", metric_value=0.85, threshold=0.80,
            created_at=now - timedelta(hours=12),
        ),
        BiasAlert(
            alert_type="age_bias", title="Age-based disparity flagged",
            description="Applicants over 55 have a 9% lower approval rate. Review underwriting criteria.",
            severity="Investigate", dimension="Age", affected_group="55+",
            metric_name="disparate_impact", metric_value=0.76, threshold=0.80,
            created_at=now - timedelta(days=1),
        ),
    ]


def _generate_demographics() -> list[DemographicParity]:
    now = datetime.utcnow()
    groups = [
        ("Male", "Gender", 76.5, 200, 153),
        ("Female", "Gender", 62.3, 180, 112),
        ("Non-Binary", "Gender", 58.0, 40, 23),
        ("North", "Region", 72.0, 100, 72),
        ("South", "Region", 64.5, 110, 71),
        ("East", "Region", 70.2, 90, 63),
        ("West", "Region", 74.8, 85, 64),
        ("Central", "Region", 69.0, 95, 66),
        ("Low", "Income", 55.2, 80, 44),
        ("Medium-Low", "Income", 65.8, 95, 63),
        ("Medium", "Income", 73.4, 110, 81),
        ("Medium-High", "Income", 78.1, 85, 66),
        ("High", "Income", 82.5, 70, 58),
    ]
    threshold = 75.0
    return [
        DemographicParity(
            group_name=g[0], dimension=g[1], approval_rate=g[2],
            total_applications=g[3], approved_count=g[4],
            parity_threshold=threshold, below_threshold=g[2] < threshold,
            computed_at=now,
        )
        for g in groups
    ]


def _generate_compliance() -> list[ComplianceStatus]:
    now = datetime.utcnow()
    return [
        ComplianceStatus(badge_name="Fairness Audit Passed", status="Passed",
                         description="Latest fairness audit completed with a score of 0.87. All primary metrics within threshold.",
                         last_audit_date=now - timedelta(days=7), next_audit_date=now + timedelta(days=23),
                         evidence_url="/audits/latest", requires_retraining=False),
        ComplianceStatus(badge_name="GDPR Compliant", status="Passed",
                         description="GDPR Article 22 compliance verified. Automated decision-making includes human review pathways.",
                         last_audit_date=now - timedelta(days=14), next_audit_date=now + timedelta(days=50),
                         evidence_url="/audits/gdpr", requires_retraining=False),
        ComplianceStatus(badge_name="EEOC Fair Lending", status="In Progress",
                         description="Equal Employment Opportunity Commission fair lending review in progress.",
                         last_audit_date=now - timedelta(days=30), next_audit_date=now + timedelta(days=90),
                         evidence_url="/audits/eeoc", requires_retraining=True,
                         retraining_reason="Disparate impact on Non-Binary group below threshold"),
        ComplianceStatus(badge_name="Model Retraining Required", status="Failed",
                         description="Approval model shows drift on income and gender dimensions. Retraining triggered.",
                         last_audit_date=now - timedelta(days=1), next_audit_date=now + timedelta(days=14),
                         evidence_url="/audits/retraining", requires_retraining=True,
                         retraining_reason="Distribution shift detected in income brackets"),
    ]


def _generate_actions() -> list[Action]:
    now = datetime.utcnow()
    return [
        Action(action_type="investigate", title="Investigate gender approval gap",
               description="Review underwriting criteria for gender bias. Analyze feature importance in model decisions.",
               status="In Progress", assigned_to="ML Team", created_at=now - timedelta(hours=2)),
        Action(action_type="escalate", title="Escalate income disparity to compliance",
               description="Income-based approval gap exceeds threshold. Escalating to compliance officer for review.",
               status="Pending", assigned_to="Compliance Officer", created_at=now - timedelta(hours=5)),
        Action(action_type="update_data", title="Update training data with balanced sampling",
               description="Re-sample training data to ensure balanced representation across income brackets.",
               status="Pending", assigned_to="Data Engineering", created_at=now - timedelta(hours=12)),
        Action(action_type="generate_report", title="Generate monthly fairness compliance report",
               description="Compile fairness metrics, alerts, and remediation actions for regulatory submission.",
               status="Pending", assigned_to="Compliance Team", created_at=now - timedelta(days=1)),
    ]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        session.add_all(_generate_applications(250))
        session.add_all(_generate_fairness_metrics())
        session.add_all(_generate_alerts())
        session.add_all(_generate_demographics())
        session.add_all(_generate_compliance())
        session.add_all(_generate_actions())
        await session.commit()
        print("Database seeded successfully with sample data.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
