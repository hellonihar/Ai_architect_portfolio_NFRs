import streamlit as st

from hr_bias_audit.models.audit_result import AuditResult


REQUIREMENTS = [
    ("EEOC Uniform Guidelines", "Disparate impact ratio ≥ 0.8 across all protected groups"),
    ("GDPR Art. 22", "Automated decision-making must be explainable and contestable"),
    ("NYC Local Law 144", "Annual bias audit required for automated employment decision tools"),
    ("EU AI Act (high-risk)", "Conformity assessment, human oversight, technical documentation"),
]


def show(result: AuditResult):
    st.header("Compliance Dashboard")
    st.caption("Regulatory alignment for AI-driven hiring tools")

    for bs in result.bias_scores:
        if bs.is_biased:
            st.warning(
                f"**{bs.dimension.value.capitalize()} bias detected** — "
                f"DI ratio {bs.disparate_impact_ratio:.3f} (threshold: 0.8). "
                f"{bs.recommendation}"
            )

    st.subheader("Regulatory Checklist")
    for name, desc in REQUIREMENTS:
        if any(bs.is_biased for bs in result.bias_scores):
            status = "⚠️ Needs Review"
        else:
            status = "✅ Compliant"
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{name}**  \n{desc}")
            c2.markdown(f"**{status}**")

    st.subheader("Remediation Actions")
    st.markdown(
        """
- **Blind screening** — Remove name, gender, age indicators from resumes before scoring
- **Weight recalibration** — Adjust scoring model to equalize pass rates across groups
- **Regular auditing** — Schedule automated audits per batch (weekly/monthly)
- **Human-in-the-loop** — Flag borderline cases for manual review
        """
    )
