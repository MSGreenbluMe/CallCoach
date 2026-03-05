"""Scenario CRUD operations."""

from database.db import get_connection
from utils.helpers import dict_from_row, rows_to_dicts


def get_all_scenarios(active_only=True) -> list[dict]:
    """Get all scenarios, optionally filtered by active status."""
    conn = get_connection()
    query = "SELECT * FROM scenarios"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY category, difficulty"
    rows = conn.execute(query).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_scenario_by_id(scenario_id: int) -> dict:
    """Get a single scenario by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,)).fetchone()
    conn.close()
    return dict_from_row(row)


def get_checkpoints_for_scenario(scenario_id: int) -> list[dict]:
    """Get all checkpoints for a scenario, ordered."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM checkpoints WHERE scenario_id = ? ORDER BY order_index",
        (scenario_id,),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_scenarios_by_category(category: str) -> list[dict]:
    """Get scenarios filtered by category."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM scenarios WHERE category = ? AND is_active = 1 ORDER BY difficulty",
        (category,),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_user_best_score_for_scenario(user_id: int, scenario_id: int) -> float | None:
    """Get the best score a user achieved on a scenario."""
    conn = get_connection()
    row = conn.execute(
        """SELECT MAX(e.overall_score) as best_score
           FROM sessions s
           JOIN evaluations e ON e.session_id = s.id
           WHERE s.user_id = ? AND s.scenario_id = ? AND s.status = 'completed'""",
        (user_id, scenario_id),
    ).fetchone()
    conn.close()
    if row and row["best_score"] is not None:
        return row["best_score"]
    return None


def get_user_scenario_status(user_id: int, scenario_id: int) -> str:
    """Get user's status for a scenario: 'new', 'attempted', 'mastered'."""
    best = get_user_best_score_for_scenario(user_id, scenario_id)
    if best is None:
        return "new"
    if best >= 80:
        return "mastered"
    return "attempted"
