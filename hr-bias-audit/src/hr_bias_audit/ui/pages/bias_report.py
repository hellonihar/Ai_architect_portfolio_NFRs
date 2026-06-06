import streamlit as st
from hr_bias_audit.ui.components.metrics import severity_badge
from hr_bias_audit.ui.components.charts import (
    pass_rate_by_group_chart, disparate_impact_chart,
)
from hr_bias_audit.models.audit_result import AuditResult


def show(result: AuditResult):
    st.header("Bias Audit Report")
    st.caption(f"Audit timestamp: {result.audit_timestamp}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applicants", result.total_applicants)
    col2.metric("Passed Screen", result.total_passed)
    col3.metric("Overall Pass Rate", f"{result.overall_pass_rate * 100:.1f}%")
    biased_count = sum(1 for b in result.bias_scores if b.is_biased)
    col4.metric("Bias Flags", biased_count, delta_color="inverse")

    for bs in result.bias_scores:
        with st.expander(
            f"{bs.dimension.value.capitalize()} Bias "
            f"— DI Ratio: {bs.disparate_impact_ratio:.3f} "
            f"{severity_badge(bs.severity)}",
            expanded=bs.is_biased,
        ):
            st.markdown(severity_badge(bs.severity), unsafe_allow_html=True)
            st.markdown(f"**p-value:** {bs.statistical_significance:.4f}")
            st.markdown(f"**Recommendation:** {bs.recommendation}")

            gm_df = [
                {
                    "Group": g.group.capitalize(),
                    "Applicants": g.applicant_count,
                    "Pass Rate": f"{g.pass_rate * 100:.1f}%",
                    "Avg Score": f"{g.avg_score:.2f}",
                }
                for g in bs.group_metrics
            ]
            st.dataframe(gm_df, use_container_width=True)

    st.subheader("Charts")
    fig1 = pass_rate_by_group_chart(result.bias_scores)
    fig2 = disparate_impact_chart(result.bias_scores)
    if fig1 and fig2:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(fig1, use_container_width=True, key="report_pass_rate")
        with right:
            st.plotly_chart(fig2, use_container_width=True, key="report_di_ratio")
