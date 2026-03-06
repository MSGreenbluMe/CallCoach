"""P10: Scenario Management — list, toggle, create/edit scenarios (Manager view)."""

import streamlit as st
from services.scenario_service import get_all_scenarios_with_stats, toggle_scenario_active
from config import CATEGORY_LABELS, CATEGORY_COLORS
from utils.helpers import score_color


def render():
    """Render the Scenario Management page."""
    user = st.session_state.get("user", {})
    if user.get("role") not in ("manager", "admin"):
        st.session_state["page"] = "login"
        st.rerun()
        return

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(
            """<h2 style="font-weight: 800; margin-bottom: 0.25rem;">Scenario Management</h2>
               <p style="color: #94a3b8;">Create, edit and manage training scenarios</p>""",
            unsafe_allow_html=True,
        )
    with col_h2:
        st.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
        if st.button("Create New Scenario", use_container_width=True, type="primary"):
            st.session_state["edit_scenario_id"] = None
            st.session_state["page"] = "scenario_editor"
            st.rerun()

    # Get scenarios with stats
    scenarios = get_all_scenarios_with_stats()

    if not scenarios:
        st.info("No scenarios yet. Click 'Create New Scenario' to add one.")
        return

    # Stats summary
    active_count = sum(1 for s in scenarios if s.get("is_active"))
    total_completions = sum(s.get("total_completions", 0) for s in scenarios)
    col_s1, col_s2, col_s3 = st.columns(3)
    _stat_mini(col_s1, "Total Scenarios", str(len(scenarios)), "#13a4ec")
    _stat_mini(col_s2, "Active", str(active_count), "#10b981")
    _stat_mini(col_s3, "Total Completions", str(total_completions), "#f59e0b")

    st.markdown("")

    # Table header
    st.markdown(
        """<div style="display: grid; grid-template-columns: 3fr 1.5fr 1fr 1fr 1fr 1.2fr;
                      padding: 0.6rem 1rem; background: #15242b; border-radius: 8px 8px 0 0;
                      border: 1px solid #1e3340; font-size: 0.75rem; color: #64748b;
                      text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">
            <div>Scenario</div><div>Category</div><div>Difficulty</div>
            <div>Completions</div><div>Avg Score</div><div>Status</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Scenario rows
    for s in scenarios:
        cat_label = CATEGORY_LABELS.get(s.get("category", ""), s.get("category", ""))
        cat_color = CATEGORY_COLORS.get(s.get("category", ""), "#64748b")
        diff = s.get("difficulty", 1)
        stars = "".join("★" if i < diff else "☆" for i in range(5))
        completions = s.get("total_completions", 0)
        avg = s.get("avg_score")
        avg_label = f"{avg:.0f}%" if avg else "—"
        avg_color = score_color(avg) if avg else "#64748b"
        is_active = s.get("is_active", False)
        status_bg = "#10b98120" if is_active else "#ef444420"
        status_color = "#10b981" if is_active else "#ef4444"
        status_label = "Active" if is_active else "Inactive"

        st.markdown(
            f"""<div style="display: grid; grid-template-columns: 3fr 1.5fr 1fr 1fr 1fr 1.2fr;
                          padding: 0.75rem 1rem; border: 1px solid #1e3340; border-top: none;
                          font-size: 0.85rem; align-items: center;">
                <div>
                    <div style="font-weight: 600;">{s['name']}</div>
                    <div style="color: #64748b; font-size: 0.75rem; margin-top: 2px;
                               display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden;">
                        {s.get('description', '')[:80]}</div>
                </div>
                <div><span style="background: {cat_color}20; color: {cat_color}; padding: 2px 10px;
                                 border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{cat_label}</span></div>
                <div style="color: #f59e0b; letter-spacing: -1px;">{stars}</div>
                <div style="color: #94a3b8;">{completions}</div>
                <div style="color: {avg_color}; font-weight: 600;">{avg_label}</div>
                <div><span style="background: {status_bg}; color: {status_color}; padding: 2px 10px;
                                 border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{status_label}</span></div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Action buttons row per scenario
    st.markdown("#### Actions")
    cols_per_row = 4
    for i in range(0, len(scenarios), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx >= len(scenarios):
                break
            s = scenarios[idx]
            with cols[j]:
                st.markdown(
                    f'<div style="font-size: 0.8rem; font-weight: 600; margin-bottom: 4px; '
                    f'white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{s["name"]}</div>',
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Edit", key=f"edit_{s['id']}", use_container_width=True):
                        st.session_state["edit_scenario_id"] = s["id"]
                        st.session_state["page"] = "scenario_editor"
                        st.rerun()
                with c2:
                    toggle_label = "Deactivate" if s.get("is_active") else "Activate"
                    if st.button(toggle_label, key=f"toggle_{s['id']}", use_container_width=True):
                        toggle_scenario_active(s["id"])
                        st.rerun()


def _stat_mini(col, label: str, value: str, color: str):
    """Mini stat card."""
    with col:
        st.markdown(
            f"""<div class="cc-card" style="text-align: center; padding: 0.75rem;">
                <div style="font-size: 1.5rem; font-weight: 800; color: {color};">{value}</div>
                <div style="color: #64748b; font-size: 0.75rem;">{label}</div>
            </div>""",
            unsafe_allow_html=True,
        )
