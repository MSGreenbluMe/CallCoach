import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get_secret(key: str, default: str = "") -> str:
    """Get secret from st.secrets (Streamlit Cloud) or env var (local)."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


# ElevenLabs
ELEVENLABS_API_KEY = _get_secret("ELEVENLABS_API_KEY")
ELEVENLABS_DEFAULT_VOICE_ID = _get_secret("ELEVENLABS_DEFAULT_VOICE_ID")

# Gemini
GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")

# App
APP_SECRET_KEY = _get_secret("APP_SECRET_KEY", "callcoach-secret-key")
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "callcoach.db")
AUDIO_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "data", "audio")
MAX_CALL_DURATION_MINUTES = int(_get_secret("MAX_CALL_DURATION_MINUTES", "15"))
DEFAULT_LANGUAGE = _get_secret("DEFAULT_LANGUAGE", "cs")

# Evaluation weights (defaults)
DEFAULT_WEIGHT_GENERAL = 0.35
DEFAULT_WEIGHT_CHECKPOINTS = 0.35
DEFAULT_WEIGHT_GOAL = 0.30

# XP constants
XP_BASE_CALL = 50
XP_PER_POINT_ABOVE_70 = 1
XP_PERFECT_BONUS = 100
XP_FIRST_SCENARIO = 25
XP_DAILY_STREAK = 20

# Level thresholds
LEVEL_THRESHOLDS = {
    1: ("Rookie", 0),
    2: ("Cadet", 200),
    3: ("Junior Agent", 500),
    4: ("Agent", 1000),
    5: ("Senior Agent", 2000),
    6: ("Expert", 4000),
    7: ("Master", 7000),
    8: ("Guru", 11000),
    9: ("Legend", 16000),
    10: ("Call Center Jedi", 25000),
}

# Categories
CATEGORIES = ["SALES", "RETENTION", "TECH_SUPPORT", "COMPLAINTS", "BILLING", "ONBOARDING"]

CATEGORY_LABELS = {
    "SALES": "Sales",
    "RETENTION": "Retention",
    "TECH_SUPPORT": "Tech Support",
    "COMPLAINTS": "Complaints",
    "BILLING": "Billing",
    "ONBOARDING": "Onboarding",
}

CATEGORY_COLORS = {
    "SALES": "#10B981",
    "RETENTION": "#F59E0B",
    "TECH_SUPPORT": "#3B82F6",
    "COMPLAINTS": "#EF4444",
    "BILLING": "#8B5CF6",
    "ONBOARDING": "#06B6D4",
}

MOOD_LABELS = {
    "CALM": "Calm",
    "FRUSTRATED": "Frustrated",
    "ANGRY": "Angry",
    "CONFUSED": "Confused",
    "IMPATIENT": "Impatient",
    "FRIENDLY": "Friendly",
}

LANGUAGES = {
    "cs": "Czech",
    "sk": "Slovak",
    "hu": "Hungarian",
    "en": "English",
}
