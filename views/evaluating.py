"""P6: Evaluating (Loading) — shown while Gemini processes the transcript."""

import streamlit as st
import time
import random
from services.evaluation_service import evaluate_session


_STEPS = [
    ("Transcribing Audio", "Converting conversation to text."),
    ("Analyzing Tone", "Evaluating empathy and clarity levels."),
    ("Checking Objectives", "Verifying script adherence and objection handling."),
    ("Generating Feedback", "Building your personalized scorecard."),
]

_TIPS = [
    "Using the customer's name twice during a call can increase perceived rapport by up to 15%.",
    "Paraphrasing the customer's words builds trust and reduces escalation.",
    "The first 30 seconds of a call set the tone for the entire interaction.",
    "Always summarize agreed steps before ending the call.",
    "Active listening = paraphrasing + follow-up questions.",
]


def render():
    """Render the evaluation loading screen, then redirect to scorecard."""
    session_id = st.session_state.get("view_session_id")

    if not session_id:
        st.session_state["page"] = "agent_home"
        st.rerun()
        return

    # ── Header ──
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #15242b;
                       border: 1px solid #1e3340; padding: 4px 12px; border-radius: 20px;
                       font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem;">
                <span class="mi" style="font-size: 14px; color: #13a4ec;">auto_awesome</span> Powered by Gemini
            </div>
            <h1 style="font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem;">Evaluating your call...</h1>
            <p style="color: #94a3b8;">Our AI is analyzing your performance metrics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Progress indicator ──
    progress_placeholder = st.empty()
    steps_placeholder = st.empty()

    # ── Pro Tip ──
    tip = random.choice(_TIPS)
    st.markdown(
        f"""
        <div style="background: linear-gradient(90deg, #13a4ec10, #6366f110);
                   border: 1px solid #13a4ec20; border-radius: 12px; padding: 1rem;
                   display: flex; align-items: flex-start; gap: 12px; max-width: 700px; margin: 1.5rem auto;">
            <div style="background: #15242b; border-radius: 8px; padding: 6px; flex-shrink: 0;">
                <span class="mi" style="color: #13a4ec;">lightbulb</span>
            </div>
            <div>
                <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 4px;">Pro Tip</div>
                <div style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5;">{tip}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Run evaluation with progress animation ──
    try:
        # Step 1: Transcribing
        _render_progress(progress_placeholder, steps_placeholder, 0, 25)
        time.sleep(0.5)

        # Step 2: Analyzing
        _render_progress(progress_placeholder, steps_placeholder, 1, 50)
        time.sleep(0.4)

        # Step 3: Checking + actual evaluation
        _render_progress(progress_placeholder, steps_placeholder, 2, 65)
        result = evaluate_session(session_id)

        # Step 4: Generating
        _render_progress(progress_placeholder, steps_placeholder, 3, 90)
        time.sleep(0.3)

        _render_progress(progress_placeholder, steps_placeholder, 4, 100)
        time.sleep(0.4)

        st.session_state["eval_result"] = result
        st.session_state["page"] = "scorecard"
        st.rerun()

    except Exception as e:
        st.error(f"Error during evaluation: {e}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Retry", use_container_width=True, type="primary"):
                st.rerun()
        with col2:
            if st.button("Back Home", use_container_width=True):
                st.session_state["page"] = "agent_home"
                st.rerun()


def _render_progress(progress_ph, steps_ph, current_step: int, pct: int):
    """Render the circular progress + step list."""
    # Circular progress via SVG
    offset = 283 - (283 * pct / 100)
    progress_ph.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin: 1rem 0;">
            <div style="position: relative; width: 140px; height: 140px;">
                <svg style="width: 100%; height: 100%; transform: rotate(-90deg);" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#1e3340" stroke-width="4"/>
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#13a4ec" stroke-width="4"
                            stroke-dasharray="283" stroke-dashoffset="{offset}" stroke-linecap="round"/>
                </svg>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                    <div style="font-size: 2rem; font-weight: 800;">{pct}%</div>
                    <div style="color: #64748b; font-size: 0.7rem;">Complete</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Steps list
    steps_html = '<div style="max-width: 500px; margin: 0 auto;">'
    steps_html += '<div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">'
    steps_html += '<span style="font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">Analysis Status</span>'
    steps_html += f'<span style="background: #13a4ec20; color: #13a4ec; font-size: 0.75rem; font-weight: 600; padding: 2px 10px; border-radius: 12px;">Step {min(current_step + 1, 4)} of 4</span>'
    steps_html += '</div>'

    for i, (name, desc) in enumerate(_STEPS):
        if i < current_step:
            icon_html = '<div style="width: 22px; height: 22px; border-radius: 50%; background: #10b98130; color: #10b981; display: flex; align-items: center; justify-content: center;"><span class="mi" style="font-size: 14px;">check</span></div>'
            name_style = "font-weight: 600; color: white;"
        elif i == current_step:
            icon_html = '<div style="width: 22px; height: 22px; border-radius: 50%; background: #13a4ec; color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px #13a4ec80;"><span class="mi" style="font-size: 14px;">sync</span></div>'
            name_style = "font-weight: 600; color: #13a4ec;"
        else:
            icon_html = '<div style="width: 22px; height: 22px; border-radius: 50%; background: #1e3340; border: 1px solid #334155; display: flex; align-items: center; justify-content: center;"><div style="width: 6px; height: 6px; border-radius: 50%; background: #334155;"></div></div>'
            name_style = "color: #64748b;"

        connector = ""
        if i < len(_STEPS) - 1:
            c_color = "#10b98130" if i < current_step else "#1e3340"
            connector = f'<div style="width: 2px; height: 20px; background: {c_color}; margin-left: 10px;"></div>'

        steps_html += f'''
        <div style="display: flex; align-items: flex-start; gap: 12px;">
            <div style="display: flex; flex-direction: column; align-items: center;">
                {icon_html}{connector}
            </div>
            <div style="padding-bottom: 0.5rem;">
                <div style="{name_style} font-size: 0.85rem;">{name}</div>
                <div style="color: #64748b; font-size: 0.75rem; margin-top: 2px;">{desc}</div>
            </div>
        </div>'''

    steps_html += '</div>'
    steps_ph.markdown(steps_html, unsafe_allow_html=True)
