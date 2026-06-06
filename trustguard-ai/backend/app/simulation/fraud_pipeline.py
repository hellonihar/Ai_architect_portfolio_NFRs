import asyncio
import math
import random
from datetime import datetime

import numpy as np


class FraudPipelineSimulator:
    PIPELINES = [
        {"name": "Primary-1", "tier": "primary", "region": "us-east", "base_latency": (8, 15)},
        {"name": "Primary-2", "tier": "primary", "region": "us-west", "base_latency": (10, 18)},
        {"name": "Secondary-1", "tier": "secondary", "region": "eu-west", "base_latency": (15, 25)},
        {"name": "Secondary-2", "tier": "secondary", "region": "eu-central", "base_latency": (16, 28)},
        {"name": "Backup-1", "tier": "backup", "region": "ap-southeast", "base_latency": (30, 50)},
        {"name": "Backup-2", "tier": "backup", "region": "ap-northeast", "base_latency": (32, 55)},
    ]

    def __init__(self):
        self.active_tier = "primary"
        self.pipeline_states = {p["name"]: {"healthy": True, "latency_spike": False} for p in self.PIPELINES}
        self.transaction_count = 0

    def get_active_pipelines(self):
        tier_map = {"primary": ["Primary-1", "Primary-2"],
                    "secondary": ["Secondary-1", "Secondary-2"],
                    "backup": ["Backup-1", "Backup-2"]}
        names = tier_map.get(self.active_tier, tier_map["primary"])
        return [p for p in self.PIPELINES if p["name"] in names]

    def simulate_transaction(self):
        self.transaction_count += 1
        pipelines = self.get_active_pipelines()
        chosen = random.choice(pipelines)
        state = self.pipeline_states[chosen["name"]]
        base_low, base_high = chosen["base_latency"]

        if state["latency_spike"]:
            latency = random.uniform(base_high * 2, base_high * 5)
        elif not state["healthy"]:
            latency = float("inf")
        else:
            latency = random.uniform(base_low, base_high)

        is_fraud = random.random() < 0.08
        decision_correct = random.random() < 0.97 if not state.get("degraded") else random.random() < 0.85

        return {
            "pipeline": chosen["name"],
            "latency_ms": latency,
            "is_fraud": is_fraud,
            "decision_correct": decision_correct,
            "timestamp": datetime.utcnow(),
        }

    def trigger_failover(self):
        tiers = ["primary", "secondary", "backup"]
        current_idx = tiers.index(self.active_tier)
        if current_idx < len(tiers) - 1:
            self.active_tier = tiers[current_idx + 1]
            return self.active_tier
        return None

    def degrade_pipeline(self, name: str):
        if name in self.pipeline_states:
            self.pipeline_states[name]["healthy"] = False

    def recover_pipeline(self, name: str):
        if name in self.pipeline_states:
            self.pipeline_states[name] = {"healthy": True, "latency_spike": False, "degraded": False}

    def spike_latency(self, name: str):
        if name in self.pipeline_states:
            self.pipeline_states[name]["latency_spike"] = True

    def degrade_accuracy(self, name: str):
        if name in self.pipeline_states:
            self.pipeline_states[name]["degraded"] = True

    def generate_metrics_snapshot(self):
        pipelines = self.get_active_pipelines()
        latencies = []
        correct = 0
        total = 200

        for _ in range(total):
            t = self.simulate_transaction()
            if math.isfinite(t["latency_ms"]):
                latencies.append(t["latency_ms"])
            if t["decision_correct"]:
                correct += 1

        fp = int(total * 0.015 * random.uniform(0.8, 1.2))
        fn = int(total * 0.025 * random.uniform(0.8, 1.2))
        precision = (total - fp) / total if total > 0 else 1.0
        recall = (total - fn) / total if total > 0 else 1.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        latencies = [l for l in latencies if math.isfinite(l)]
        if not latencies:
            latencies = [10]

        return {
            "uptime_percent": 100.0 * sum(1 for s in self.pipeline_states.values() if s["healthy"]) / len(self.pipeline_states),
            "avg_latency_ms": float(np.mean(latencies)),
            "p50_latency_ms": float(np.percentile(latencies, 50)),
            "p95_latency_ms": float(np.percentile(latencies, 95)),
            "p99_latency_ms": float(np.percentile(latencies, 99)),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "false_positives": fp,
            "false_negatives": fn,
            "total_transactions": total,
        }
