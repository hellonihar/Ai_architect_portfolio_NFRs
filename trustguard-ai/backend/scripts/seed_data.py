"""Seeds historical data for TrustGuard AI demo."""

import asyncio
import random
from datetime import datetime, timedelta

import numpy as np

from app.database import async_session, init_db
from app.models import AuditLog, FailoverEvent, PipelineHealth, ReliabilityMetric


async def seed():
    await init_db()
    async with async_session() as session:
        for p in [
            {"name": "Primary-1", "tier": "primary", "region": "us-east"},
            {"name": "Primary-2", "tier": "primary", "region": "us-west"},
            {"name": "Secondary-1", "tier": "secondary", "region": "eu-west"},
            {"name": "Secondary-2", "tier": "secondary", "region": "eu-central"},
            {"name": "Backup-1", "tier": "backup", "region": "ap-southeast"},
            {"name": "Backup-2", "tier": "backup", "region": "ap-northeast"},
        ]:
            session.add(PipelineHealth(
                id=p["name"], name=p["name"], tier=p["tier"],
                status="healthy", region=p["region"], uptime_percent=100.0,
                active_requests=random.randint(50, 500),
            ))

        now = datetime.utcnow()
        for i in range(7 * 24 * 12):
            t = now - timedelta(days=7) + timedelta(minutes=5 * i)
            base_f1 = 0.97 + 0.02 * np.sin(i / 48) + random.gauss(0, 0.005)
            base_precision = min(1.0, base_f1 + 0.01)
            base_recall = min(1.0, base_f1 - 0.005)
            base_latency = 12 + 5 * np.sin(i / 96) + random.gauss(0, 2)

            session.add(ReliabilityMetric(
                timestamp=t,
                uptime_percent=round(99.99 - abs(random.gauss(0, 0.003)), 4),
                avg_latency_ms=round(max(1, base_latency), 2),
                p50_latency_ms=round(max(1, base_latency * 0.7), 2),
                p95_latency_ms=round(max(1, base_latency * 1.8), 2),
                p99_latency_ms=round(max(1, base_latency * 3.0), 2),
                precision=round(max(0, min(1, base_precision)), 4),
                recall=round(max(0, min(1, base_recall)), 4),
                f1_score=round(max(0, min(1, base_f1)), 4),
                false_positives=random.randint(1, 5),
                false_negatives=random.randint(2, 8),
                total_transactions=random.randint(150, 250),
            ))

        for i in range(8):
            t = now - timedelta(days=random.randint(0, 6), hours=random.randint(0, 23))
            session.add(FailoverEvent(
                timestamp=t,
                from_pipeline=["Primary Tier", "Primary-1"][random.randint(0, 1)],
                to_pipeline=["Secondary Tier", "Backup Tier"][random.randint(0, 1)],
                cause=random.choice([
                    "latency threshold exceeded", "node failure",
                    "network partition", "resource exhaustion",
                ]),
                duration_seconds=round(random.uniform(1.5, 12.0), 1),
                recovered=True,
            ))

        audit_actions = [
            ("FAILOVER", "system", "Primary -> Secondary", "Automatic failover triggered due to latency spike"),
            ("MODEL_RETRAIN", "system", "all", "Model retrained after drift detection in transaction_amount"),
            ("SLA_CHECK", "auditor", None, "Monthly SLA compliance audit: 99.99% uptime achieved"),
            ("CONFIG_UPDATE", "admin", "Primary-1", "Latency threshold updated from 50ms to 75ms"),
            ("DRIFT_DETECTED", "system", "all", "Drift detected in location_velocity (magnitude: 0.12)"),
            ("SCALE_UP", "system", "Secondary-1", "Auto-scaling triggered: +2 instances"),
            ("AUDIT_EXPORT", "compliance", None, "Compliance report exported for regulatory review"),
        ]
        for i, (action, actor, pipeline, details) in enumerate(audit_actions):
            session.add(AuditLog(
                timestamp=now - timedelta(days=random.randint(0, 6), hours=random.randint(0, 23)),
                action=action, actor=actor, pipeline=pipeline, details=details,
            ))

        await session.commit()
        print("Seed data inserted successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
