"""P2: Agent Home — dashboard with XP, level, achievements, recent sessions."""

import streamlit as st
from services.evaluation_service import get_user_stats, get_user_sessions
from services.gamification_service import get_user_achievements
from utils.helpers import get_level_for_xp, get_xp_for_next_level, format_duration, score_color
from config import CATEGORY_LABELS


def render():
    """Render the Agent Home page."""
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    if not user_id:
        st.session_state["page"] = "login"
        st.rerun()
        return

    # Refresh user stats
    stats = get_user_stats(user_id)
    level, level_name = get_level_for_xp(stats["xp"])
    current_threshold, next_threshold = get_xp_for_next_level(stats["xp"])
    xp_in_level = stats["xp"] - current_threshold
    xp_needed = max(next_threshold - current_threshold, 1)
    xp_pct = min(100, int(xp_in_level / xp_needed * 100))

    # ── Main layout: content + sidebar ──
    col_main, col_right = st.columns([3, 1])

    with col_main:
        # Welcome + level badge
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div>
                    <h2 style="margin: 0; font-weight: 800;">Welcome back, {user.get('name', 'Agent').split()[0]}</h2>
                    <p style="color: #94a3b8; margin: 0;">Your training hub at a glance.</p>
                </div>
                <div style="text-align: right;">
                    <span style="background: #13a4ec20; color: #13a4ec; padding: 4px 14px; border-radius: 20px;
                                font-size: 0.8rem; font-weight: 700;">Level {level} · {level_name}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # XP progress bar
        st.markdown(
            f"""
            <div class="cc-card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 600; font-size: 0.9rem;">{stats['xp']} XP</span>
                    <span style="color: #94a3b8; font-size: 0.8rem;">{xp_in_level}/{xp_needed} to Level {level + 1}</span>
                </div>
                <div style="height: 8px; background: #1e3340; border-radius: 4px; overflow: hidden;">
                    <div style="height: 100%; width: {xp_pct}%; background: linear-gradient(90deg, #13a4ec, #6366f1);
                               border-radius: 4px; transition: width 0.5s;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Stats cards row
        col1, col2, col3, col4 = st.columns(4)
        _stat_card(col1, "headset_mic", str(stats["total_sessions"]), "Calls Completed", "#13a4ec")
        _stat_card(col2, "trending_up", f"{stats['avg_score']:.0f}%", "Avg Score", "#10b981")
        _stat_card(col3, "local_fire_department", f"{stats['streak_days']}", "Day Streak", "#f59e0b")
        _stat_card(col4, "emoji_events", str(len([a for a in get_user_achievements(user_id) if a.get("earned_at")])), "Badges", "#a855f7")

        st.markdown("")

        # CTA button
        if st.button("Start New Training Session", use_container_width=True, type="primary"):
            st.session_state["page"] = "scenario_browser"
            st.rerun()

        st.markdown("")

        # Achievements row
        st.markdown("#### Recent Achievements")
        achievements = get_user_achievements(user_id)
        earned = [a for a in achievements if a.get("earned_at")]
        if earned:
            ach_cols = st.columns(min(len(earned), 4) + 1)
            for i, ach in enumerate(earned[:4]):
                with ach_cols[i]:
                    _badge_card(ach)
            with ach_cols[min(len(earned), 4)]:
                st.markdown(
                    """<div style="border: 1px dashed #334155; border-radius: 12px; padding: 1rem;
                                  text-align: center; display: flex; flex-direction: column; align-items: center;
                                  justify-content: center; min-height: 130px; cursor: pointer; color: #64748b;">
                        <span class="mi">lock</span><br><span style="font-size: 0.75rem;">View All</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
                if st.button("All Badges", key="view_all_badges", use_container_width=True):
                    st.session_state["page"] = "achievements"
                    st.rerun()
        else:
            st.caption("No badges yet. Complete your first training call!")

        st.markdown("")

        # Recent Sessions table
        st.markdown("#### Recent Sessions")
        sessions = get_user_sessions(user_id, limit=5)

        if sessions:
            # Table header
            st.markdown(
                """<div style="display: grid; grid-template-columns: 3fr 2fr 1fr 1fr;
                              padding: 0.5rem 1rem; background: #15242b; border-radius: 8px 8px 0 0;
                              border: 1px solid #1e3340; font-size: 0.75rem; color: #64748b;
                              text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">
                    <div>Scenario Name</div><div>Date</div><div>Score</div><div>Duration</div>
                </div>""",
                unsafe_allow_html=True,
            )
            for s in sessions:
                score = s.get("overall_score")
                s_color = score_color(score) if score else "#64748b"
                s_label = f"{score:.0f}%" if score else "—"
                cat_label = CATEGORY_LABELS.get(s.get("category", ""), "")
                date_str = s.get("started_at", "")[:10] if s.get("started_at") else "—"
                dur = format_duration(s.get("duration_seconds"))

                badge_bg = "#10b98120" if score and score >= 85 else ("#f59e0b20" if score and score >= 70 else "#ef444420")
                badge_col = "#10b981" if score and score >= 85 else ("#f59e0b" if score and score >= 70 else "#ef4444")

                st.markdown(
                    f"""<div style="display: grid; grid-template-columns: 3fr 2fr 1fr 1fr;
                                  padding: 0.7rem 1rem; border: 1px solid #1e3340; border-top: none;
                                  font-size: 0.85rem; cursor: pointer;"
                         class="session-row">
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

            # Detail buttons (Streamlit can't do onclick on custom HTML)
            detail_cols = st.columns(len(sessions))
            for i, s in enumerate(sessions):
                with detail_cols[i]:
                    if st.button("View", key=f"session_{s['id']}"):
                        st.session_state["view_session_id"] = s["id"]
                        st.session_state["page"] = "scorecard"
                        st.rerun()
        else:
            st.info("No sessions yet. Start your first training call!")

    # ── Right column ──
    with col_right:
        # Active Milestones
        st.markdown(
            """
            <div class="cc-card" style="margin-bottom: 1rem;">
                <h4 style="margin: 0 0 1rem 0; display: flex; align-items: center; gap: 6px;">
                    <span class="mi" style="color: #13a4ec;">flag</span> Active Milestones
                </h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _milestone_bar("Complete 5 Scenarios", stats["total_sessions"], 5, "#13a4ec")
        _milestone_bar(f"Reach Level {level + 3}", level, level + 3, "#a855f7")
        _milestone_bar("Maintain 90% Avg", int(stats["avg_score"]), 90, "#f59e0b")

        st.markdown("")

        # Pro Tip
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #13a4ec10, transparent);
                       border: 1px solid #13a4ec30; border-radius: 12px; padding: 1rem; position: relative; overflow: hidden;">
                <div style="display: flex; align-items: center; gap: 6px; color: #13a4ec; font-weight: 700; margin-bottom: 0.5rem;">
                    <span class="mi">tips_and_updates</span> Pro Tip
                </div>
                <p style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                    Try pausing for 2 seconds after stating the price to let the customer process the information. 
                    This reduces objections by up to 20%.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _stat_card(col, icon: str, value: str, label: str, color: str):
    """Render a stat card matching UX design."""
    with col:
        st.markdown(
            f"""
            <div class="cc-card" style="text-align: center; min-height: 100px;">
                <span class="mi" style="color: {color}; font-size: 24px;">{icon}</span>
                <div style="font-size: 1.5rem; font-weight: 800; margin: 0.25rem 0;">{value}</div>
                <div style="color: #64748b; font-size: 0.75rem;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _badge_card(ach: dict):
    """Render a single achievement badge card."""
    icon = ach.get("icon", "star")
    st.markdown(
        f"""
        <div style="background: #15242b; border: 1px solid #1e3340; border-radius: 12px;
                   padding: 1rem; text-align: center; min-height: 130px;">
            <div style="width: 48px; height: 48px; border-radius: 50%; margin: 0 auto 0.5rem auto;
                       background: linear-gradient(135deg, #13a4ec, #6366f1);
                       display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1.5rem;">{icon}</span>
            </div>
            <div style="font-weight: 700; font-size: 0.8rem;">{ach.get('name', '')}</div>
            <div style="color: #64748b; font-size: 0.7rem; margin-top: 2px;">{ach.get('description', '')[:30]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _milestone_bar(label: str, current: int, target: int, color: str):
    """Render a milestone progress bar."""
    pct = min(100, int(current / target * 100)) if target > 0 else 0
    st.markdown(
        f"""
        <div style="margin-bottom: 0.75rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                <span>{label}</span>
                <span style="color: #64748b;">{current}/{target}</span>
            </div>
            <div style="height: 6px; background: #1e3340; border-radius: 3px; overflow: hidden;">
                <div style="height: 100%; width: {pct}%; background: {color}; border-radius: 3px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
