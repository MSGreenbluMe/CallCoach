"""P5: Active Call — real-time voice call with ElevenLabs AI customer."""

import streamlit as st
from datetime import datetime
from services.scenario_service import get_scenario_by_id, get_checkpoints_for_scenario
from services.elevenlabs_service import get_signed_url
from services.evaluation_service import create_session, complete_session
from config import ELEVENLABS_API_KEY


def render():
    """Render the Active Call page."""
    scenario_id = st.session_state.get("selected_scenario_id")
    user = st.session_state.get("user", {})

    if not scenario_id:
        st.session_state["page"] = "scenario_browser"
        st.rerun()
        return

    scenario = get_scenario_by_id(scenario_id)
    if not scenario:
        st.error("Scenario not found.")
        return

    checkpoints = get_checkpoints_for_scenario(scenario_id)

    # Initialize session if not already started
    if "active_session_id" not in st.session_state:
        session_id = create_session(user["id"], scenario_id)
        st.session_state["active_session_id"] = session_id
        st.session_state["call_start_time"] = datetime.now().isoformat()

    # ── Main layout: call area + objectives sidebar ──
    col_main, col_side = st.columns([3, 1])

    with col_main:
        # Call header with timer
        st.markdown(
            f"""
            <div style="text-align: center; padding-top: 1rem;">
                <h2 style="font-weight: 700; margin-bottom: 0.25rem;">{scenario['name']}</h2>
                <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 8px; height: 8px; border-radius: 50%; background: #ef4444;
                                   animation: blink 1.5s infinite;"></div>
                        <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 500;">Call in Progress</span>
                    </div>
                    <span id="call-timer" style="font-family: monospace; font-weight: 700; font-size: 1.1rem;
                                                 color: white; background: #1e3340; padding: 4px 12px;
                                                 border-radius: 8px;">00:00</span>
                </div>
            </div>
            <style>
                @keyframes blink {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
            </style>
            <script>
                (function() {{
                    var start = Date.now();
                    var el = document.getElementById('call-timer');
                    if (el) {{
                        setInterval(function() {{
                            var s = Math.floor((Date.now() - start) / 1000);
                            var m = Math.floor(s / 60);
                            el.textContent = String(m).padStart(2,'0') + ':' + String(s % 60).padStart(2,'0');
                        }}, 1000);
                    }}
                }})();
            </script>
            """,
            unsafe_allow_html=True,
        )

        # Check if ElevenLabs is configured
        if ELEVENLABS_API_KEY and scenario.get("elevenlabs_agent_id"):
            _render_elevenlabs_call(scenario, checkpoints)
        else:
            _render_mock_call(scenario, checkpoints)

    # ── Objectives sidebar ──
    with col_side:
        st.markdown(
            """<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 1rem;">
                <span class="mi" style="color: #13a4ec;">checklist</span>
                <h4 style="margin: 0; font-weight: 700;">Objectives</h4>
            </div>
            <p style="color: #64748b; font-size: 0.8rem; margin-bottom: 0.75rem;">Complete these steps during the call:</p>""",
            unsafe_allow_html=True,
        )

        for cp in checkpoints:
            st.markdown(
                f"""<div style="display: flex; align-items: flex-start; gap: 10px; padding: 0.5rem 0.75rem;
                              border-radius: 8px; background: #15242b; border: 1px solid #1e3340; margin-bottom: 0.4rem;">
                    <span class="mi" style="color: #334155; font-size: 18px; margin-top: 1px;">radio_button_unchecked</span>
                    <div>
                        <div style="font-weight: 500; font-size: 0.85rem;">{cp['name']}</div>
                        <div style="color: #64748b; font-size: 0.75rem; margin-top: 2px;">{cp.get('description', '')[:60]}</div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("")
        st.markdown(
            """<div style="background: #13a4ec15; border: 1px solid #13a4ec30; border-radius: 8px;
                          padding: 0.75rem; display: flex; align-items: center; gap: 8px;">
                <span class="mi" style="color: #13a4ec; font-size: 18px;">smart_toy</span>
                <span style="color: #94a3b8; font-size: 0.75rem;">AI is actively analyzing your tone and empathy.</span>
            </div>""",
            unsafe_allow_html=True,
        )


def _render_elevenlabs_call(scenario: dict, checkpoints: list[dict]):
    """Render real ElevenLabs voice call interface."""
    import streamlit.components.v1 as components

    agent_id = scenario.get("elevenlabs_agent_id")
    if not agent_id:
        st.warning("ElevenLabs agent not configured. Using mock mode.")
        _render_mock_call(scenario, checkpoints)
        return

    # ElevenLabs Convai widget — must use components.html() because
    # st.markdown strips <script> tags
    components.html(
        f"""
        <style>
            body {{ margin: 0; background: transparent; display: flex;
                   justify-content: center; align-items: center; min-height: 350px; }}
        </style>
        <elevenlabs-convai agent-id="{agent_id}"></elevenlabs-convai>
        <script src="https://elevenlabs.io/convai-widget/index.js" async></script>
        """,
        height=400,
    )

    st.markdown("")
    st.caption("Use the widget above to talk with the AI customer. When done, click End Call below.")

    # End call button
    st.markdown('<style>div[data-testid="stButton"] button[kind="primary"] { background-color: #ef4444 !important; border-color: #ef4444 !important; } div[data-testid="stButton"] button[kind="primary"]:hover { background-color: #dc2626 !important; border-color: #dc2626 !important; }</style>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        if st.button("End Call", use_container_width=True, type="primary", key="end_call_el"):
            session_id = st.session_state.get("active_session_id")
            start_time = st.session_state.get("call_start_time", datetime.now().isoformat())
            duration = int((datetime.now() - datetime.fromisoformat(start_time)).total_seconds())

            # For ElevenLabs calls, transcript comes from the widget/API
            # For now, use a placeholder — real transcript retrieval requires conversation_id
            transcript = "[ElevenLabs voice call — transcript retrieval pending]"
            complete_session(session_id, transcript, duration)

            st.session_state["view_session_id"] = session_id
            st.session_state["page"] = "evaluating"
            del st.session_state["active_session_id"]
            del st.session_state["call_start_time"]
            st.rerun()


def _render_mock_call(scenario: dict, checkpoints: list[dict]):
    """Render mock call interface for testing without ElevenLabs."""
    # Waveform visualization
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 4px; height: 120px; margin: 1rem 0;">
                <div style="width: 4px; background: #13a4ec40; border-radius: 2px; height: 20px;"></div>
                <div style="width: 4px; background: #13a4ec60; border-radius: 2px; height: 40px;"></div>
                <div style="width: 4px; background: #13a4ec80; border-radius: 2px; height: 60px;"></div>
                <div style="width: 4px; background: #13a4ec; border-radius: 2px; height: 80px;"></div>
                <div style="width: 4px; background: #13a4eccc; border-radius: 2px; height: 100px;"></div>
                <div style="width: 4px; background: #13a4ec; border-radius: 2px; height: 120px; animation: wavepulse 1.5s infinite;"></div>
                <div style="width: 4px; background: #13a4eccc; border-radius: 2px; height: 100px;"></div>
                <div style="width: 4px; background: #13a4ec; border-radius: 2px; height: 80px;"></div>
                <div style="width: 4px; background: #13a4ec80; border-radius: 2px; height: 60px;"></div>
                <div style="width: 4px; background: #13a4ec60; border-radius: 2px; height: 40px;"></div>
                <div style="width: 4px; background: #13a4ec40; border-radius: 2px; height: 20px;"></div>
            </div>
            <style>
            @keyframes wavepulse {
                0%, 100% { transform: scaleY(1); }
                50% { transform: scaleY(0.7); }
            }
            </style>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;">
                Mock Mode — paste or edit the transcript below
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Mock transcript input
    default_transcript = _get_mock_transcript(scenario)
    transcript = st.text_area(
        "Transcript",
        value=default_transcript,
        height=250,
        label_visibility="collapsed",
    )

    st.markdown("")

    # End call button — centered, red
    st.markdown('<style>div[data-testid="stButton"] button[kind="primary"] { background-color: #ef4444 !important; border-color: #ef4444 !important; } div[data-testid="stButton"] button[kind="primary"]:hover { background-color: #dc2626 !important; border-color: #dc2626 !important; }</style>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        if st.button("End Call", use_container_width=True, type="primary"):
            session_id = st.session_state.get("active_session_id")
            start_time = st.session_state.get("call_start_time", datetime.now().isoformat())
            duration = int((datetime.now() - datetime.fromisoformat(start_time)).total_seconds())

            complete_session(session_id, transcript, duration)

            st.session_state["view_session_id"] = session_id
            st.session_state["page"] = "evaluating"
            del st.session_state["active_session_id"]
            del st.session_state["call_start_time"]
            st.rerun()


def _get_mock_transcript(scenario: dict) -> str:
    """Generate a simple mock transcript for testing."""
    persona = scenario.get("persona_name", "Zákazník")
    return f"""{persona}: {scenario.get('first_message', 'Dobrý deň.')}
Agent: Dobrý deň, vitajte na linke zákazníckej podpory. Moje meno je Petra a rada vám pomôžem. Môžete mi prosím povedať vaše meno a číslo objednávky?
{persona}: Áno, som {persona}. Číslo objednávky je 2024-8847.
Agent: Ďakujem, {persona}. Vidím vašu objednávku. Povedzte mi prosím, aký máte problém?
{persona}: Tak, ten problém je taký, že to jednoducho nefunguje. Skúšala som to viackrát a stále to isté.
Agent: Rozumiem, to musí byť veľmi frustrujúce. Prepáčte za nepríjemnosti. Mohli by ste mi prosím popísať presnejšie, čo sa deje?
{persona}: No proste to nefunguje správne. Zastaví sa to v polovici a musím to robiť ručne.
Agent: Chápem, to je naozaj nepríjemné. Poďme to vyriešiť. Mám pre vás niekoľko možností — môžeme zariadiť opravu, alebo ak by ste preferovali, môžeme vám ponúknuť výmenu za novší model.
{persona}: A to by šlo? Výmena? To by bolo asi najlepšie riešenie.
Agent: Samozrejme! Môžeme vám ponúknuť výmenu za vyšší model s malým doplatkom. Zariadim to pre vás hneď. Súhlasíte s týmto riešením?
{persona}: Áno, to znie dobre. Ďakujem.
Agent: Výborne. Takže zhrniem — dohodli sme sa na výmene za vyšší model. Kuriér k vám príde do 3 pracovných dní. Dostanete potvrdzovací email. Je ešte niečo, s čím by som vám mohla pomôcť?
{persona}: Nie, to je všetko. Ďakujem za pomoc.
Agent: Nemáte za čo, {persona}. Pekný deň a ďakujem za váš hovor. Dovidenia."""
