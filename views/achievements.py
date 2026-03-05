"""P12: Achievements Gallery — all achievements with earned/locked status."""

import streamlit as st
from services.gamification_service import get_user_achievements


def render():
    """Render the Achievements Gallery page."""
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    if not user_id:
        st.session_state["page"] = "login"
        st.rerun()
        return

    achievements = get_user_achievements(user_id)
    earned = [a for a in achievements if a.get("earned_at")]
    locked = [a for a in achievements if not a.get("earned_at")]

    # ── Header ──
    st.markdown(
        f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h2 style="margin: 0; font-weight: 800;">Achievement Gallery</h2>
                <p style="color: #94a3b8; margin: 0;">Track your milestones and accomplishments</p>
            </div>
            <div style="background: #15242b; border: 1px solid #1e3340; padding: 8px 16px; border-radius: 10px;">
                <span style="color: #10b981; font-weight: 800; font-size: 1.2rem;">{len(earned)}</span>
                <span style="color: #64748b; font-size: 0.85rem;"> / {len(achievements)} earned</span>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Progress bar
    pct = int(len(earned) / len(achievements) * 100) if achievements else 0
    st.markdown(
        f"""<div style="height: 6px; background: #1e3340; border-radius: 3px; overflow: hidden; margin-bottom: 1.5rem;">
            <div style="height: 100%; width: {pct}%; background: linear-gradient(90deg, #13a4ec, #10b981); border-radius: 3px;"></div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Filter
    filter_opt = st.radio("Filter", ["All", "Earned", "Locked"], horizontal=True, label_visibility="collapsed")

    if filter_opt == "Earned":
        display = earned
    elif filter_opt == "Locked":
        display = locked
    else:
        display = achievements

    if not display:
        st.info("No achievements match this filter.")
        return

    # Grid
    cols_per_row = 4
    for i in range(0, len(display), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(display):
                break
            ach = display[idx]
            is_earned = ach.get("earned_at") is not None
            with col:
                _render_badge(ach, is_earned)

    st.markdown("")


def _render_badge(ach: dict, is_earned: bool):
    """Render achievement badge card."""
    icon = ach.get("icon", "star")
    name = ach.get("name", "")
    desc = ach.get("description", "")
    earned_date = ach.get("earned_at", "")[:10] if ach.get("earned_at") else ""

    if is_earned:
        bg = "linear-gradient(135deg, #13a4ec, #6366f1)"
        border = "#13a4ec30"
        opacity = "1"
        date_html = f'<div style="color: #64748b; font-size: 0.7rem; margin-top: 4px;">Earned {earned_date}</div>'
    else:
        bg = "#1e3340"
        border = "#334155"
        opacity = "0.5"
        date_html = f'<div style="color: #475569; font-size: 0.7rem; margin-top: 4px;">{desc[:40]}</div>'

    st.markdown(
        f"""<div style="background: #15242b; border: 1px solid {border}; border-radius: 12px;
                       padding: 1.25rem; text-align: center; margin-bottom: 0.75rem; opacity: {opacity};">
            <div style="width: 56px; height: 56px; border-radius: 50%; margin: 0 auto 0.75rem auto;
                       background: {bg}; display: flex; align-items: center; justify-content: center;
                       font-size: 1.5rem;">{icon}</div>
            <div style="font-weight: 700; font-size: 0.85rem;">{name}</div>
            {date_html}
        </div>""",
        unsafe_allow_html=True,
    )
