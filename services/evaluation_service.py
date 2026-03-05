"""Evaluation logic — orchestrates Gemini evaluation and scoring."""

import json
from datetime import datetime
from database.db import get_connection
from services.gemini_service import evaluate_transcript
from services.gamification_service import calculate_xp_for_session, award_xp, check_achievements
from services.scenario_service import get_scenario_by_id, get_checkpoints_for_scenario
from utils.helpers import dict_from_row
from config import DEFAULT_WEIGHT_GENERAL, DEFAULT_WEIGHT_CHECKPOINTS, DEFAULT_WEIGHT_GOAL


def create_session(user_id: int, scenario_id: int) -> int:
    """Create a new training session. Returns session ID."""
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO sessions (user_id, scenario_id, started_at, status)
           VALUES (?, ?, ?, 'in_progress')""",
        (user_id, scenario_id, datetime.now().isoformat()),
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def complete_session(session_id: int, transcript: str, duration_seconds: int,
                     conversation_id: str = None, audio_url: str = None):
    """Mark session as completed and store transcript."""
    conn = get_connection()
    conn.execute(
        """UPDATE sessions SET
           ended_at = ?, duration_seconds = ?, transcript = ?,
           elevenlabs_conversation_id = ?, audio_url = ?, status = 'completed'
           WHERE id = ?""",
        (datetime.now().isoformat(), duration_seconds, transcript,
         conversation_id, audio_url, session_id),
    )
    conn.commit()
    conn.close()


def evaluate_session(session_id: int) -> dict:
    """Run full evaluation pipeline on a completed session.

    Returns dict with evaluation results, xp_entries, new_achievements.
    """
    conn = get_connection()
    session = dict_from_row(conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone())
    conn.close()

    scenario = get_scenario_by_id(session["scenario_id"])
    checkpoints = get_checkpoints_for_scenario(session["scenario_id"])

    # Call Gemini for evaluation
    eval_result = evaluate_transcript(scenario, checkpoints, session["transcript"])

    # Calculate overall score
    overall_score = compute_overall_score(eval_result, checkpoints, scenario)

    # Save evaluation to DB
    eval_id = save_evaluation(session_id, eval_result, overall_score)

    # Calculate and award XP
    xp_entries = calculate_xp_for_session(session["user_id"], session_id, overall_score)
    total_xp, new_xp, new_level = award_xp(session["user_id"], session_id, xp_entries)

    # Check achievements
    new_achievements = check_achievements(session["user_id"], session_id)

    return {
        "eval_result": eval_result,
        "overall_score": overall_score,
        "xp_entries": xp_entries,
        "total_xp_earned": total_xp,
        "new_xp": new_xp,
        "new_level": new_level,
        "new_achievements": new_achievements,
    }


def compute_overall_score(eval_result: dict, checkpoints: list[dict], scenario: dict) -> float:
    """Compute overall score from evaluation results."""
    # Parse weights from scenario or use defaults
    weights = None
    if scenario.get("evaluation_weights"):
        try:
            weights = json.loads(scenario["evaluation_weights"])
        except (json.JSONDecodeError, TypeError):
            pass

    w_general = weights.get("general", DEFAULT_WEIGHT_GENERAL) if weights else DEFAULT_WEIGHT_GENERAL
    w_checkpoints = weights.get("checkpoints", DEFAULT_WEIGHT_CHECKPOINTS) if weights else DEFAULT_WEIGHT_CHECKPOINTS
    w_goal = weights.get("goal", DEFAULT_WEIGHT_GOAL) if weights else DEFAULT_WEIGHT_GOAL

    # General quality average (1-10 scale -> 0-100)
    general_scores = []
    for key in ["communication_clarity", "empathy_rapport", "active_listening",
                "professional_language", "call_structure", "call_control", "objection_handling"]:
        if key in eval_result and isinstance(eval_result[key], dict):
            general_scores.append(eval_result[key].get("score", 5))
        elif key in eval_result and isinstance(eval_result[key], (int, float)):
            general_scores.append(eval_result[key])

    general_avg = (sum(general_scores) / len(general_scores) * 10) if general_scores else 50

    # Checkpoint completion percentage
    cp_results = eval_result.get("checkpoints", [])
    if cp_results:
        passed = sum(1 for cp in cp_results if cp.get("passed", False))
        cp_pct = (passed / len(cp_results)) * 100
    else:
        cp_pct = 0

    # Goal achievement score
    goal_map = {"ACHIEVED": 100, "PARTIAL": 50, "FAILED": 0}
    goal_score = goal_map.get(eval_result.get("goal_achieved", "FAILED"), 0)

    # Bonus/penalty
    bonus = eval_result.get("bonus_points", 0)
    penalty = eval_result.get("penalty_points", 0)

    overall = (
        general_avg * w_general +
        cp_pct * w_checkpoints +
        goal_score * w_goal +
        bonus - penalty
    )

    return max(0, min(100, overall))


def save_evaluation(session_id: int, eval_result: dict, overall_score: float) -> int:
    """Save evaluation results to database."""
    conn = get_connection()

    def get_score(key):
        val = eval_result.get(key)
        if isinstance(val, dict):
            return val.get("score")
        return val

    cursor = conn.execute(
        """INSERT INTO evaluations (
            session_id, overall_score,
            communication_clarity, empathy_rapport, active_listening,
            professional_language, call_structure, call_control, objection_handling,
            checkpoint_results, checkpoint_order_ok,
            goal_achieved, hidden_need_found,
            bonus_points, penalty_points,
            summary, strengths, improvements, coaching_tip,
            raw_llm_response
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            session_id, overall_score,
            get_score("communication_clarity"),
            get_score("empathy_rapport"),
            get_score("active_listening"),
            get_score("professional_language"),
            get_score("call_structure"),
            get_score("call_control"),
            get_score("objection_handling"),
            json.dumps(eval_result.get("checkpoints", []), ensure_ascii=False),
            eval_result.get("checkpoint_order_correct", False),
            eval_result.get("goal_achieved", "FAILED"),
            eval_result.get("hidden_need_found", False),
            eval_result.get("bonus_points", 0),
            eval_result.get("penalty_points", 0),
            eval_result.get("summary", ""),
            json.dumps(eval_result.get("strengths", []), ensure_ascii=False),
            json.dumps(eval_result.get("improvements", []), ensure_ascii=False),
            eval_result.get("coaching_tip", ""),
            json.dumps(eval_result, ensure_ascii=False),
        ),
    )
    eval_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return eval_id


