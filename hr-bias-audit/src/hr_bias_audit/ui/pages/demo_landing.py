import streamlit as st

from hr_bias_audit.models.audit_result import AuditResult


def show(result: AuditResult):
    st.header("HR Bias Audit — Demo")
    st.markdown(
        "This application demonstrates **automated bias detection and mitigation** "
        "for AI-driven resume screening platforms.  \n"
        "Navigate the tabs below to explore each use case."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Applicants Processed", result.total_applicants or "—")
    col2.metric("Pass Rate", f"{result.overall_pass_rate * 100:.1f}%" if result.total_applicants else "—")
    biased = sum(1 for b in result.bias_scores if b.is_biased)
    col3.metric("Bias Flags", biased if result.total_applicants else "—")
    compliant = "✅" if biased == 0 and result.total_applicants > 0 else "⚠️"
    col4.metric("Compliance Status", compliant)

    st.divider()

    use_cases = [
        ("📋 Bias Audit Report",
         "Run a comprehensive bias audit across **gender, ethnicity, and age** dimensions. "
         "View disparate impact ratios, statistical significance (chi-square), and group-level "
         "pass rates. Charts show disparities visually with regulatory thresholds overlaid."),
        ("🔍 What-If Simulator",
         "Adjust screening thresholds interactively and see how bias metrics change in real time. "
         "Explore questions like: *What if we raise the pass threshold?* or *What if we weight "
         "experience differently?*"),
        ("🛠️ Remediation Planner",
         "Compare mitigation strategies side-by-side: **blind screening**, **weight recalibration**, "
         "and **human-in-the-loop review**. See before/after metrics for disparate impact ratio, "
         "pass rate parity, and overall selection rate."),
        ("🔒 Compliance Dashboard",
         "Map audit results to regulatory frameworks: EEOC Uniform Guidelines, GDPR Art. 22, "
         "NYC Local Law 144, and EU AI Act. Track remediation actions and generate compliance "
         "reports."),
    ]

    for title, desc in use_cases:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.markdown(desc)

    st.divider()
    st.caption(
        "**How it works:** Upload resumes → Demographic signals are inferred from text "
        "(pronouns, experience keywords, name-based heuristics) → BiasEngine computes "
        "disparate impact ratios and chi-square significance → Results are visualised "
        "on dashboards with regulatory context."
    )
