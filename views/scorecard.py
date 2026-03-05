"""P7: Scorecard — full evaluation results, radar chart, feedback, XP."""

import json
import streamlit as st
from services.evaluation_service import get_evaluation_for_session
from services.scenario_service import get_scenario_by_id, get_checkpoints_for_scenario
from components.radar_chart import render_radar_chart
from utils.helpers import dict_from_row, score_color
from database.db import get_connection


def render():
    """Render the Scorecard page."""
    session_id = st.session_state.get("view_session_id")
    eval_result_from_state = st.session_state.get("eval_result")

    if not session_id:
        st.session_state["page"] = "agent_home"
        st.rerun()
        return

    conn = get_connection()
    session = dict_from_row(conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone())
    conn.close()

    if not session:
        st.error("Session not found.")
        return

    scenario = get_scenario_by_id(session["scenario_id"])
    checkpoints = get_checkpoints_for_scenario(session["scenario_id"])
    evaluation = get_evaluation_for_session(session_id)

    if not evaluation:
        st.warning("No evaluation found for this session.")
        if st.button("Back Home"):
            st.session_state["page"] = "agent_home"
            st.rerun()
        return

    overall = evaluation["overall_score"]
    s_color = score_color(overall)

    # ── XP popup (only on fresh eval) ──
    if eval_result_from_state:
        _render_xp_popup(eval_result_from_state)
        if "eval_result" in st.session_state:
            del st.session_state["eval_result"]

    # ── Score header + Goal ──
    goal_map = {
        "ACHIEVED": ("Goal Achieved", "#10b981", "check_circle"),
        "PARTIAL": ("Partially Achieved", "#f59e0b", "warning"),
        "FAILED": ("Goal Not Met", "#ef4444", "cancel"),
    }
    goal_label, goal_color, goal_icon = goal_map.get(evaluation.get("goal_achieved", "FAILED"), goal_map["FAILED"])

    col_score, col_goal = st.columns([1, 2])
    with col_score:
        st.markdown(
            f"""
            <div class="cc-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; font-weight: 900; color: {s_color}; line-height: 1;">{overall:.0f}<span style="font-size: 1.5rem;">%</span></div>
                <div style="color: #64748b; font-size: 0.85rem; margin-top: 0.5rem;">Overall Score</div>
                <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 0.75rem;
                           color: {goal_color}; font-weight: 600; font-size: 0.9rem;">
                    <span class="mi" style="color: {goal_color};">{goal_icon}</span> {goal_label}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_goal:
        # Radar chart
        render_radar_chart(evaluation)

    st.markdown("")

    # ── Checkpoint Checklist ──
    st.markdown(
        f"""<div class="cc-card" style="padding: 0; overflow: hidden; margin-bottom: 1rem;">
            <div style="padding: 1rem 1.25rem; border-bottom: 1px solid #1e3340; display: flex; justify-content: space-between; align-items: center; background: #15242b;">
                <h3 style="margin: 0; font-weight: 600;">Checkpoint Checklist</h3>
                <span style="color: #64748b; font-size: 0.8rem;">Scenario: {scenario.get('name', '')}</span>
            </div>""",
        unsafe_allow_html=True,
    )

    cp_results = evaluation.get("checkpoint_results", [])
    if isinstance(cp_results, str):
        try:
            cp_results = json.loads(cp_results)
        except (json.JSONDecodeError, TypeError):
            cp_results = []

    cp_map = {cp["id"]: cp for cp in checkpoints}
    for cpr in cp_results:
        cp_id = cpr.get("checkpoint_id")
        passed = cpr.get("passed", False)
        evidence = cpr.get("evidence", "")
        cp_info = cp_map.get(cp_id, {})
        cp_name = cp_info.get("name", f"Checkpoint {cp_id}")

        icon = "check_circle" if passed else "cancel"
        icon_color = "#10b981" if passed else "#ef4444"

        st.markdown(
            f"""<div style="padding: 1rem 1.25rem; border-bottom: 1px solid #1e3340; display: flex; gap: 12px;">
                <span class="mi" style="color: {icon_color}; flex-shrink: 0; margin-top: 2px;">{icon}</span>
                <div>
                    <div style="font-weight: 500; margin-bottom: 4px;">{cp_name}</div>
                    <div style="color: #94a3b8; font-size: 0.85rem;">{evidence if evidence else 'No evidence captured.'}</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Strengths + Improvements ──
    col_s, col_i = st.columns(2)

    with col_s:
        strengths = evaluation.get("strengths", [])
        if isinstance(strengths, str):
            try:
                strengths = json.loads(strengths)
            except (json.JSONDecodeError, TypeError):
                strengths = [strengths] if strengths else []
        items_html = "".join(f'<li style="margin-bottom: 6px;">{s}</li>' for s in strengths)
        st.markdown(
            f"""<div class="cc-card">
                <h4 style="color: #10b981; display: flex; align-items: center; gap: 6px; margin: 0 0 0.75rem 0;">
                    <span class="mi" style="color: #10b981;">thumb_up</span> Strengths
                </h4>
                <ul style="color: #94a3b8; font-size: 0.85rem; padding-left: 1.2rem; line-height: 1.6; margin: 0;">{items_html}</ul>
            </div>""",
            unsafe_allow_html=True,
        )

    with col_i:
        improvements = evaluation.get("improvements", [])
        if isinstance(improvements, str):
            try:
                improvements = json.loads(improvements)
            except (json.JSONDecodeError, TypeError):
                improvements = [improvements] if improvements else []
        items_html = "".join(f'<li style="margin-bottom: 6px;">{imp}</li>' for imp in improvements)
        st.markdown(
            f"""<div class="cc-card">
                <h4 style="color: #f59e0b; display: flex; align-items: center; gap: 6px; margin: 0 0 0.75rem 0;">
                    <span class="mi" style="color: #f59e0b;">trending_up</span> Areas for Improvement
                </h4>
                <ul style="color: #94a3b8; font-size: 0.85rem; padding-left: 1.2rem; line-height: 1.6; margin: 0;">{items_html}</ul>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("")

    # ── Coaching Tip ──
    tip = evaluation.get("coaching_tip", "")
    if tip:
        st.markdown(
            f"""<div style="background: #13a4ec10; border: 1px solid #13a4ec20; border-radius: 12px;
                           padding: 1.25rem; position: relative; overflow: hidden;">
                <h4 style="color: #13a4ec; display: flex; align-items: center; gap: 6px; margin: 0 0 0.5rem 0;">
                    <span class="mi" style="color: #13a4ec;">lightbulb</span> AI Coaching Tip
                </h4>
                <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6; margin: 0;">{tip}</p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("")

    # ── Transcript expander ──
    with st.expander("View Full Transcript"):
        transcript = session.get("transcript", "")
        if transcript:
            for line in transcript.split("\n"):
                if line.strip():
                    if line.strip().startswith("Agent:"):
                        st.markdown(f'<div style="color: #13a4ec; margin: 0.3rem 0;">{line}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="color: #f59e0b; margin: 0.3rem 0;">{line}</div>', unsafe_allow_html=True)
        else:
            st.caption("Transcript not available.")

    st.markdown("")

    # ── CTA buttons ──
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("Back Home", use_container_width=True):
            st.session_state["page"] = "agent_home"
            st.rerun()
    with col_b:
        if st.button("Try Again", use_container_width=True):
            st.session_state["page"] = "pre_call_briefing"
            st.rerun()
    with col_c:
        if st.button("Next Scenario", use_container_width=True, type="primary"):
            if "selected_scenario_id" in st.session_state:
                del st.session_state["selected_scenario_id"]
            st.session_state["page"] = "scenario_browser"
            st.rerun()


def _render_xp_popup(eval_result: dict):
    """Render XP gained popup."""
    total_xp = eval_result.get("total_xp_earned", 0)
    xp_entries = eval_result.get("xp_entries", [])
    new_achievements = eval_result.get("new_achievements", [])

    xp_lines = " · ".join(f"+{e['xp']} {e['reason']}" for e in xp_entries)

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #13a4ec15, #6366f115);
                   border: 1px solid #13a4ec30; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;
                   text-align: center;">
            <div style="font-size: 1.8rem; font-weight: 900; color: #13a4ec;">+{total_xp} XP</div>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;">{xp_lines}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if new_achievements:
        for ach in new_achievements:
            st.markdown(
                f"""<div style="background: #15242b; border: 1px solid #1e3340; border-radius: 12px;
                               padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.5rem;">{ach.get('icon', '🏆')}</span>
                    <div>
                        <div style="font-weight: 700; color: #f59e0b;">New Achievement!</div>
                        <div style="font-size: 0.85rem;">{ach.get('name', '')}</div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
