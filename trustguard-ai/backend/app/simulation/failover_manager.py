import random
from datetime import datetime, timedelta


class FailoverManager:
    def __init__(self):
        self.cooldown_until: datetime | None = None
        self.cooldown_seconds = 30
        self.consecutive_failures = 0

    def should_trigger_failover(self, recent_errors: list[bool]) -> bool:
        if self.cooldown_until and datetime.utcnow() < self.cooldown_until:
            return False

        if len(recent_errors) >= 3 and sum(recent_errors[-3:]) >= 2:
            self.consecutive_failures += 1
            if self.consecutive_failures >= 1:
                self.consecutive_failures = 0
                return True

        return False

    def simulate_outage(self) -> dict | None:
        if random.random() < 0.04:
            causes = ["latency threshold exceeded", "node failure", "network partition",
                      "resource exhaustion", "database connection timeout"]
            cause = random.choice(causes)
            return {
                "cause": cause,
                "duration_seconds": round(random.uniform(2.0, 15.0), 1),
                "timestamp": datetime.utcnow(),
            }
        return None

    def start_cooldown(self):
        self.cooldown_until = datetime.utcnow() + timedelta(seconds=self.cooldown_seconds)
