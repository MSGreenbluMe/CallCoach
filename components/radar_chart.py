"""Radar chart component for call quality visualization."""

import plotly.graph_objects as go
import streamlit as st


def render_radar_chart(scores: dict, title: str = "Kvalita hovoru"):
    """Render a radar chart with 7 quality criteria scores.

    Args:
        scores: dict with keys like communication_clarity, empathy_rapport, etc.
               Values can be floats (1-10) or dicts with 'score' key.
    """
    labels = [
        "Clarity",
        "Empathy",
        "Listening",
        "Language",
        "Structure",
        "Control",
        "Objections",
    ]

    keys = [
        "communication_clarity",
        "empathy_rapport",
        "active_listening",
        "professional_language",
        "call_structure",
        "call_control",
        "objection_handling",
    ]

    values = []
    for key in keys:
        val = scores.get(key, 5)
        if isinstance(val, dict):
            val = val.get("score", 5)
        values.append(val if val is not None else 5)

    # Close the polygon
    values_closed = values + [values[0]]
    labels_closed = labels + [labels[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(19, 164, 236, 0.15)",
        line=dict(color="#13a4ec", width=2),
        marker=dict(size=6, color="#13a4ec"),
        name="Score",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickvals=[2, 4, 6, 8, 10],
                gridcolor="rgba(156, 163, 175, 0.3)",
            ),
            angularaxis=dict(
                gridcolor="rgba(156, 163, 175, 0.3)",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        title=dict(text=title, font=dict(size=14, color="#94a3b8")),
        margin=dict(l=60, r=60, t=40, b=20),
        height=350,
        font=dict(color="#94a3b8"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)
