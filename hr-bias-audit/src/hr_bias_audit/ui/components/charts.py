import plotly.express as px
import pandas as pd

from hr_bias_audit.models.audit_result import BiasScore, BiasDimension


def pass_rate_by_group_chart(bias_scores: list[BiasScore]) -> dict:
    rows = []
    for bs in bias_scores:
        for gm in bs.group_metrics:
            rows.append({
                "Dimension": bs.dimension.value.capitalize(),
                "Group": gm.group.capitalize(),
                "Pass Rate": round(gm.pass_rate * 100, 1),
                "Applicants": gm.applicant_count,
            })
    df = pd.DataFrame(rows)
    if df.empty:
        return {}
    fig = px.bar(
        df, x="Group", y="Pass Rate", color="Dimension",
        barmode="group", text="Pass Rate",
        title="Pass Rate by Demographic Group",
        height=400,
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    return fig


def disparate_impact_chart(bias_scores: list[BiasScore]) -> dict:
    rows = [
        {
            "Dimension": bs.dimension.value.capitalize(),
            "Disparate Impact Ratio": bs.disparate_impact_ratio,
        }
        for bs in bias_scores
    ]
    df = pd.DataFrame(rows)
    if df.empty:
        return {}
    fig = px.bar(
        df, x="Dimension", y="Disparate Impact Ratio",
        color="Dimension", text_auto=".3f",
        title="Disparate Impact Ratio (1.0 = perfect parity)",
        height=350,
    )
    fig.add_hline(
        y=0.8, line_dash="dash", line_color="red",
        annotation_text="Threshold (0.8)",
    )
    fig.add_hline(
        y=1.0, line_dash="dot", line_color="green",
        annotation_text="Parity (1.0)",
    )
    return fig


def score_distribution_chart(bias_scores: list[BiasScore]) -> dict:
    rows = []
    for bs in bias_scores:
        for gm in bs.group_metrics:
            rows.extend(
                [{
                    "Dimension": bs.dimension.value.capitalize(),
                    "Group": gm.group.capitalize(),
                    "Score": gm.avg_score,
                }]
            )
    df = pd.DataFrame(rows)
    if df.empty:
        return {}
    fig = px.bar(
        df, x="Group", y="Score", color="Dimension",
        barmode="group", text_auto=".2f",
        title="Average Screening Score by Group",
        height=400,
    )
    return fig
