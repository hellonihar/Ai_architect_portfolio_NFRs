from datetime import datetime, timezone

from hr_bias_audit.models.resume import ResumeProfile
from hr_bias_audit.models.audit_result import (
    AuditResult, BiasScore, BiasDimension, GroupMetric,
)
from hr_bias_audit.analysis.fairness_metrics import FairnessMetrics


class BiasEngine:

    def __init__(self) -> None:
        self.fm = FairnessMetrics()

    FIELD_MAP = {
        BiasDimension.GENDER: "inferred_gender",
        BiasDimension.ETHNICITY: "inferred_ethnicity",
        BiasDimension.AGE: "inferred_age_group",
    }

    def _compute_dimension(
        self,
        dimension: BiasDimension,
        profiles: list[ResumeProfile],
    ) -> BiasScore:
        field = self.FIELD_MAP[dimension]
        label = dimension.value
        group_labels = [getattr(p, field) for p in profiles]
        scores = [p.screening_score for p in profiles]
        pass_flags = [p.passed_screen for p in profiles]

        group_metrics = self.fm.compute_group_metrics(
            group_labels, scores, pass_flags
        )

        privileged_pass = 0.0
        unprivileged_pass = 0.0
        for gm in group_metrics:
            if gm.group == "unknown":
                continue
            if gm.pass_rate > privileged_pass:
                unprivileged_pass = privileged_pass
                privileged_pass = gm.pass_rate
            elif gm.pass_rate > unprivileged_pass:
                unprivileged_pass = gm.pass_rate

        dir_value = self.fm.disparate_impact_ratio(
            privileged_pass, unprivileged_pass
        ) if privileged_pass > 0 else 1.0
        p_value = self.fm.chi_square_p_value(group_labels, pass_flags)

        is_biased = dir_value < 0.8 or p_value < 0.05
        if dir_value < 0.5:
            severity = "high"
            recommendation = (
                "Urgent: review screening criteria for "
                f"{label}-based disparities."
            )
        elif dir_value < 0.8:
            severity = "medium"
            recommendation = (
                f"Review {label} distribution and adjust "
                "weights to reduce disparity."
            )
        else:
            severity = "low"
            recommendation = (
                f"No significant {label} bias detected."
            )

        return BiasScore(
            dimension=dimension,
            disparate_impact_ratio=round(dir_value, 3),
            statistical_significance=round(p_value, 4),
            is_biased=is_biased,
            severity=severity,
            recommendation=recommendation,
            group_metrics=group_metrics,
        )

    def audit(self, profiles: list[ResumeProfile]) -> AuditResult:
        if not profiles:
            return AuditResult(
                total_applicants=0, total_passed=0, overall_pass_rate=0.0,
                bias_scores=[], audit_timestamp=datetime.now(tz=timezone.utc).isoformat(),
            )

        total = len(profiles)
        passed = sum(1 for p in profiles if p.passed_screen)
        overall_rate = passed / total

        scores = [
            self._compute_dimension(BiasDimension.GENDER, profiles),
            self._compute_dimension(BiasDimension.ETHNICITY, profiles),
            self._compute_dimension(BiasDimension.AGE, profiles),
        ]

        return AuditResult(
            total_applicants=total,
            total_passed=passed,
            overall_pass_rate=round(overall_rate, 3),
            bias_scores=scores,
            audit_timestamp=datetime.now(tz=timezone.utc).isoformat(),
        )
