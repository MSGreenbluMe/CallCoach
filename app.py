"""CallCoach — AI Tréningový Bot pre Call Centrá
Main Streamlit entry point with routing and session management.
"""

import streamlit as st
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db
from database.seed import seed_all

# Page imports
from views import login, agent_home, scenario_browser, pre_call_briefing
from views import active_call, evaluating, scorecard
from views import manager_dashboard, agent_detail, achievements


# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CallCoach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<style>
    /* Font */
    *, .stApp, .stMarkdown, p, span, label, h1, h2, h3, h4, h5, h6, button, input, textarea, select {
        font-family: 'Inter', sans-serif !important;
    }

    /* Hide Streamlit branding but keep sidebar toggle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
        height: 2.5rem !important;
    }
    /* Hide the page-title / decoration inside the header, keep the collapse btn */
    header[data-testid="stHeader"] [data-testid="stDecoration"],
    header[data-testid="stHeader"] [data-testid="stToolbar"] {display: none;}

    /* Tighter padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }

    /* Card component */
    .cc-card {
        background: #15242b;
        border: 1px solid #1e3340;
        border-radius: 12px;
        padding: 1.25rem;
    }

    /* Material icon inline helper */
    .mi { font-family: 'Material Symbols Outlined' !important; font-size: 20px; vertical-align: middle; }
</style>
""", unsafe_allow_html=True)


# ── Database Init ────────────────────────────────────────────────────────────
@st.cache_resource
def setup_database():
    """Initialize database and seed data on first run."""
    init_db()
    seed_all()
    return True

setup_database()


# ── Session State Init ───────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "user" not in st.session_state:
    st.session_state["user"] = None


# ── Sidebar Navigation ──────────────────────────────────────────────────────
def render_sidebar():
    """Render navigation sidebar for logged-in users."""
    user = st.session_state.get("user")
    if not user:
        return

    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; padding: 0.5rem 0 1rem 0;">
                <span class="mi" style="color: #13a4ec; font-size: 28px;">headset_mic</span>
                <div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: white;">CallCoach</div>
                    <div style="color: #94A3B8; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Simulator</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # User info
        initials = "".join(w[0] for w in user.get("name", "?").split()[:2]).upper()
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; padding: 0.5rem 0;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background: #1e3340;
                           display: flex; align-items: center; justify-content: center;
                           font-weight: 700; font-size: 0.8rem; color: #13a4ec;">{initials}</div>
                <div>
                    <div style="font-weight: 600; font-size: 0.85rem;">{user.get('name', '')}</div>
                    <div style="color: #94A3B8; font-size: 0.7rem;">{user.get('role', '').capitalize()}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        role = user.get("role", "agent")
        current = st.session_state.get("page", "")

        if role == "agent":
            _nav_btn("dashboard", "Home", "agent_home", current)
            _nav_btn("headset_mic", "Training", "scenario_browser", current)
            _nav_btn("emoji_events", "Achievements", "achievements", current)
        elif role in ("manager", "admin"):
            _nav_btn("dashboard", "Dashboard", "manager_dashboard", current)
            _nav_btn("headset_mic", "Scenarios", "scenario_browser", current)

        st.markdown("---")

        if st.button("Log Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def _nav_btn(icon: str, label: str, target_page: str, current_page: str):
    """Render a sidebar navigation button."""
    is_active = current_page == target_page
    if st.button(f"{label}", use_container_width=True, type="primary" if is_active else "secondary"):
        st.session_state["page"] = target_page
        st.rerun()


# ── Router ───────────────────────────────────────────────────────────────────
PAGE_MAP = {
    "login": login.render,
    "agent_home": agent_home.render,
    "scenario_browser": scenario_browser.render,
    "pre_call_briefing": pre_call_briefing.render,
    "active_call": active_call.render,
    "evaluating": evaluating.render,
    "scorecard": scorecard.render,
    "manager_dashboard": manager_dashboard.render,
    "agent_detail": agent_detail.render,
    "achievements": achievements.render,
}


def main():
    """Main app router."""
    current_page = st.session_state.get("page", "login")

    # Redirect to login if not logged in (except login page)
    if current_page != "login" and not st.session_state.get("user"):
        current_page = "login"
        st.session_state["page"] = "login"

    # Show sidebar only when logged in
    if st.session_state.get("user"):
        render_sidebar()

    page_func = PAGE_MAP.get(current_page, login.render)
    page_func()


main()
