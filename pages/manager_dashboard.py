"""P8: Manager Dashboard — team overview, trends, leaderboard, skill gaps."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.db import get_connection
from services.gamification_service import get_leaderboard
from utils.helpers import rows_to_dicts, get_level_for_xp


def render():
    """Render the Manager Dashboard page."""
    user = st.session_state.get("user", {})

    # ── Header ──
    st.markdown(
        """<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h2 style="margin: 0; font-weight: 800;">Team Overview</h2>
                <p style="color: #94a3b8; margin: 0;">Monitor your team's training performance</p>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Period filter
    period = st.selectbox(
        "Period",
        options=["week", "month", "all"],
        format_func=lambda x: {"week": "This Week", "month": "This Month", "all": "All Time"}[x],
        index=1,
    )

    conn = get_connection()
    team = user.get("team")

    # Queries
    agents_count = conn.execute(
        "SELECT COUNT(*) as c FROM users WHERE role = 'agent'" + (" AND team = ?" if team else ""),
        (team,) if team else (),
    ).fetchone()["c"]

    period_filter = ""
    if period == "week":
        period_filter = "AND s.started_at >= date('now', '-7 days')"
    elif period == "month":
        period_filter = "AND s.started_at >= date('now', '-30 days')"

    avg_score_row = conn.execute(f"""
        SELECT COALESCE(AVG(e.overall_score), 0) as avg, COUNT(DISTINCT s.id) as sessions
        FROM sessions s
        JOIN evaluations e ON e.session_id = s.id
        JOIN users u ON u.id = s.user_id
        WHERE s.status = 'completed' AND u.role = 'agent' {period_filter}
        {"AND u.team = ?" if team else ""}
    """, (team,) if team else ()).fetchone()

    active_today = conn.execute("""
        SELECT COUNT(DISTINCT s.user_id) as c
        FROM sessions s JOIN users u ON u.id = s.user_id
        WHERE DATE(s.started_at) = DATE('now') AND u.role = 'agent'
        """ + (f"AND u.team = '{team}'" if team else "")
    ).fetchone()["c"]

    # ── Stats cards ──
    col1, col2, col3, col4 = st.columns(4)
    _stat_card(col1, "groups", str(agents_count), "Total Agents", "#13a4ec")
    _stat_card(col2, "trending_up", f"{avg_score_row['avg']:.0f}%", "Avg Score", "#10b981")
    _stat_card(col3, "headset_mic", str(avg_score_row["sessions"]), "Total Sessions", "#a855f7")
    _stat_card(col4, "person", str(active_today), "Active Today", "#f59e0b")

    st.markdown("")

    # ── Score trend chart ──
    st.markdown("#### Average Score Trend")
    trend_data = rows_to_dicts(conn.execute(f"""
        SELECT DATE(s.started_at) as day, AVG(e.overall_score) as avg_score, COUNT(*) as cnt
        FROM sessions s
        JOIN evaluations e ON e.session_id = s.id
        JOIN users u ON u.id = s.user_id
        WHERE s.status = 'completed' AND u.role = 'agent'
              AND s.started_at >= date('now', '-30 days')
              {"AND u.team = ?" if team else ""}
        GROUP BY DATE(s.started_at)
        ORDER BY day
    """, (team,) if team else ()).fetchall())

    if trend_data:
        df = pd.DataFrame(trend_data)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["day"], y=df["avg_score"],
            mode="lines+markers",
            line=dict(color="#13a4ec", width=2),
            marker=dict(size=6, color="#13a4ec"),
            fill="tozeroy",
            fillcolor="rgba(19, 164, 236, 0.1)",
        ))
        fig.update_layout(
            yaxis=dict(range=[0, 100], title="Score %", gridcolor="#1e3340"),
            xaxis=dict(title="", gridcolor="#1e3340"),
            height=280,
            margin=dict(l=40, r=20, t=10, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for selected period yet.")

    st.markdown("")

    # ── Leaderboard + Skill gap ──
    col_lb, col_sg = st.columns([1, 1])

    with col_lb:
        st.markdown("#### Top Performers")
        lb_data = get_leaderboard(team=team, period=period)
        if lb_data:
            header = """<div style="display: grid; grid-template-columns: 2fr 1fr 1fr;
                                   padding: 0.5rem 1rem; font-size: 0.7rem; color: #64748b;
                                   text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
                                   background: #15242b; border-radius: 8px 8px 0 0; border: 1px solid #1e3340;">
                <div>Agent</div><div>Level</div><div style="text-align: right;">Score</div>
            </div>"""
            st.markdown(header, unsafe_allow_html=True)

            colors = ["#818cf8", "#3b82f6", "#a855f7", "#f59e0b", "#ef4444"]
            for i, entry in enumerate(lb_data[:5]):
                initials = "".join(w[0] for w in entry.get("name", "?").split()[:2]).upper()
                _, lvl_name = get_level_for_xp(entry.get("xp", 0))
                avg = entry.get("avg_score", 0)
                c = colors[i % len(colors)]
                s_color = "#10b981" if avg >= 85 else ("#f59e0b" if avg >= 70 else "#94a3b8")
                st.markdown(
                    f"""<div style="display: grid; grid-template-columns: 2fr 1fr 1fr;
                                  padding: 0.6rem 1rem; border: 1px solid #1e3340; border-top: none;
                                  font-size: 0.85rem; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 30px; height: 30px; border-radius: 50%; background: {c}30; color: {c};
                                       display: flex; align-items: center; justify-content: center;
                                       font-size: 0.7rem; font-weight: 700;">{initials}</div>
                            <span style="font-weight: 500;">{entry.get('name', '').split()[0]}</span>
                        </div>
                        <div style="color: #64748b;">{lvl_name}</div>
                        <div style="text-align: right; font-weight: 600; color: {s_color};">{avg:.0f}%</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No leaderboard data yet.")

    with col_sg:
        st.markdown("#### Skill Gap Analysis")
        _render_skill_heatmap(conn, team)

    st.markdown("")

    # ── Agent list ──
    st.markdown("#### Agents")
    agents = rows_to_dicts(conn.execute(
        "SELECT * FROM users WHERE role = 'agent'" + (" AND team = ?" if team else "") + " ORDER BY xp DESC",
        (team,) if team else (),
    ).fetchall())

    cols = st.columns(min(len(agents), 4) if agents else 1)
    for i, agent in enumerate(agents):
        _, level_name = get_level_for_xp(agent["xp"])
        initials = "".join(w[0] for w in agent["name"].split()[:2]).upper()
        with cols[i % len(cols)]:
            st.markdown(
                f"""<div class="cc-card" style="text-align: center; margin-bottom: 0.5rem;">
                    <div style="width: 48px; height: 48px; border-radius: 50%; background: #1e3340;
                               display: flex; align-items: center; justify-content: center;
                               font-weight: 700; color: #13a4ec; margin: 0 auto 0.5rem auto;">{initials}</div>
                    <div style="font-weight: 600;">{agent['name']}</div>
                    <div style="color: #64748b; font-size: 0.8rem;">Lv.{agent['level']} {level_name} · {agent['xp']} XP</div>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button("View Profile", key=f"agent_{agent['id']}", use_container_width=True):
                st.session_state["view_agent_id"] = agent["id"]
                st.session_state["page"] = "agent_detail"
                st.rerun()

    conn.close()


def _stat_card(col, icon: str, value: str, label: str, color: str):
    """Render a manager stat card."""
    with col:
        st.markdown(
            f"""<div class="cc-card" style="text-align: center;">
                <span class="mi" style="color: {color}; font-size: 24px;">{icon}</span>
                <div style="font-size: 1.5rem; font-weight: 800; margin: 0.25rem 0;">{value}</div>
                <div style="color: #64748b; font-size: 0.75rem;">{label}</div>
            </div>""",
            unsafe_allow_html=True,
        )


def _render_skill_heatmap(conn, team: str = None):
    """Render skill gap heatmap: criteria vs agents."""
    agents = rows_to_dicts(conn.execute(
        "SELECT id, name FROM users WHERE role = 'agent'" + (" AND team = ?" if team else "") + " ORDER BY name",
        (team,) if team else (),
    ).fetchall())

    if not agents:
        st.info("No agents found.")
        return

    criteria = [
        ("communication_clarity", "Clarity"),
        ("empathy_rapport", "Empathy"),
        ("active_listening", "Listening"),
        ("call_structure", "Structure"),
        ("objection_handling", "Objections"),
    ]

    z_data = []
    y_labels = []

    for crit_key, crit_label in criteria:
        row = []
        for agent in agents:
            avg = conn.execute(f"""
                SELECT AVG(e.{crit_key}) as avg_val
                FROM evaluations e
                JOIN sessions s ON s.id = e.session_id
                WHERE s.user_id = ? AND s.status = 'completed'
            """, (agent["id"],)).fetchone()["avg_val"]
            row.append(round(avg, 1) if avg else 0)
        z_data.append(row)
        y_labels.append(crit_label)

    x_labels = [a["name"].split()[0] for a in agents]

    fig = go.Figure(data=go.Heatmap(
        z=z_data, x=x_labels, y=y_labels,
        colorscale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#10b981"]],
        zmin=0, zmax=10,
        text=[[f"{v:.1f}" for v in row] for row in z_data],
        texttemplate="%{text}",
        textfont={"size": 11, "color": "white"},
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=70, r=10, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
    )
    st.plotly_chart(fig, use_container_width=True)
