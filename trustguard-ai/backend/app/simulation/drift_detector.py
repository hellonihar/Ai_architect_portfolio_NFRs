import random
from datetime import datetime

import numpy as np


class DriftDetector:
    def __init__(self, baseline_mean: float = 0.97, baseline_std: float = 0.02):
        self.baseline_mean = baseline_mean
        self.baseline_std = baseline_std
        self.recent_scores: list[float] = []
        self.window_size = 20

    def add_observation(self, f1_score: float):
        self.recent_scores.append(f1_score)
        if len(self.recent_scores) > self.window_size:
            self.recent_scores.pop(0)

    def check_drift(self) -> dict | None:
        if len(self.recent_scores) < 10:
            return None

        recent_mean = float(np.mean(self.recent_scores))
        magnitude = abs(self.baseline_mean - recent_mean)

        if magnitude > 3 * self.baseline_std:
            severity = "critical" if magnitude > 5 * self.baseline_std else "warning"
            return {
                "detected": True,
                "magnitude": round(magnitude, 4),
                "severity": severity,
                "recent_mean": round(recent_mean, 4),
                "baseline_mean": self.baseline_mean,
            }
        return None

    def simulate_drift_event(self) -> dict | None:
        if random.random() < 0.08:
            features = ["transaction_amount", "location_velocity", "device_fingerprint",
                        "ip_geolocation", "merchant_category", "time_since_last_txn"]
            feature = random.choice(features)
            magnitude = round(random.uniform(0.03, 0.15), 4)
            severity = "critical" if magnitude > 0.1 else "warning"
            return {
                "feature": feature,
                "magnitude": magnitude,
                "severity": severity,
                "timestamp": datetime.utcnow(),
            }
        return None
