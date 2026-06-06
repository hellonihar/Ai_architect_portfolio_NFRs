import streamlit as st


def metric_card(label: str, value: str, delta: str = "", color: str = "blue"):
    colors = {
        "green": "#28a745", "red": "#dc3545",
        "blue": "#007bff", "orange": "#fd7e14",
    }
    bg = colors.get(color, "#007bff")
    st.markdown(
        f"""
        <div style="
            background:{bg}; color:white; padding:16px 12px; border-radius:8px;
            text-align:center; margin-bottom:8px;
        ">
            <div style="font-size:12px; opacity:0.85;">{label}</div>
            <div style="font-size:28px; font-weight:700;">{value}</div>
            {f'<div style="font-size:13px;">{delta}</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def severity_badge(severity: str) -> str:
    colors = {"high": "red", "medium": "orange", "low": "green"}
    c = colors.get(severity, "gray")
    return f'<span style="background:{c}; color:white; padding:2px 10px; border-radius:12px; font-size:11px;">{severity.upper()}</span>'
