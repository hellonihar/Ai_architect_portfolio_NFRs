import streamlit as st
import copy
import pandas as pd

from hr_bias_audit.models.resume import ResumeProfile
from hr_bias_audit.models.audit_result import AuditResult, BiasDimension
from hr_bias_audit.analysis.bias_engine import BiasEngine
from hr_bias_audit.ui.components.metrics import severity_badge
from hr_bias_audit.ui.components.charts import (
    pass_rate_by_group_chart, disparate_impact_chart, score_distribution_chart,
)


def simulate(
    profiles: list[ResumeProfile],
    threshold: float,
    boost_female: float,
    boost_under30: float,
    boost_over50: float,
    boost_diverse: float,
) -> AuditResult:
    adjusted: list[ResumeProfile] = []
    for p in profiles:
        r = copy.deepcopy(p)
        boost = 0.0
        if r.inferred_gender == "female":
            boost += boost_female
        if r.inferred_age_group == "under_30":
            boost += boost_under30
        if r.inferred_age_group == "over_50":
            boost += boost_over50
        if r.inferred_ethnicity != "unknown":
            boost += boost_diverse
        r.screening_score = min(0.98, max(0.05, r.screening_score + boost))
        r.passed_screen = r.screening_score >= threshold
        adjusted.append(r)
    return BiasEngine().audit(adjusted)


def show(result: AuditResult, profiles: list[ResumeProfile]):
    st.header("What-If Simulator")
    st.markdown("Adjust screening parameters and see how bias metrics change in real time.")

    if not profiles:
        st.info("Load sample data or upload resumes to use the simulator.")
        return

    with st.container(border=True):
        st.markdown("**Screening Parameters**")
        col1, col2 = st.columns([2, 3])
        with col1:
            threshold = st.slider("Pass/Fail Threshold", 0.0, 1.0, 0.5, 0.01)
        with col2:
            st.caption("Candidates with scores below this threshold are rejected.")

        st.markdown("**Equity Adjustments (score boosts)**")
        cols = st.columns(4)
        with cols[0]:
            boost_female = st.slider("Female boost", -0.2, 0.3, 0.0, 0.01, format="%+0.02f")
        with cols[1]:
            boost_under30 = st.slider("Under-30 boost", -0.2, 0.3, 0.0, 0.01, format="%+0.02f")
        with cols[2]:
            boost_over50 = st.slider("Over-50 boost", -0.2, 0.3, 0.0, 0.01, format="%+0.02f")
        with cols[3]:
            boost_diverse = st.slider("Diverse signal boost", -0.2, 0.3, 0.0, 0.01, format="%+0.02f")

    sim_result = simulate(profiles, threshold, boost_female, boost_under30, boost_over50, boost_diverse)

    st.subheader("Simulated Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Applicants", sim_result.total_applicants)
    c2.metric("Passed", sim_result.total_passed)
    c3.metric("Pass Rate", f"{sim_result.overall_pass_rate * 100:.1f}%")
    biased_count = sum(1 for b in sim_result.bias_scores if b.is_biased)
    c4.metric("Bias Flags", biased_count, delta_color="inverse")

    for bs in sim_result.bias_scores:
        with st.expander(
            f"{bs.dimension.value.capitalize()} — DI Ratio: {bs.disparate_impact_ratio:.3f} "
            f"{severity_badge(bs.severity)}",
            expanded=bs.is_biased,
        ):
            st.markdown(severity_badge(bs.severity), unsafe_allow_html=True)
            st.markdown(f"**p-value:** {bs.statistical_significance:.4f}")
            st.markdown(f"**Recommendation:** {bs.recommendation}")
            gm_df = pd.DataFrame([{
                "Group": g.group.capitalize(),
                "Applicants": g.applicant_count,
                "Pass Rate": f"{g.pass_rate * 100:.1f}%",
                "Avg Score": f"{g.avg_score:.2f}",
            } for g in bs.group_metrics])
            st.dataframe(gm_df, use_container_width=True)

    fig1 = pass_rate_by_group_chart(sim_result.bias_scores)
    fig2 = disparate_impact_chart(sim_result.bias_scores)
    fig3 = score_distribution_chart(sim_result.bias_scores)
    if fig1 and fig2:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(fig1, use_container_width=True, key="whatif_pass_rate")
        with right:
            st.plotly_chart(fig2, use_container_width=True, key="whatif_di_ratio")
    if fig3:
        st.plotly_chart(fig3, use_container_width=True, key="whatif_score_dist")
