import streamlit as st
import pandas as pd
import plotly.express as px

from hr_bias_audit.models.resume import ResumeProfile
from hr_bias_audit.models.audit_result import AuditResult
from hr_bias_audit.analysis.remediation import compare_strategies
from hr_bias_audit.ui.components.metrics import severity_badge


def _summary_df(strategies: dict[str, AuditResult]) -> pd.DataFrame:
    rows = []
    for name, result in strategies.items():
        for bs in result.bias_scores:
            rows.append({
                "Strategy": name,
                "Dimension": bs.dimension.value.capitalize(),
                "Pass Rate": f"{result.overall_pass_rate * 100:.1f}%",
                "DI Ratio": bs.disparate_impact_ratio,
                "p-value": bs.statistical_significance,
                "Bias Flag": "⚠️" if bs.is_biased else "✅",
                "Severity": bs.severity,
            })
    return pd.DataFrame(rows)


def _comparison_chart(strategies: dict[str, AuditResult]) -> dict:
    rows = []
    for name, result in strategies.items():
        for bs in result.bias_scores:
            rows.append({
                "Strategy": name,
                "Dimension": bs.dimension.value.capitalize(),
                "Disparate Impact Ratio": bs.disparate_impact_ratio,
            })
    df = pd.DataFrame(rows)
    if df.empty:
        return {}
    fig = px.bar(
        df, x="Strategy", y="Disparate Impact Ratio",
        color="Dimension", barmode="group", text_auto=".3f",
        title="Disparate Impact Ratio by Strategy",
        height=400,
    )
    fig.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Threshold (0.8)")
    fig.add_hline(y=1.0, line_dash="dot", line_color="green", annotation_text="Parity")
    return fig


def show(result: AuditResult, profiles: list[ResumeProfile]):
    st.header("Remediation Planner")
    st.markdown("Compare bias mitigation strategies side by side.")

    if not profiles:
        st.info("Load sample data or upload resumes to use the planner.")
        return

    threshold = st.slider("Pass/Fail Threshold for Comparison", 0.0, 1.0, 0.5, 0.01)

    with st.spinner("Running remediation simulations..."):
        strategies = compare_strategies(profiles, threshold=threshold)

    df = _summary_df(strategies)

    tabs = st.tabs(list(strategies.keys()))
    for i, (name, result) in enumerate(strategies.items()):
        with tabs[i]:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Passed", result.total_passed)
            c2.metric("Pass Rate", f"{result.overall_pass_rate * 100:.1f}%")
            biased = sum(1 for b in result.bias_scores if b.is_biased)
            c3.metric("Bias Flags", biased, delta_color="inverse")

            for bs in result.bias_scores:
                with st.container(border=True):
                    cols = st.columns([1, 1, 2])
                    cols[0].markdown(f"**{bs.dimension.value.capitalize()}**")
                    cols[0].markdown(severity_badge(bs.severity), unsafe_allow_html=True)
                    cols[1].markdown(f"DI Ratio: **{bs.disparate_impact_ratio:.3f}**  \np-value: {bs.statistical_significance:.4f}")
                    cols[2].markdown(f"_{bs.recommendation}_")

    st.subheader("Side-by-Side Comparison")
    fig = _comparison_chart(strategies)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key="remediation_comparison")

    with st.expander("View detailed comparison table"):
        st.dataframe(df, use_container_width=True)

    st.subheader("Recommended Action Plan")
    baseline = strategies.get("Baseline")
    if baseline and any(b.is_biased for b in baseline.bias_scores):
        st.markdown(
            """
1. **Apply blind screening** first — removes demographic signals from the review process
2. **If bias persists**, enable **weight recalibration** with targeted score boosts
3. **Add human-in-the-loop review** for borderline candidates (±10% of threshold)
4. **Schedule automated audits** per batch to track progress over time
            """
        )
    else:
        st.success("No bias detected in baseline. Continue monitoring with regular audits.")
