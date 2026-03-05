"""P9: Agent Detail (Manager view) — individual agent profile, scores, history."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.db import get_connection
from services.evaluation_service import get_user_stats, get_user_sessions
from services.gamification_service import get_user_achievements
from components.radar_chart import render_radar_chart
from utils.helpers import dict_from_row, rows_to_dicts, get_level_for_xp, get_xp_for_next_level
from utils.helpers import format_duration, score_color
from config import CATEGORY_LABELS


def render():
    """Render the Agent Detail page."""
    agent_id = st.session_state.get("view_agent_id")

    if not agent_id:
        st.session_state["page"] = "manager_dashboard"
        st.rerun()
        return

    conn = get_connection()
    agent = dict_from_row(conn.execute("SELECT * FROM users WHERE id = ?", (agent_id,)).fetchone())
    conn.close()

    if not agent:
        st.error("Agent not found.")
        return

    stats = get_user_stats(agent_id)
    level, level_name = get_level_for_xp(stats["xp"])
    current_threshold, next_threshold = get_xp_for_next_level(stats["xp"])
    xp_in_level = stats["xp"] - current_threshold
    xp_needed = max(next_threshold - current_threshold, 1)
    xp_pct = min(100, int(xp_in_level / xp_needed * 100))

    initials = "".join(w[0] for w in agent["name"].split()[:2]).upper()

    # ── Profile header ──
    st.markdown(
        f"""
        <div class="cc-card" style="display: flex; align-items: center; gap: 20px; margin-bottom: 1.5rem;">
            <div style="width: 72px; height: 72px; border-radius: 50%; background: #1e3340;
                       display: flex; align-items: center; justify-content: center;
                       font-weight: 800; font-size: 1.5rem; color: #13a4ec; border: 2px solid #13a4ec30;
                       flex-shrink: 0;">{initials}</div>
            <div style="flex: 1;">
                <h2 style="margin: 0; font-weight: 800;">{agent['name']}</h2>
                <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                    Level {level} · {level_name} · {agent.get('team', '')} Team
                </div>
                <div style="display: flex; align-items: center; gap: 10px; margin-top: 0.5rem;">
                    <span style="font-weight: 600; font-size: 0.8rem;">{stats['xp']} XP</span>
                    <div style="flex: 1; height: 6px; background: #1e3340; border-radius: 3px; max-width: 200px;">
                        <div style="height: 100%; width: {xp_pct}%; background: linear-gradient(90deg, #13a4ec, #6366f1); border-radius: 3px;"></div>
                    </div>
                    <span style="color: #64748b; font-size: 0.75rem;">{xp_in_level}/{xp_needed}</span>
                </div>
            </div>
            <div style="text-align: right;">
                <span style="background: #13a4ec20; color: #13a4ec; padding: 4px 14px; border-radius: 20px;
                            font-size: 0.8rem; font-weight: 700;">Level {level}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Stat cards ──
    col1, col2, col3, col4 = st.columns(4)
    _stat_card(col1, "headset_mic", str(stats["total_sessions"]), "Sessions", "#13a4ec")
    _stat_card(col2, "trending_up", f"{stats['avg_score']:.0f}%", "Avg Score", "#10b981")
    _stat_card(col3, "local_fire_department", str(stats["streak_days"]), "Day Streak", "#f59e0b")
    earned = [a for a in get_user_achievements(agent_id) if a.get("earned_at")]
    _stat_card(col4, "emoji_events", str(len(earned)), "Badges", "#a855f7")

    st.markdown("")

    # ── Charts: Trend + Radar ──
    col_chart, col_radar = st.columns(2)

    with col_chart:
        st.markdown("#### Score Progress")
        conn = get_connection()
        trend = rows_to_dicts(conn.execute("""
            SELECT DATE(s.started_at) as day, AVG(e.overall_score) as avg_score
            FROM sessions s
            JOIN evaluations e ON e.session_id = s.id
            WHERE s.user_id = ? AND s.status = 'completed'
            GROUP BY DATE(s.started_at)
            ORDER BY day
        """, (agent_id,)).fetchall())
        conn.close()

        if trend:
            df = pd.DataFrame(trend)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["day"], y=df["avg_score"],
                mode="lines+markers",
                line=dict(color="#13a4ec", width=2),
                marker=dict(size=6, color="#13a4ec"),
                fill="tozeroy",
                fillcolor="rgba(19,164,236,0.1)",
            ))
            fig.update_layout(
                yaxis=dict(range=[0, 100], title="Score %", gridcolor="#1e3340"),
                xaxis=dict(gridcolor="#1e3340"),
                height=300,
                margin=dict(l=40, r=20, t=10, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet.")

    with col_radar:
        st.markdown("#### Skill Profile")
        conn = get_connection()
        avg_skills = dict_from_row(conn.execute("""
            SELECT
                AVG(e.communication_clarity) as communication_clarity,
                AVG(e.empathy_rapport) as empathy_rapport,
                AVG(e.active_listening) as active_listening,
                AVG(e.professional_language) as professional_language,
                AVG(e.call_structure) as call_structure,
                AVG(e.call_control) as call_control,
                AVG(e.objection_handling) as objection_handling
            FROM evaluations e
            JOIN sessions s ON s.id = e.session_id
            WHERE s.user_id = ? AND s.status = 'completed'
        """, (agent_id,)).fetchone())
        conn.close()

        if avg_skills and any(v for v in avg_skills.values() if v is not None):
            render_radar_chart(avg_skills, title="")
        else:
            st.info("No data yet.")

    st.markdown("")

    # ── Session History ──
    st.markdown("#### Session History")
    sessions = get_user_sessions(agent_id, limit=20)

    if sessions:
        st.markdown(
            """<div style="display: grid; grid-template-columns: 3fr 2fr 1fr 1fr;
                          padding: 0.5rem 1rem; background: #15242b; border-radius: 8px 8px 0 0;
                          border: 1px solid #1e3340; font-size: 0.75rem; color: #64748b;
                          text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">
                <div>Scenario</div><div>Date</div><div>Score</div><div>Duration</div>
            </div>""",
            unsafe_allow_html=True,
        )
        for s in sessions:
            score = s.get("overall_score")
            s_label = f"{score:.0f}%" if score else "—"
            badge_bg = "#10b98120" if score and score >= 85 else ("#f59e0b20" if score and score >= 70 else "#ef444420")
            badge_col = "#10b981" if score and score >= 85 else ("#f59e0b" if score and score >= 70 else "#ef4444")
            cat_label = CATEGORY_LABELS.get(s.get("category", ""), "")
            date_str = s.get("started_at", "")[:10] if s.get("started_at") else "—"
            dur = format_duration(s.get("duration_seconds"))

            st.markdown(
                f"""<div style="display: grid; grid-template-columns: 3fr 2fr 1fr 1fr;
                              padding: 0.7rem 1rem; border: 1px solid #1e3340; border-top: none; font-size: 0.85rem;">
                    <div>
                        <div style="font-weight: 600;">{s.get('scenario_name', '—')}</div>
                        <div style="color: #64748b; font-size: 0.75rem;">{cat_label}</div>
                    </div>
                    <div style="color: #94a3b8;">{date_str}</div>
                    <div><span style="background: {badge_bg}; color: {badge_col}; padding: 2px 10px;
                                     border-radius: 12px; font-size: 0.8rem; font-weight: 600;">{s_label}</span></div>
                    <div style="color: #94a3b8;">{dur}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        # View buttons
        detail_cols = st.columns(min(len(sessions), 5))
        for i, s in enumerate(sessions[:5]):
            with detail_cols[i]:
                if st.button("View", key=f"mgr_session_{s['id']}"):
                    st.session_state["view_session_id"] = s["id"]
                    st.session_state["page"] = "scorecard"
                    st.rerun()
    else:
        st.info("No sessions yet for this agent.")

    st.markdown("")

    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state["page"] = "manager_dashboard"
        st.rerun()


def _stat_card(col, icon: str, value: str, label: str, color: str):
    """Render a stat card."""
    with col:
        st.markdown(
            f"""<div class="cc-card" style="text-align: center;">
                <span class="mi" style="color: {color}; font-size: 24px;">{icon}</span>
                <div style="font-size: 1.5rem; font-weight: 800; margin: 0.25rem 0;">{value}</div>
                <div style="color: #64748b; font-size: 0.75rem;">{label}</div>
            </div>""",
            unsafe_allow_html=True,
        )
