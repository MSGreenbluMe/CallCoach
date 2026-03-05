import sqlite3
import os
from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Get SQLite connection with row factory."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            email           TEXT UNIQUE,
            role            TEXT CHECK(role IN ('agent','manager','admin')) NOT NULL,
            team            TEXT,
            avatar_url      TEXT,
            xp              INTEGER DEFAULT 0,
            level           INTEGER DEFAULT 1,
            streak_days     INTEGER DEFAULT 0,
            last_active     DATETIME,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS scenarios (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            name                    TEXT NOT NULL,
            description             TEXT,
            category                TEXT CHECK(category IN ('SALES','RETENTION','TECH_SUPPORT','COMPLAINTS','BILLING','ONBOARDING')),
            difficulty              INTEGER CHECK(difficulty BETWEEN 1 AND 5),
            language                TEXT DEFAULT 'cs',
            estimated_duration_min  INTEGER,
            max_duration_min        INTEGER,
            persona_name            TEXT,
            persona_background      TEXT,
            persona_mood            TEXT,
            persona_patience        INTEGER,
            persona_comm_style      TEXT,
            persona_hidden_need     TEXT,
            primary_goal            TEXT,
            success_definition      TEXT,
            fail_conditions         TEXT,
            elevenlabs_agent_id     TEXT,
            voice_id                TEXT,
            system_prompt           TEXT,
            first_message           TEXT,
            knowledge_base_config   TEXT,
            temperature             REAL DEFAULT 0.7,
            evaluation_weights      TEXT,
            bonus_criteria          TEXT,
            penalty_criteria        TEXT,
            is_active               BOOLEAN DEFAULT 1,
            created_by              INTEGER REFERENCES users(id),
            created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at              DATETIME
        );

        CREATE TABLE IF NOT EXISTS checkpoints (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id         INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
            name                TEXT NOT NULL,
            description         TEXT,
            order_index         INTEGER NOT NULL,
            is_order_strict     BOOLEAN DEFAULT 0,
            detection_hint      TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id                          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id                     INTEGER REFERENCES users(id),
            scenario_id                 INTEGER REFERENCES scenarios(id),
            started_at                  DATETIME,
            ended_at                    DATETIME,
            duration_seconds            INTEGER,
            audio_url                   TEXT,
            transcript                  TEXT,
            elevenlabs_conversation_id  TEXT,
            status                      TEXT CHECK(status IN ('in_progress','completed','abandoned','timeout')),
            created_at                  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS evaluations (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id              INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
            overall_score           REAL,
            communication_clarity   REAL,
            empathy_rapport         REAL,
            active_listening        REAL,
            professional_language   REAL,
            call_structure          REAL,
            call_control            REAL,
            objection_handling      REAL,
            checkpoint_results      TEXT,
            checkpoint_order_ok     BOOLEAN,
            goal_achieved           TEXT CHECK(goal_achieved IN ('ACHIEVED','PARTIAL','FAILED')),
            hidden_need_found       BOOLEAN,
            bonus_points            REAL DEFAULT 0,
            penalty_points          REAL DEFAULT 0,
            summary                 TEXT,
            strengths               TEXT,
            improvements            TEXT,
            coaching_tip            TEXT,
            raw_llm_response        TEXT,
            evaluated_at            DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS achievements (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            name                TEXT NOT NULL,
            description         TEXT,
            icon                TEXT,
            condition_type      TEXT NOT NULL,
            condition_value     TEXT NOT NULL,
            category            TEXT
        );

        CREATE TABLE IF NOT EXISTS user_achievements (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER REFERENCES users(id),
            achievement_id  INTEGER REFERENCES achievements(id),
            earned_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, achievement_id)
        );

        CREATE TABLE IF NOT EXISTS xp_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER REFERENCES users(id),
            session_id  INTEGER REFERENCES sessions(id),
            xp_earned   INTEGER,
            reason      TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
