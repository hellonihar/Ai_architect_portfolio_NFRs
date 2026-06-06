import streamlit as st

from hr_bias_audit.analysis.bias_engine import BiasEngine
from hr_bias_audit.analysis.demographic_parser import DemographicParser
from hr_bias_audit.ingest.resume_parser import ResumeParser
from hr_bias_audit.ui.pages import (
    demo_landing, bias_report, what_if, remediation, resume_view, compliance,
)
from hr_bias_audit.models.audit_result import AuditResult

st.set_page_config(
    page_title="HR Bias Audit",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚖️ HR Bias Audit")
st.markdown(
    "Automated bias detection & mitigation for AI-driven resume screening."
)


def main():
    if "audit_result" not in st.session_state:
        st.session_state.audit_result = AuditResult(
            total_applicants=0, total_passed=0, overall_pass_rate=0.0,
            bias_scores=[], audit_timestamp="",
        )
    if "profiles" not in st.session_state:
        st.session_state.profiles = []

    with st.sidebar:
        st.header("Data Source")
        uploaded = st.file_uploader(
            "Upload resumes (.txt, .pdf, .docx)",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
        )

        if uploaded and st.button("Run Bias Audit", type="primary"):
            profiles = []
            for f in uploaded:
                temp_path = f"src/data/{f.name}"
                with open(temp_path, "wb") as out:
                    out.write(f.getbuffer())
                profile = ResumeParser.parse(temp_path)
                profile.screening_score = 0.5
                profile.passed_screen = profile.screening_score >= 0.5
                profile = DemographicParser.enrich(profile)
                profiles.append(profile)

            engine = BiasEngine()
            result = engine.audit(profiles)
            st.session_state.profiles = profiles
            st.session_state.audit_result = result
            st.success(f"Audit complete — {len(profiles)} resumes analysed.")
            st.rerun()

        st.divider()
        st.caption("Sample Data")
        if st.button("Load 8-profile sample"):
            from hr_bias_audit.analysis import sample_data
            profiles = sample_data.load()
            engine = BiasEngine()
            result = engine.audit(profiles)
            st.session_state.profiles = profiles
            st.session_state.audit_result = result
            st.success("Sample data loaded.")
            st.rerun()

        if st.button("Load 250-profile demo (biased)"):
            from hr_bias_audit.analysis import demo_data
            profiles = demo_data.generate(batch_size=250, bias_scale=1.0)
            engine = BiasEngine()
            result = engine.audit(profiles)
            st.session_state.profiles = profiles
            st.session_state.audit_result = result
            st.success("250 demo profiles loaded with simulated bias patterns.")
            st.rerun()

        if st.button("Load 250-profile demo (fair)"):
            from hr_bias_audit.analysis import demo_data
            profiles = demo_data.generate(batch_size=250, bias_scale=0.0)
            engine = BiasEngine()
            result = engine.audit(profiles)
            st.session_state.profiles = profiles
            st.session_state.audit_result = result
            st.success("250 fair profiles loaded (bias scale = 0).")
            st.rerun()

    tabs = st.tabs([
        "🏠 Demo Overview",
        "📊 Bias Audit Report",
        "🔍 What-If Simulator",
        "🛠️ Remediation Planner",
        "📄 Resume View",
        "🔒 Compliance",
    ])

    with tabs[0]:
        demo_landing.show(st.session_state.audit_result)
    with tabs[1]:
        bias_report.show(st.session_state.audit_result)
    with tabs[2]:
        what_if.show(st.session_state.audit_result, st.session_state.profiles)
    with tabs[3]:
        remediation.show(st.session_state.audit_result, st.session_state.profiles)
    with tabs[4]:
        resume_view.show(st.session_state.audit_result)
    with tabs[5]:
        compliance.show(st.session_state.audit_result)


if __name__ == "__main__":
    main()
