"""P1: Login page — simple name + team code login."""

import streamlit as st
from database.db import get_connection
from utils.helpers import dict_from_row


def render():
    """Render the login page."""
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; padding: 2rem 0 1rem 0;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 1.5rem;">
                    <span class="mi" style="color: #13a4ec; font-size: 36px;">headset_mic</span>
                    <span style="font-size: 1.8rem; font-weight: 900; color: white;">CallCoach</span>
                </div>
                <h2 style="font-size: 1.8rem; font-weight: 900; margin-bottom: 0.25rem;">Welcome Back</h2>
                <p style="color: #94A3B8; font-size: 0.95rem;">Master the art of conversation.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Role toggle
        role_tab = st.radio("Rola", ["Agent", "Manager"], horizontal=True, label_visibility="collapsed")

        with st.form("login_form"):
            # Get existing users for quick login
            conn = get_connection()
            filter_role = "agent" if role_tab == "Agent" else "manager"
            users = conn.execute(
                "SELECT id, name, role, team FROM users WHERE role = ? ORDER BY name",
                (filter_role,),
            ).fetchall()
            conn.close()

            if users:
                user_options = {u["name"]: dict(u) for u in users}
                selected = st.selectbox(
                    "Vybrať používateľa",
                    options=list(user_options.keys()),
                    index=0,
                )
            else:
                selected = None
                st.info("Žiadni používatelia pre túto rolu.")

            st.markdown("---")
            st.caption("Alebo sa prihláste manuálne:")

            name = st.text_input("Meno", placeholder="Vaše meno")
            team_code = st.text_input("Team kód", placeholder="napr. Demo")

            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if selected and not name:
                    user_data = user_options[selected]
                    _login_user(user_data["id"])
                elif name:
                    user_id = _get_or_create_user(name, team_code or "Default", filter_role)
                    _login_user(user_id)
                else:
                    st.error("Vyberte používateľa alebo zadajte meno.")


def _login_user(user_id: int):
    """Set session state for logged in user."""
    conn = get_connection()
    user = dict_from_row(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())
    conn.close()

    if user:
        st.session_state["user"] = user
        st.session_state["user_id"] = user["id"]
        st.session_state["user_role"] = user["role"]
        if user["role"] == "manager" or user["role"] == "admin":
            st.session_state["page"] = "manager_dashboard"
        else:
            st.session_state["page"] = "agent_home"
        st.rerun()


def _get_or_create_user(name: str, team: str, role: str) -> int:
    """Get existing user or create new one."""
    conn = get_connection()
    existing = conn.execute("SELECT id FROM users WHERE name = ? AND team = ?", (name, team)).fetchone()
    if existing:
        conn.close()
        return existing["id"]

    cursor = conn.execute(
        "INSERT INTO users (name, role, team) VALUES (?, ?, ?)",
        (name, role, team),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id
