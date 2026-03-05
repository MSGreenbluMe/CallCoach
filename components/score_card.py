"""Score display component."""

import streamlit as st
from utils.helpers import score_color


def render_big_score(score: float, label: str = "Celkové skóre"):
    """Render a large score number with color coding."""
    color = score_color(score)
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1.5rem 0;">
            <div style="font-size: 0.9rem; color: #6B7280; margin-bottom: 0.25rem;">{label}</div>
            <div style="font-size: 4rem; font-weight: 800; color: {color}; line-height: 1;">{score:.0f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(value: str, label: str, icon: str = "", delta: str = None):
    """Render a single stat card."""
    delta_html = ""
    if delta:
        delta_color = "#10B981" if delta.startswith("+") or delta.startswith("↑") else "#EF4444"
        delta_html = f'<span style="font-size: 0.75rem; color: {delta_color}; margin-left: 0.5rem;">{delta}</span>'

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1E293B, #334155); border-radius: 12px;
                    padding: 1.25rem; border: 1px solid #475569;">
            <div style="font-size: 0.8rem; color: #94A3B8;">{icon} {label}</div>
            <div style="font-size: 1.75rem; font-weight: 700; color: #F1F5F9; margin-top: 0.25rem;">
                {value}{delta_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_xp_bar(current_xp: int, level: int, level_name: str, xp_current_level: int, xp_next_level: int):
    """Render XP progress bar to next level."""
    if xp_next_level <= xp_current_level:
        progress = 100
    else:
        progress = ((current_xp - xp_current_level) / (xp_next_level - xp_current_level)) * 100
        progress = max(0, min(100, progress))

    st.markdown(
        f"""
        <div style="background: #1E293B; border-radius: 12px; padding: 1rem; border: 1px solid #475569;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div>
                    <span style="background: linear-gradient(135deg, #3B82F6, #8B5CF6); color: white;
                                padding: 0.2rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                        Lv.{level} {level_name}
                    </span>
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8;">{current_xp} / {xp_next_level} XP</div>
            </div>
            <div style="background: #334155; border-radius: 10px; height: 10px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, #3B82F6, #8B5CF6); height: 100%;
                           width: {progress}%; border-radius: 10px; transition: width 0.5s ease;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