def get_evaluation_for_session(session_id: int) -> dict | None:
    """Get evaluation results for a session."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM evaluations WHERE session_id = ?", (session_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    result = dict_from_row(row)
    # Parse JSON fields
    for field in ["checkpoint_results", "strengths", "improvements"]:
        if result.get(field):
            try:
                result[field] = json.loads(result[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def get_user_sessions(user_id: int, limit: int = 50) -> list[dict]:
    """Get user's completed sessions with scenario info and scores."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT s.*, sc.name as scenario_name, sc.category, sc.difficulty,
                  e.overall_score
           FROM sessions s
           JOIN scenarios sc ON sc.id = s.scenario_id
           LEFT JOIN evaluations e ON e.session_id = s.id
           WHERE s.user_id = ? AND s.status = 'completed'
           ORDER BY s.started_at DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_stats(user_id: int) -> dict:
    """Get aggregated stats for a user."""
    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) as c FROM sessions WHERE user_id = ? AND status = 'completed'",
        (user_id,),
    ).fetchone()["c"]

    avg_score = conn.execute(
        """SELECT COALESCE(AVG(e.overall_score), 0) as avg
           FROM sessions s JOIN evaluations e ON e.session_id = s.id
           WHERE s.user_id = ? AND s.status = 'completed'""",
        (user_id,),
    ).fetchone()["avg"]

    user = dict_from_row(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())

    conn.close()
    return {
        "total_sessions": total,
        "avg_score": avg_score,
        "streak_days": user["streak_days"],
        "xp": user["xp"],
        "level": user["level"],
    }
