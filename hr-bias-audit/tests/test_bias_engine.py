import pytest
from hr_bias_audit.analysis.bias_engine import BiasEngine
from hr_bias_audit.models.resume import ResumeProfile


def _make_profile(
    g: str, a: str, e: str, score: float, passed: bool
) -> ResumeProfile:
    return ResumeProfile(
        id="", name="", email="", raw_text="",
        inferred_gender=g, inferred_age_group=a, inferred_ethnicity=e,
        screening_score=score, passed_screen=passed,
    )


def test_audit_empty():
    engine = BiasEngine()
    result = engine.audit([])
    assert result.total_applicants == 0


def test_audit_all_pass_same_group():
    profiles = [
        _make_profile("female", "30_50", "unknown", 0.9, True) for _ in range(5)
    ]
    engine = BiasEngine()
    result = engine.audit(profiles)
    assert result.total_applicants == 5
    assert result.total_passed == 5


def test_audit_detects_disparity():
    profiles = [
        _make_profile("male", "30_50", "unknown", 0.9, True) for _ in range(5)
    ] + [
        _make_profile("female", "under_30", "diverse_signal", 0.3, False)
        for _ in range(5)
    ]
    engine = BiasEngine()
    result = engine.audit(profiles)
    bias = {b.dimension.value: b for b in result.bias_scores}
    assert bias.get("gender") is not None
