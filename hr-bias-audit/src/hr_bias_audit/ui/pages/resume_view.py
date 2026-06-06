import streamlit as st
import pandas as pd

from hr_bias_audit.models.audit_result import AuditResult


def show(result: AuditResult):
    st.header("Resume Screening Overview")
    rows = []
    for bs in result.bias_scores:
        for gm in bs.group_metrics:
            rows.append({
                "Dimension": bs.dimension.value.capitalize(),
                "Group": gm.group.capitalize(),
                "Applicants": gm.applicant_count,
                "Pass Rate": f"{gm.pass_rate * 100:.1f}%",
                "Avg Score": f"{gm.avg_score:.2f}",
            })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No resume data loaded yet.")
