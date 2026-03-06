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


def get_all_scenarios_with_stats() -> list[dict]:
    """Get all scenarios (active + inactive) with completion stats."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.*,
               COUNT(DISTINCT ses.id) as total_completions,
               ROUND(AVG(e.overall_score), 1) as avg_score
        FROM scenarios s
        LEFT JOIN sessions ses ON ses.scenario_id = s.id AND ses.status = 'completed'
        LEFT JOIN evaluations e ON e.session_id = ses.id
        GROUP BY s.id
        ORDER BY s.created_at DESC
    """).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def toggle_scenario_active(scenario_id: int) -> bool:
    """Toggle a scenario's active status. Returns new status."""
    conn = get_connection()
    row = conn.execute("SELECT is_active FROM scenarios WHERE id = ?", (scenario_id,)).fetchone()
    if not row:
        conn.close()
        return False
    new_status = 0 if row["is_active"] else 1
    conn.execute("UPDATE scenarios SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                 (new_status, scenario_id))
    conn.commit()
    conn.close()
    return bool(new_status)


def create_scenario(data: dict, created_by: int) -> int:
    """Create a new scenario. Returns the new scenario ID."""
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO scenarios (
            name, description, category, difficulty, language,
            estimated_duration_min, max_duration_min,
            persona_name, persona_background, persona_mood,
            persona_patience, persona_comm_style, persona_hidden_need,
            primary_goal, success_definition, fail_conditions,
            elevenlabs_agent_id, voice_id, system_prompt, first_message,
            temperature, is_active, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name", ""), data.get("description", ""),
        data.get("category", "SALES"), data.get("difficulty", 3),
        data.get("language", "cs"),
        data.get("estimated_duration_min", 10), data.get("max_duration_min", 15),
        data.get("persona_name", ""), data.get("persona_background", ""),
        data.get("persona_mood", "CALM"), data.get("persona_patience", 5),
        data.get("persona_comm_style", ""), data.get("persona_hidden_need", ""),
        data.get("primary_goal", ""), data.get("success_definition", ""),
        data.get("fail_conditions", ""),
        data.get("elevenlabs_agent_id", ""), data.get("voice_id", ""),
        data.get("system_prompt", ""), data.get("first_message", ""),
        data.get("temperature", 0.7), 1, created_by,
    ))
    scenario_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scenario_id


def update_scenario(scenario_id: int, data: dict):
    """Update an existing scenario."""
    conn = get_connection()
    conn.execute("""
        UPDATE scenarios SET
            name = ?, description = ?, category = ?, difficulty = ?, language = ?,
            estimated_duration_min = ?, max_duration_min = ?,
            persona_name = ?, persona_background = ?, persona_mood = ?,
            persona_patience = ?, persona_comm_style = ?, persona_hidden_need = ?,
            primary_goal = ?, success_definition = ?, fail_conditions = ?,
            elevenlabs_agent_id = ?, voice_id = ?, system_prompt = ?, first_message = ?,
            temperature = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        data.get("name", ""), data.get("description", ""),
        data.get("category", "SALES"), data.get("difficulty", 3),
        data.get("language", "cs"),
        data.get("estimated_duration_min", 10), data.get("max_duration_min", 15),
        data.get("persona_name", ""), data.get("persona_background", ""),
        data.get("persona_mood", "CALM"), data.get("persona_patience", 5),
        data.get("persona_comm_style", ""), data.get("persona_hidden_need", ""),
        data.get("primary_goal", ""), data.get("success_definition", ""),
        data.get("fail_conditions", ""),
        data.get("elevenlabs_agent_id", ""), data.get("voice_id", ""),
        data.get("system_prompt", ""), data.get("first_message", ""),
        data.get("temperature", 0.7),
        scenario_id,
    ))
    conn.commit()
    conn.close()


def save_checkpoints(scenario_id: int, checkpoints: list[dict]):
    """Replace all checkpoints for a scenario."""
    conn = get_connection()
    conn.execute("DELETE FROM checkpoints WHERE scenario_id = ?", (scenario_id,))
    for i, cp in enumerate(checkpoints):
        conn.execute("""
            INSERT INTO checkpoints (scenario_id, name, description, order_index, is_order_strict, detection_hint)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            scenario_id, cp.get("name", ""), cp.get("description", ""),
            i + 1, cp.get("is_order_strict", False), cp.get("detection_hint", ""),
        ))
    conn.commit()
    conn.close()


def delete_scenario(scenario_id: int):
    """Delete a scenario and its checkpoints."""
    conn = get_connection()
    conn.execute("DELETE FROM checkpoints WHERE scenario_id = ?", (scenario_id,))
    conn.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))
    conn.commit()
    conn.close()
