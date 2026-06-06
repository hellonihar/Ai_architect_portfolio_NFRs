import numpy as np
import pandas as pd
from scipy import stats
from hr_bias_audit.models.audit_result import GroupMetric


class FairnessMetrics:

    @staticmethod
    def disparate_impact_ratio(
        privileged_pass_rate: float, unprivileged_pass_rate: float
    ) -> float:
        if privileged_pass_rate == 0:
            return 0.0
        return unprivileged_pass_rate / privileged_pass_rate

    @staticmethod
    def chi_square_p_value(
        group_labels: list[str], pass_flags: list[bool]
    ) -> float:
        df = pd.DataFrame({"group": group_labels, "passed": pass_flags})
        contingency = pd.crosstab(df["group"], df["passed"])
        if contingency.shape != (2, 2):
            return 1.0
        _, p, _, _ = stats.chi2_contingency(contingency, correction=False)
        return p

    @staticmethod
    def compute_group_metrics(
        groups: list[str], scores: list[float], pass_flags: list[bool]
    ) -> list[GroupMetric]:
        df = pd.DataFrame({
            "group": groups, "score": scores, "passed": pass_flags,
        })
        metrics = []
        for name, grp in df.groupby("group"):
            metrics.append(
                GroupMetric(
                    group=name,
                    applicant_count=len(grp),
                    pass_rate=grp["passed"].mean(),
                    avg_score=float(grp["score"].mean()),
                    std_score=float(grp["score"].std()) if len(grp) > 1 else 0.0,
                )
            )
        return metrics
