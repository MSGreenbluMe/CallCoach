"""Utility functions for CallCoach."""

from datetime import datetime, timedelta
from config import LEVEL_THRESHOLDS


def get_level_for_xp(xp: int) -> tuple[int, str]:
    """Return (level_number, level_name) for given XP."""
    current_level = 1
    current_name = "Nováčik"
    for level, (name, threshold) in sorted(LEVEL_THRESHOLDS.items()):
        if xp >= threshold:
            current_level = level
            current_name = name
        else:
            break
    return current_level, current_name


def get_xp_for_next_level(xp: int) -> tuple[int, int]:
    """Return (xp_needed_for_next_level, xp_of_current_level) for progress bar."""
    current_level, _ = get_level_for_xp(xp)
    if current_level >= 10:
        return LEVEL_THRESHOLDS[10][1], LEVEL_THRESHOLDS[10][1]

    next_threshold = LEVEL_THRESHOLDS[current_level + 1][1]
    current_threshold = LEVEL_THRESHOLDS[current_level][1]
    return current_threshold, next_threshold


def format_duration(seconds: int) -> str:
    """Format seconds to mm:ss."""
    if seconds is None:
        return "—"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def format_score(score: float) -> str:
    """Format score to string with color indicator."""
    if score is None:
        return "—"
    return f"{score:.0f}%"


def score_color(score: float) -> str:
    """Return color based on score."""
    if score is None:
        return "#6B7280"
    if score >= 80:
        return "#10B981"
    if score >= 50:
        return "#F59E0B"
    return "#EF4444"


def difficulty_stars(difficulty: int) -> str:
    """Return star string for difficulty."""
    return "★" * difficulty + "☆" * (5 - difficulty)


def dict_from_row(row) -> dict:
    """Convert sqlite3.Row to dict."""
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows) -> list[dict]:
    """Convert list of sqlite3.Row to list of dicts."""
    return [dict(row) for row in rows]
