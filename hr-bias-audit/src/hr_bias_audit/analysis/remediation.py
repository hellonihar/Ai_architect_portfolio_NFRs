import copy
from typing import Optional

from hr_bias_audit.models.resume import ResumeProfile
from hr_bias_audit.models.audit_result import AuditResult
from hr_bias_audit.analysis.bias_engine import BiasEngine


def apply_blind_screening(
    profiles: list[ResumeProfile], threshold: float = 0.5
) -> list[ResumeProfile]:
    remediated: list[ResumeProfile] = []
    for p in profiles:
        r = copy.deepcopy(p)
        r.inferred_gender = "unknown"
        r.inferred_age_group = "unknown"
        r.inferred_ethnicity = "unknown"
        r.passed_screen = r.screening_score >= threshold
        remediated.append(r)
    return remediated


def apply_weight_recalibration(
    profiles: list[ResumeProfile],
    threshold: float = 0.5,
    boost_factors: Optional[dict[str, float]] = None,
) -> list[ResumeProfile]:
    if boost_factors is None:
        boost_factors = {
            "female": 0.10,
            "under_30": 0.08,
            "over_50": 0.05,
            "diverse_signal": 0.10,
        }
    remediated: list[ResumeProfile] = []
    for p in profiles:
        r = copy.deepcopy(p)
        boost = 0.0
        for attr, factor in boost_factors.items():
            vals = [getattr(r, f) for f in ["inferred_gender", "inferred_age_group", "inferred_ethnicity"]]
            if attr in vals:
                boost += factor
        r.screening_score = min(0.98, r.screening_score + boost)
        r.passed_screen = r.screening_score >= threshold
        remediated.append(r)
    return remediated


def apply_human_review(
    profiles: list[ResumeProfile],
    threshold: float = 0.5,
    review_margin: float = 0.10,
) -> list[ResumeProfile]:
    remediated: list[ResumeProfile] = []
    for p in profiles:
        r = copy.deepcopy(p)
        if (threshold - review_margin) <= r.screening_score < threshold:
            r.passed_screen = True
        else:
            r.passed_screen = r.screening_score >= threshold
        remediated.append(r)
    return remediated


def compare_strategies(
    original: list[ResumeProfile],
    threshold: float = 0.5,
) -> dict[str, AuditResult]:
    engine = BiasEngine()

    original_passed = [copy.deepcopy(p) for p in original]
    for p in original_passed:
        p.passed_screen = p.screening_score >= threshold
    baseline = engine.audit(original_passed)

    blind_profiles = apply_blind_screening(original, threshold)
    blind = engine.audit(blind_profiles)

    recalib_profiles = apply_weight_recalibration(original, threshold)
    recalib = engine.audit(recalib_profiles)

    review_profiles = apply_human_review(original, threshold)
    review = engine.audit(review_profiles)

    return {
        "Baseline": baseline,
        "Blind Screening": blind,
        "Weight Recalibration": recalib,
        "Human-in-the-Loop": review,
    }
