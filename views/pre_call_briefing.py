"""P4: Pre-Call Briefing — context, goals, checkpoints before starting a call."""

import streamlit as st
from services.scenario_service import get_scenario_by_id, get_checkpoints_for_scenario
from config import CATEGORY_LABELS


def render():
    """Render the Pre-Call Briefing page."""
    scenario_id = st.session_state.get("selected_scenario_id")
    if not scenario_id:
        st.session_state["page"] = "scenario_browser"
        st.rerun()
        return

    scenario = get_scenario_by_id(scenario_id)
    if not scenario:
        st.error("Scenario not found.")
        return

    checkpoints = get_checkpoints_for_scenario(scenario_id)
    cat_label = CATEGORY_LABELS.get(scenario["category"], scenario["category"])
    diff = scenario.get("difficulty", 1)

    # Stars HTML
    stars_html = ""
    for i in range(1, 6):
        color = "#f59e0b" if i <= diff else "#334155"
        stars_html += f'<span class="mi" style="font-size: 16px; color: {color};">star</span>'

    # ── Header section ──
    st.markdown(
        f"""
        <div class="cc-card" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <div>
                <span style="background: #13a4ec20; color: #13a4ec; font-size: 0.7rem; font-weight: 700;
                            padding: 3px 12px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px;">{cat_label}</span>
                <h1 style="font-size: 1.8rem; font-weight: 900; margin: 0.5rem 0 0 0;">{scenario['name']}</h1>
            </div>
            <div style="background: #1e3340; padding: 8px 16px; border-radius: 10px; border: 1px solid #2a4050; text-align: center;">
                <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 4px;">Difficulty</div>
                <div>{stars_html}</div>
                <div style="font-weight: 700; font-size: 0.85rem; margin-top: 2px;">{diff}/5</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Two column layout ──
    col_left, col_right = st.columns(2)

    with col_left:
        # Context
        st.markdown(
            f"""
            <div class="cc-card" style="margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
                    <span class="mi" style="color: #13a4ec;">info</span>
                    <h3 style="margin: 0; font-weight: 700;">Context</h3>
                </div>
                <p style="color: #94a3b8; line-height: 1.6; margin: 0;">{scenario['description']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Customer persona
        initials = "".join(w[0] for w in scenario.get("persona_name", "?").split()[:2]).upper()
        st.markdown(
            f"""
            <div class="cc-card">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
                    <span class="mi" style="color: #13a4ec;">person</span>
                    <h3 style="margin: 0; font-weight: 700;">Your Customer</h3>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 56px; height: 56px; border-radius: 50%; background: #1e3340;
                               display: flex; align-items: center; justify-content: center;
                               font-weight: 700; font-size: 1.1rem; color: #13a4ec; border: 2px solid #13a4ec30;
                               flex-shrink: 0;">{initials}</div>
                    <div>
                        <div style="font-weight: 700; font-size: 1.05rem;">{scenario['persona_name']}</div>
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">{scenario.get('persona_background', '')}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        # Goal
        st.markdown(
            f"""
            <div class="cc-card" style="border-left: 4px solid #13a4ec; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
                    <span class="mi" style="color: #13a4ec;">flag</span>
                    <h3 style="margin: 0; font-weight: 700;">Your Goal</h3>
                </div>
                <p style="font-size: 1rem; font-weight: 500; line-height: 1.5; margin: 0;">{scenario['primary_goal']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Checkpoints
        cp_html = ""
        for cp in checkpoints:
            cp_html += f"""
            <div style="display: flex; align-items: flex-start; gap: 10px; padding: 0.5rem 0;">
                <div style="width: 20px; height: 20px; border-radius: 4px; border: 1px solid #334155;
                           background: #1e3340; flex-shrink: 0; margin-top: 2px;"></div>
                <span style="font-weight: 500;">{cp['name']}</span>
            </div>"""

        st.markdown(
            f"""
            <div class="cc-card" style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
                    <span class="mi" style="color: #13a4ec;">fact_check</span>
                    <h3 style="margin: 0; font-weight: 700;">Checkpoints</h3>
                </div>
                {cp_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    # ── Footer with Start button ──
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            """<div style="display: flex; align-items: center; gap: 8px; color: #64748b; font-size: 0.85rem; padding-top: 0.5rem;">
                <span class="mi" style="font-size: 18px;">mic</span>
                Note: This call will be recorded and evaluated by AI.
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Start Training Call", use_container_width=True, type="primary"):
            st.session_state["page"] = "active_call"
            st.rerun()
