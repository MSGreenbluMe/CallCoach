"""P3: Scenario Browser — browse and filter available training scenarios."""

import streamlit as st
from services.scenario_service import get_all_scenarios, get_user_best_score_for_scenario, get_user_scenario_status
from config import CATEGORIES, CATEGORY_LABELS, CATEGORY_COLORS, LANGUAGES
from utils.helpers import score_color

# Gradient backgrounds per category (matching UX)
_CAT_GRADIENTS = {
    "SALES": "linear-gradient(135deg, #f97316, #ef4444)",
    "RETENTION": "linear-gradient(135deg, #f59e0b, #d97706)",
    "TECH_SUPPORT": "linear-gradient(135deg, #10b981, #14b8a6)",
    "COMPLAINTS": "linear-gradient(135deg, #3b82f6, #8b5cf6)",
    "BILLING": "linear-gradient(135deg, #8b5cf6, #6366f1)",
    "ONBOARDING": "linear-gradient(135deg, #06b6d4, #3b82f6)",
}


def render():
    """Render the Scenario Browser page."""
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    st.markdown(
        """<h2 style="font-weight: 800; margin-bottom: 0.25rem;">Scenario Library</h2>
           <p style="color: #94a3b8; margin-bottom: 1rem;">Choose a scenario and start practicing</p>""",
        unsafe_allow_html=True,
    )

    # Filters row
    col_f1, col_f2, col_f3, col_f4 = st.columns([3, 2, 2, 1])
    with col_f1:
        selected_category = st.selectbox(
            "Category",
            options=["all"] + CATEGORIES,
            format_func=lambda x: "All Categories" if x == "all" else CATEGORY_LABELS.get(x, x),
        )
    with col_f2:
        difficulty_filter = st.slider("Difficulty", 1, 5, (1, 5))
    with col_f3:
        language_filter = st.selectbox(
            "Language",
            options=["all"] + list(LANGUAGES.keys()),
            format_func=lambda x: "All" if x == "all" else LANGUAGES.get(x, x),
        )
    with col_f4:
        st.markdown(f'<div style="padding-top: 1.7rem; color: #64748b; font-size: 0.8rem;"></div>', unsafe_allow_html=True)

    # Get and filter scenarios
    scenarios = get_all_scenarios(active_only=True)

    if selected_category != "all":
        scenarios = [s for s in scenarios if s["category"] == selected_category]
    scenarios = [s for s in scenarios if difficulty_filter[0] <= s["difficulty"] <= difficulty_filter[1]]
    if language_filter != "all":
        scenarios = [s for s in scenarios if s["language"] == language_filter]

    st.markdown(
        f'<p style="color: #64748b; font-size: 0.85rem; margin: 0.5rem 0;">{len(scenarios)} scenarios found</p>',
        unsafe_allow_html=True,
    )

    if not scenarios:
        st.info("No scenarios match your filters.")
        return

    # Render scenario cards in grid
    cols_per_row = 3
    for i in range(0, len(scenarios), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(scenarios):
                break
            with col:
                _render_scenario_card(scenarios[idx], user_id)


def _render_scenario_card(scenario: dict, user_id: int):
    """Render a single scenario card matching UX design."""
    cat_label = CATEGORY_LABELS.get(scenario["category"], scenario["category"])
    gradient = _CAT_GRADIENTS.get(scenario["category"], "linear-gradient(135deg, #3b82f6, #6366f1)")
    diff = scenario.get("difficulty", 1)
    dur_min = scenario.get("estimated_duration_min", "?")

    # Stars
    stars_html = ""
    for i in range(1, 6):
        color = "#f59e0b" if i <= diff else "#334155"
        stars_html += f'<span class="mi" style="font-size: 14px; color: {color};">star</span>'

    diff_labels = {1: "Beginner", 2: "Easy", 3: "Intermediate", 4: "Advanced", 5: "Expert"}
    diff_label = diff_labels.get(diff, "")

    # User status
    status = get_user_scenario_status(user_id, scenario["id"])
    best_score = get_user_best_score_for_scenario(user_id, scenario["id"])

    # Status badge in header
    status_badge = ""
    if status == "new":
        status_badge = '<span style="background: #13a4ec; color: white; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">NEW</span>'

    # Score display
    if best_score is not None:
        s_col = score_color(best_score)
        if best_score >= 95:
            score_html = f'<span style="font-weight: 700; color: #f59e0b; display: flex; align-items: center; gap: 2px;"><span class="mi" style="font-size: 14px;">workspace_premium</span> {best_score:.0f}%</span>'
        else:
            score_html = f'<span style="font-weight: 700; color: {s_col};">{best_score:.0f}%</span>'
    else:
        score_html = '<span style="color: #64748b;">Not attempted</span>'

    # Button style based on status
    if status == "mastered":
        btn_label = "Retake Scenario"
        btn_icon = "replay"
    else:
        btn_label = "Start Training"
        btn_icon = "play_arrow"

    st.markdown(
        f"""
        <div style="border: 1px solid #1e3340; border-radius: 12px; overflow: hidden; background: #15242b; margin-bottom: 0.5rem;">
            <div style="height: 130px; {f'background: {gradient}'};  position: relative; padding: 12px;">
                <div style="display: flex; gap: 6px;">
                    <span style="background: rgba(0,0,0,0.4); backdrop-filter: blur(8px); color: white;
                                font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 6px;">{cat_label}</span>
                    {status_badge}
                </div>
                <div style="position: absolute; top: 12px; right: 12px;">
                    <span style="background: rgba(255,255,255,0.9); color: #1e293b; font-size: 0.7rem;
                                font-weight: 600; padding: 3px 10px; border-radius: 6px;">{dur_min} min</span>
                </div>
            </div>
            <div style="padding: 1rem;">
                <div style="font-weight: 700; font-size: 1rem; margin-bottom: 0.4rem; line-height: 1.3;">
                    {scenario['name']}
                </div>
                <div style="margin-bottom: 0.5rem;">
                    {stars_html}
                    <span style="color: #64748b; font-size: 0.75rem; margin-left: 4px;">{diff_label}</span>
                </div>
                <p style="color: #94a3b8; font-size: 0.8rem; line-height: 1.4; margin-bottom: 0.75rem;
                          display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                    {scenario.get('description', '')[:100]}
                </p>
                <div style="border-top: 1px solid #1e3340; padding-top: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; margin-bottom: 0.5rem;">
                        <span style="color: #64748b;">Personal Best</span>
                        {score_html}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(f"{btn_label}", key=f"scenario_{scenario['id']}", use_container_width=True,
                 type="primary" if status == "new" else "secondary"):
        st.session_state["selected_scenario_id"] = scenario["id"]
        st.session_state["page"] = "pre_call_briefing"
        st.rerun()
