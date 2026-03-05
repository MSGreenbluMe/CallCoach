"""Achievement badge component."""

import streamlit as st


def render_achievement_badge(achievement: dict, earned: bool = False, size: str = "medium"):
    """Render a single achievement badge."""
    if earned:
        bg = "linear-gradient(135deg, #1E3A5F, #2D4A7C)"
        border = "#3B82F6"
        opacity = "1"
        icon_filter = ""
        earned_text = f"<div style='font-size: 0.65rem; color: #60A5FA; margin-top: 0.2rem;'>✓ Získané</div>"
    else:
        bg = "#1E293B"
        border = "#475569"
        opacity = "0.5"
        icon_filter = "filter: grayscale(100%);"
        earned_text = "<div style='font-size: 0.65rem; color: #6B7280; margin-top: 0.2rem;'>🔒 Zamknuté</div>"

    sizes = {
        "small": ("3rem", "1.5rem", "0.6rem"),
        "medium": ("4.5rem", "2rem", "0.7rem"),
        "large": ("6rem", "2.5rem", "0.8rem"),
    }
    width, icon_size, text_size = sizes.get(size, sizes["medium"])

    st.markdown(
        f"""
        <div style="background: {bg}; border: 2px solid {border}; border-radius: 12px;
                    padding: 0.75rem; text-align: center; opacity: {opacity}; min-width: {width};">
            <div style="font-size: {icon_size}; {icon_filter}">{achievement.get('icon', '🏅')}</div>
            <div style="font-size: {text_size}; font-weight: 600; color: #E2E8F0; margin-top: 0.25rem;">
                {achievement.get('name', '')}
            </div>
            {earned_text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_achievement_row(achievements: list[dict]):
    """Render a horizontal row of achievement badges."""
    if not achievements:
        st.caption("Zatiaľ žiadne achievementy")
        return

    cols = st.columns(min(len(achievements), 5))
    for i, ach in enumerate(achievements[:5]):
        with cols[i]:
            earned = ach.get("earned_at") is not None
            render_achievement_badge(ach, earned=earned, size="small")
