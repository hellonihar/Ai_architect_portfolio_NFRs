import asyncio
import random
from datetime import datetime

from ..database import async_session
from ..models import AuditLog, FailoverEvent, PipelineHealth, ReliabilityMetric, SLABadge, DriftEvent
from .drift_detector import DriftDetector
from .failover_manager import FailoverManager
from .fraud_pipeline import FraudPipelineSimulator


class MetricsEngine:
    def __init__(self):
        self.pipeline = FraudPipelineSimulator()
        self.drift_detector = DriftDetector()
        self.failover_manager = FailoverManager()
        self.running = False
        self._sla_breach_log: list[str] = []

    async def initialize(self):
        async with async_session() as session:
            existing = await session.get(PipelineHealth, "seed-check")
            if existing is None:
                for p in FraudPipelineSimulator.PIPELINES:
                    ph = PipelineHealth(
                        id=p["name"],
                        name=p["name"],
                        tier=p["tier"],
                        status="healthy",
                        region=p["region"],
                        uptime_percent=100.0,
                        active_requests=0,
                    )
                    session.add(ph)

                sla_defs = [
                    SLABadge(id="sla-uptime", name="Uptime SLA", description="Service uptime meets 99.9% target",
                             status="met", current_value=99.99, threshold=99.9, unit="%"),
                    SLABadge(id="sla-latency", name="Latency SLA", description="Fraud check latency below 50ms P99",
                             status="met", current_value=42.5, threshold=50.0, unit="ms"),
                    SLABadge(id="sla-accuracy", name="Accuracy SLA", description="F1 score above 0.95",
                             status="met", current_value=0.97, threshold=0.95, unit="score"),
                    SLABadge(id="sla-fraud-detection", name="Fraud Detection SLA", description="Fraud detection SLA met with 99.99% reliability",
                             status="met", current_value=99.99, threshold=99.99, unit="%"),
                ]
                for sla in sla_defs:
                    session.add(sla)

                audit = AuditLog(
                    id="audit-init",
                    action="SYSTEM_INIT",
                    actor="system",
                    pipeline=None,
                    details="TrustGuard AI platform initialized with 6 pipeline nodes across 3 tiers",
                )
                session.add(audit)
                await session.commit()

    async def tick(self):
        snapshot = self.pipeline.generate_metrics_snapshot()
        self.drift_detector.add_observation(snapshot["f1_score"])
        drift_result = self.drift_detector.check_drift()

        async with async_session() as session:
            metric = ReliabilityMetric(**snapshot)
            session.add(metric)

            if drift_result:
                de = DriftEvent(
                    feature="f1_score",
                    magnitude=drift_result["magnitude"],
                    severity=drift_result["severity"],
                    retraining_triggered=True,
                    resolved=False,
                )
                session.add(de)
                self.drift_detector.recent_scores = []
                session.add(AuditLog(
                    action="DRIFT_DETECTED",
                    actor="system",
                    pipeline="all",
                    details=f"F1 drift: {drift_result['magnitude']} ({drift_result['severity']}). Auto-retraining triggered.",
                ))

            drift_sim = self.drift_detector.simulate_drift_event()
            if drift_sim:
                de2 = DriftEvent(
                    feature=drift_sim["feature"],
                    magnitude=drift_sim["magnitude"],
                    severity=drift_sim["severity"],
                    retraining_triggered=True,
                    resolved=False,
                )
                session.add(de2)
                session.add(AuditLog(
                    action="FEATURE_DRIFT",
                    actor="system",
                    pipeline="all",
                    details=f"Drift in {drift_sim['feature']}: {drift_sim['magnitude']} ({drift_sim['severity']})",
                ))

            outage = self.failover_manager.simulate_outage()
            if outage:
                old_tier = self.pipeline.active_tier
                new_tier = self.pipeline.trigger_failover()
                if new_tier:
                    fe = FailoverEvent(
                        from_pipeline=f"{old_tier.title()} Tier",
                        to_pipeline=f"{new_tier.title()} Tier",
                        cause=outage["cause"],
                        duration_seconds=outage["duration_seconds"],
                        recovered=True,
                    )
                    session.add(fe)
                    self.failover_manager.start_cooldown()
                    session.add(AuditLog(
                        action="FAILOVER",
                        actor="system",
                        pipeline=f"{old_tier}->{new_tier}",
                        details=f"Automatic failover: {old_tier} → {new_tier}. Cause: {outage['cause']}",
                    ))

            pipeline_statuses = self.pipeline.pipeline_states
            for p in FraudPipelineSimulator.PIPELINES:
                state = pipeline_statuses[p["name"]]
                ph = await session.get(PipelineHealth, p["name"])
                if ph:
                    ph.status = "healthy" if state["healthy"] else "degraded"
                    ph.uptime_percent = round(min(100.0, ph.uptime_percent + random.uniform(-0.001, 0.002)), 4)
                    ph.active_requests = random.randint(50, 500)

            sla_records = await session.get(SLABadge, "sla-uptime")
            if sla_records:
                sla_records.current_value = round(snapshot["uptime_percent"], 4)
                sla_records.status = "met" if snapshot["uptime_percent"] >= sla_records.threshold else "breached"

            sla_lat = await session.get(SLABadge, "sla-latency")
            if sla_lat:
                sla_lat.current_value = round(snapshot["p99_latency_ms"], 2)
                sla_lat.status = "met" if snapshot["p99_latency_ms"] <= sla_lat.threshold else "breached"

            sla_acc = await session.get(SLABadge, "sla-accuracy")
            if sla_acc:
                sla_acc.current_value = round(snapshot["f1_score"], 4)
                sla_acc.status = "met" if snapshot["f1_score"] >= sla_acc.threshold else "breached"

            sla_fd = await session.get(SLABadge, "sla-fraud-detection")
            if sla_fd:
                sla_fd.current_value = round(99.99 - (snapshot["false_negatives"] * 0.001), 4)
                sla_fd.status = "met" if sla_fd.current_value >= sla_fd.threshold else "breached"

            await session.commit()

    async def run_loop(self):
        self.running = True
        await self.initialize()
        while self.running:
            await self.tick()
            await asyncio.sleep(5)

    def stop(self):
        self.running = False
