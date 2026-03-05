"""Gamification: XP, levels, achievements, streaks."""

import json
from datetime import datetime, date, timedelta
from database.db import get_connection
from utils.helpers import get_level_for_xp, rows_to_dicts, dict_from_row
from config import (
    XP_BASE_CALL, XP_PER_POINT_ABOVE_70, XP_PERFECT_BONUS,
    XP_FIRST_SCENARIO, XP_DAILY_STREAK,
)


def calculate_xp_for_session(user_id: int, session_id: int, overall_score: float) -> list[dict]:
    """Calculate XP earned for a completed session. Returns list of {xp, reason}."""
    conn = get_connection()
    session = dict_from_row(conn.execute(
        "SELECT * FROM sessions WHERE id = ?", (session_id,)
    ).fetchone())

    xp_entries = []

    # Base XP for completing a call
    xp_entries.append({"xp": XP_BASE_CALL, "reason": "Dokončený hovor"})

    # Bonus for score above 70
    if overall_score > 70:
        bonus = int((overall_score - 70) * XP_PER_POINT_ABOVE_70)
        if bonus > 0:
            xp_entries.append({"xp": bonus, "reason": f"Bonus za skóre {overall_score:.0f}%"})

    # Perfect score bonus
    if overall_score >= 100:
        xp_entries.append({"xp": XP_PERFECT_BONUS, "reason": "Perfektné skóre!"})

    # First completion of this scenario
    prev = conn.execute(
        """SELECT COUNT(*) as cnt FROM sessions
           WHERE user_id = ? AND scenario_id = ? AND status = 'completed' AND id != ?""",
        (user_id, session["scenario_id"], session_id),
    ).fetchone()
    if prev["cnt"] == 0:
        xp_entries.append({"xp": XP_FIRST_SCENARIO, "reason": "Prvé dokončenie scenára"})

    # Daily streak bonus
    user = dict_from_row(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())
    if user["last_active"]:
        last_active_date = datetime.fromisoformat(user["last_active"]).date() if isinstance(user["last_active"], str) else user["last_active"].date()
        today = date.today()
        if last_active_date == today - timedelta(days=1):
            xp_entries.append({"xp": XP_DAILY_STREAK, "reason": "Daily streak bonus"})

    conn.close()
    return xp_entries


def award_xp(user_id: int, session_id: int, xp_entries: list[dict]):
    """Award XP to user and log it."""
    conn = get_connection()
    total_xp = sum(e["xp"] for e in xp_entries)

    for entry in xp_entries:
        conn.execute(
            "INSERT INTO xp_log (user_id, session_id, xp_earned, reason) VALUES (?, ?, ?, ?)",
            (user_id, session_id, entry["xp"], entry["reason"]),
        )

    # Update user XP and level
    user = dict_from_row(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())
    new_xp = user["xp"] + total_xp
    new_level, _ = get_level_for_xp(new_xp)

    # Update streak
    today = date.today()
    new_streak = user["streak_days"]
    if user["last_active"]:
        last_active_date = datetime.fromisoformat(user["last_active"]).date() if isinstance(user["last_active"], str) else user["last_active"].date()
        if last_active_date == today - timedelta(days=1):
            new_streak += 1
        elif last_active_date != today:
            new_streak = 1
    else:
        new_streak = 1

    conn.execute(
        "UPDATE users SET xp = ?, level = ?, streak_days = ?, last_active = ? WHERE id = ?",
        (new_xp, new_level, new_streak, datetime.now().isoformat(), user_id),
    )

    conn.commit()
    conn.close()
    return total_xp, new_xp, new_level


def check_achievements(user_id: int, session_id: int) -> list[dict]:
    """Check and award any new achievements after a session. Returns newly earned achievements."""
    conn = get_connection()
    new_achievements = []

    all_achievements = rows_to_dicts(conn.execute("SELECT * FROM achievements").fetchall())
    earned_ids = [
        r["achievement_id"]
        for r in conn.execute(
            "SELECT achievement_id FROM user_achievements WHERE user_id = ?", (user_id,)
        ).fetchall()
    ]

    for ach in all_achievements:
        if ach["id"] in earned_ids:
            continue

        earned = False
        ctype = ach["condition_type"]
        cval = ach["condition_value"]

        if ctype == "first_call":
            cnt = conn.execute(
                "SELECT COUNT(*) as c FROM sessions WHERE user_id = ? AND status = 'completed'",
                (user_id,),
            ).fetchone()["c"]
            earned = cnt >= 1

        elif ctype == "perfect_score":
            row = conn.execute(
                """SELECT MAX(e.overall_score) as ms FROM sessions s
                   JOIN evaluations e ON e.session_id = s.id
                   WHERE s.user_id = ? AND s.status = 'completed'""",
                (user_id,),
            ).fetchone()
            earned = row["ms"] is not None and row["ms"] >= float(cval)

        elif ctype == "streak_days":
            user = dict_from_row(conn.execute("SELECT streak_days FROM users WHERE id = ?", (user_id,)).fetchone())
            earned = user["streak_days"] >= int(cval)

        elif ctype == "avg_empathy":
            row = conn.execute(
                """SELECT AVG(e.empathy_rapport) as avg_emp, COUNT(*) as cnt
                   FROM sessions s JOIN evaluations e ON e.session_id = s.id
                   WHERE s.user_id = ? AND s.status = 'completed'""",
                (user_id,),
            ).fetchone()
            earned = row["cnt"] >= 10 and row["avg_emp"] is not None and row["avg_emp"] >= float(cval)

        elif ctype == "daily_calls":
            today = date.today().isoformat()
            cnt = conn.execute(
                "SELECT COUNT(*) as c FROM sessions WHERE user_id = ? AND status = 'completed' AND DATE(started_at) = ?",
                (user_id, today),
            ).fetchone()["c"]
            earned = cnt >= int(cval)

        if earned:
            try:
                conn.execute(
                    "INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?)",
                    (user_id, ach["id"]),
                )
                new_achievements.append(ach)
            except Exception:
                pass

    conn.commit()
    conn.close()
    return new_achievements


def get_user_achievements(user_id: int) -> list[dict]:
    """Get all achievements with earned status for a user."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT a.*, ua.earned_at
           FROM achievements a
           LEFT JOIN user_achievements ua ON ua.achievement_id = a.id AND ua.user_id = ?
           ORDER BY ua.earned_at DESC NULLS LAST, a.id""",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_leaderboard(team: str = None, period: str = "all") -> list[dict]:
    """Get leaderboard sorted by XP. Optional team and period filters."""
    conn = get_connection()
    query = """
        SELECT u.id, u.name, u.level, u.xp, u.streak_days,
               COUNT(DISTINCT s.id) as total_sessions,
               COALESCE(AVG(e.overall_score), 0) as avg_score
        FROM users u
        LEFT JOIN sessions s ON s.user_id = u.id AND s.status = 'completed'
        LEFT JOIN evaluations e ON e.session_id = s.id
        WHERE u.role = 'agent'
    """
    params = []

    if team:
        query += " AND u.team = ?"
        params.append(team)

    if period == "week":
        query += " AND (s.started_at IS NULL OR s.started_at >= date('now', '-7 days'))"
    elif period == "month":
        query += " AND (s.started_at IS NULL OR s.started_at >= date('now', '-30 days'))"

    query += " GROUP BY u.id ORDER BY u.xp DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows_to_dicts(rows)
