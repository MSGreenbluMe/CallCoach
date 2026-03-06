"""P11: Scenario Editor — multi-step form for creating/editing scenarios."""

import streamlit as st
from services.scenario_service import (
    get_scenario_by_id, get_checkpoints_for_scenario,
    create_scenario, update_scenario, save_checkpoints,
)
from config import CATEGORIES, CATEGORY_LABELS, LANGUAGES, MOOD_LABELS

_STEPS = [
    ("Basic Info", "info"),
    ("Customer Persona", "person"),
    ("Goal & Checkpoints", "flag"),
    ("ElevenLabs Config", "smart_toy"),
    ("Evaluation Config", "analytics"),
    ("Review & Publish", "publish"),
]


def render():
    """Render the Scenario Editor page."""
    user = st.session_state.get("user", {})
    if user.get("role") not in ("manager", "admin"):
        st.session_state["page"] = "login"
        st.rerun()
        return

    scenario_id = st.session_state.get("edit_scenario_id")
    is_edit = scenario_id is not None

    # Load existing data for edit mode
    if is_edit and "editor_data" not in st.session_state:
        scenario = get_scenario_by_id(scenario_id)
        checkpoints = get_checkpoints_for_scenario(scenario_id)
        if scenario:
            st.session_state["editor_data"] = dict(scenario)
            st.session_state["editor_checkpoints"] = [dict(cp) for cp in checkpoints]
        else:
            st.error("Scenario not found.")
            return
    elif not is_edit and "editor_data" not in st.session_state:
        st.session_state["editor_data"] = {}
        st.session_state["editor_checkpoints"] = []

    # Initialize step
    if "editor_step" not in st.session_state:
        st.session_state["editor_step"] = 0

    step = st.session_state["editor_step"]
    data = st.session_state["editor_data"]

    # Header
    title = f"Edit Scenario" if is_edit else "Create New Scenario"
    st.markdown(
        f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h2 style="font-weight: 800; margin: 0;">{title}</h2>
                <p style="color: #94a3b8; margin: 0;">Step {step + 1} of {len(_STEPS)}</p>
            </div>
            <div style="display: flex; gap: 8px;">
        </div></div>""",
        unsafe_allow_html=True,
    )

    # Step progress bar
    _render_step_nav(step)

    st.markdown("")

    # Render current step
    if step == 0:
        _step_basic_info(data)
    elif step == 1:
        _step_persona(data)
    elif step == 2:
        _step_goal_checkpoints(data)
    elif step == 3:
        _step_elevenlabs(data)
    elif step == 4:
        _step_evaluation(data)
    elif step == 5:
        _step_review(data, is_edit, scenario_id, user)

    st.markdown("")

    # Navigation buttons
    col_cancel, col_back, col_spacer, col_next = st.columns([1, 1, 1, 1])
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            _cleanup_editor()
            st.session_state["page"] = "scenario_management"
            st.rerun()
    with col_back:
        if step > 0:
            if st.button("Back", use_container_width=True):
                st.session_state["editor_step"] = step - 1
                st.rerun()
    with col_next:
        if step < len(_STEPS) - 1:
            if st.button("Next", use_container_width=True, type="primary"):
                st.session_state["editor_step"] = step + 1
                st.rerun()


def _render_step_nav(current_step: int):
    """Render clickable step navigation bar."""
    cols = st.columns(len(_STEPS))
    for i, (name, icon) in enumerate(_STEPS):
        with cols[i]:
            if i < current_step:
                style = "background:#10b981;color:white;border-color:#10b981;"
            elif i == current_step:
                style = "background:#13a4ec;color:white;border-color:#13a4ec;"
            else:
                style = "background:#1e3340;color:#64748b;border-color:#334155;"
            if st.button(name, key=f"step_nav_{i}", use_container_width=True):
                st.session_state["editor_step"] = i
                st.rerun()


def _step_basic_info(data: dict):
    """Step 1: Basic scenario information."""
    st.markdown("#### Basic Information")

    data["name"] = st.text_input("Scenario Name", value=data.get("name", ""),
                                  placeholder="e.g. Product Return Complaint")
    data["description"] = st.text_area("Description", value=data.get("description", ""),
                                        placeholder="Describe the scenario situation...", height=100)

    col1, col2, col3 = st.columns(3)
    with col1:
        cat_options = CATEGORIES
        cat_index = cat_options.index(data.get("category", "SALES")) if data.get("category") in cat_options else 0
        data["category"] = st.selectbox("Category", options=cat_options,
                                         format_func=lambda x: CATEGORY_LABELS.get(x, x), index=cat_index)
    with col2:
        data["difficulty"] = st.slider("Difficulty", 1, 5, value=data.get("difficulty", 3))
    with col3:
        lang_keys = list(LANGUAGES.keys())
        lang_index = lang_keys.index(data.get("language", "cs")) if data.get("language") in lang_keys else 0
        data["language"] = st.selectbox("Language", options=lang_keys,
                                         format_func=lambda x: LANGUAGES.get(x, x), index=lang_index)

    col4, col5 = st.columns(2)
    with col4:
        data["estimated_duration_min"] = st.number_input("Estimated Duration (min)", min_value=1, max_value=60,
                                                          value=data.get("estimated_duration_min", 10))
    with col5:
        data["max_duration_min"] = st.number_input("Max Duration (min)", min_value=1, max_value=60,
                                                    value=data.get("max_duration_min", 15))

    st.session_state["editor_data"] = data


def _step_persona(data: dict):
    """Step 2: Customer persona configuration."""
    st.markdown("#### Customer Persona")

    data["persona_name"] = st.text_input("Customer Name", value=data.get("persona_name", ""),
                                          placeholder="e.g. Jana Novakova")
    data["persona_background"] = st.text_area("Background Story", value=data.get("persona_background", ""),
                                               placeholder="Age, occupation, purchase history...", height=80)

    col1, col2 = st.columns(2)
    with col1:
        mood_keys = list(MOOD_LABELS.keys())
        mood_index = mood_keys.index(data.get("persona_mood", "CALM")) if data.get("persona_mood") in mood_keys else 0
        data["persona_mood"] = st.selectbox("Starting Mood", options=mood_keys,
                                             format_func=lambda x: MOOD_LABELS.get(x, x), index=mood_index)
    with col2:
        data["persona_patience"] = st.slider("Patience Level", 1, 10, value=data.get("persona_patience", 5))

    data["persona_comm_style"] = st.text_input("Communication Style",
                                                value=data.get("persona_comm_style", ""),
                                                placeholder="e.g. Speaks quickly, interrupts often")
    data["persona_hidden_need"] = st.text_area("Hidden Need (agent must discover)",
                                                value=data.get("persona_hidden_need", ""),
                                                placeholder="e.g. Actually wants an upgrade, not just a refund",
                                                height=60)

    st.session_state["editor_data"] = data


def _step_goal_checkpoints(data: dict):
    """Step 3: Call goal and mandatory checkpoints."""
    st.markdown("#### Call Goal")

    data["primary_goal"] = st.text_area("Primary Goal", value=data.get("primary_goal", ""),
                                         placeholder="What must the agent achieve?", height=60)
    data["success_definition"] = st.text_input("Success Definition",
                                                value=data.get("success_definition", ""),
                                                placeholder="What counts as a successful outcome?")
    data["fail_conditions"] = st.text_input("Fail Conditions", value=data.get("fail_conditions", ""),
                                             placeholder="What triggers a failure?")

    st.markdown("---")
    st.markdown("#### Mandatory Checkpoints")
    st.caption("Steps the agent must complete during the call. Order matters.")

    checkpoints = st.session_state.get("editor_checkpoints", [])

    for i, cp in enumerate(checkpoints):
        with st.expander(f"Checkpoint {i + 1}: {cp.get('name', 'Untitled')}", expanded=False):
            cp["name"] = st.text_input("Name", value=cp.get("name", ""), key=f"cp_name_{i}")
            cp["description"] = st.text_input("Description", value=cp.get("description", ""), key=f"cp_desc_{i}")
            cp["detection_hint"] = st.text_input("Detection Hint (for evaluator)",
                                                  value=cp.get("detection_hint", ""), key=f"cp_hint_{i}")
            cp["is_order_strict"] = st.checkbox("Strict order required", value=cp.get("is_order_strict", False),
                                                 key=f"cp_strict_{i}")
            if st.button("Remove", key=f"cp_remove_{i}"):
                checkpoints.pop(i)
                st.session_state["editor_checkpoints"] = checkpoints
                st.rerun()

    if st.button("+ Add Checkpoint"):
        checkpoints.append({"name": "", "description": "", "detection_hint": "", "is_order_strict": False})
        st.session_state["editor_checkpoints"] = checkpoints
        st.rerun()

    st.session_state["editor_data"] = data
    st.session_state["editor_checkpoints"] = checkpoints


def _step_elevenlabs(data: dict):
    """Step 4: ElevenLabs voice AI configuration."""
    st.markdown("#### ElevenLabs Configuration")

    from config import ELEVENLABS_API_KEY
    has_key = bool(ELEVENLABS_API_KEY)

    if has_key:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:6px;margin-bottom:0.5rem;">'
            '<span class="mi" style="color:#10b981;font-size:16px;">check_circle</span>'
            '<span style="color:#10b981;font-size:0.85rem;">ElevenLabs API key detected</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("No ElevenLabs API key found. Add ELEVENLABS_API_KEY to Streamlit Secrets to enable voice calls.")

    # Agent ID — manual input
    col_id, col_btn = st.columns([3, 1])
    with col_id:
        data["elevenlabs_agent_id"] = st.text_input("ElevenLabs Agent ID",
                                                     value=data.get("elevenlabs_agent_id", ""),
                                                     placeholder="Agent ID from ElevenLabs dashboard")
    with col_btn:
        st.markdown('<div style="padding-top: 1.55rem;"></div>', unsafe_allow_html=True)
        auto_disabled = not has_key or not data.get("persona_name")
        if st.button("Auto-create Agent", use_container_width=True, type="primary", disabled=auto_disabled):
            with st.spinner("Creating ElevenLabs agent..."):
                try:
                    from services.elevenlabs_service import create_agent_for_scenario
                    agent_id = create_agent_for_scenario(data)
                    if agent_id:
                        data["elevenlabs_agent_id"] = agent_id
                        st.session_state["editor_data"] = data
                        st.success(f"Agent created: {agent_id}")
                        st.rerun()
                    else:
                        st.error("Agent creation returned empty ID.")
                except Exception as e:
                    st.error(f"Failed: {e}")

    if auto_disabled and has_key and not data.get("persona_name"):
        st.caption("Fill in Customer Persona (step 2) first to enable auto-create.")

    data["voice_id"] = st.text_input("Voice ID (optional)", value=data.get("voice_id", ""),
                                      placeholder="Voice ID for the customer — leave blank for default")

    data["first_message"] = st.text_area("Customer's First Message",
                                          value=data.get("first_message", ""),
                                          placeholder="What the customer says first when calling...",
                                          height=80)

    data["system_prompt"] = st.text_area("System Prompt (Customer AI)",
                                          value=data.get("system_prompt", ""),
                                          placeholder="Full prompt defining customer behavior — auto-generated if blank",
                                          height=150)

    data["temperature"] = st.slider("Temperature (creativity)", 0.0, 1.0,
                                     value=float(data.get("temperature", 0.7)), step=0.1)

    st.session_state["editor_data"] = data


def _step_evaluation(data: dict):
    """Step 5: Evaluation configuration."""
    st.markdown("#### Evaluation Weights")
    st.caption("How much each component contributes to the overall score.")

    col1, col2, col3 = st.columns(3)
    with col1:
        w_general = st.slider("General Quality", 0.0, 1.0, value=0.35, step=0.05, key="w_gen")
    with col2:
        w_checkpoints = st.slider("Checkpoint Completion", 0.0, 1.0, value=0.35, step=0.05, key="w_cp")
    with col3:
        w_goal = st.slider("Goal Achievement", 0.0, 1.0, value=0.30, step=0.05, key="w_goal")

    total = w_general + w_checkpoints + w_goal
    if abs(total - 1.0) > 0.01:
        st.warning(f"Weights should sum to 1.0 (currently {total:.2f})")

    import json
    data["evaluation_weights"] = json.dumps({
        "general": w_general, "checkpoints": w_checkpoints, "goal": w_goal
    })

    st.markdown("---")
    st.markdown("#### Bonus & Penalty Criteria (optional)")

    col_b, col_p = st.columns(2)
    with col_b:
        bonus = st.text_area("Bonus Criteria (one per line)", value=data.get("bonus_criteria", ""),
                              placeholder="e.g. Successful upsell\nCross-sell attempt", height=80)
        data["bonus_criteria"] = bonus
    with col_p:
        penalty = st.text_area("Penalty Criteria (one per line)", value=data.get("penalty_criteria", ""),
                                placeholder="e.g. Used forbidden words\nInterrupted customer", height=80)
        data["penalty_criteria"] = penalty

    st.session_state["editor_data"] = data


def _step_review(data: dict, is_edit: bool, scenario_id: int, user: dict):
    """Step 6: Review all data and publish."""
    st.markdown("#### Review & Publish")

    checkpoints = st.session_state.get("editor_checkpoints", [])

    # Summary cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""<div class="cc-card" style="margin-bottom: 1rem;">
                <h4 style="margin: 0 0 0.75rem 0; color: #13a4ec;">
                    <span class="mi" style="color: #13a4ec;">info</span> Basic Info</h4>
                <div style="font-size: 0.85rem; line-height: 1.8;">
                    <b>Name:</b> {data.get('name', '—')}<br>
                    <b>Category:</b> {CATEGORY_LABELS.get(data.get('category', ''), '—')}<br>
                    <b>Difficulty:</b> {'★' * data.get('difficulty', 0)}{'☆' * (5 - data.get('difficulty', 0))}<br>
                    <b>Language:</b> {LANGUAGES.get(data.get('language', ''), '—')}<br>
                    <b>Duration:</b> {data.get('estimated_duration_min', '?')} – {data.get('max_duration_min', '?')} min
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div class="cc-card" style="margin-bottom: 1rem;">
                <h4 style="margin: 0 0 0.75rem 0; color: #13a4ec;">
                    <span class="mi" style="color: #13a4ec;">person</span> Customer</h4>
                <div style="font-size: 0.85rem; line-height: 1.8;">
                    <b>Name:</b> {data.get('persona_name', '—')}<br>
                    <b>Mood:</b> {MOOD_LABELS.get(data.get('persona_mood', ''), '—')}<br>
                    <b>Patience:</b> {data.get('persona_patience', '?')}/10<br>
                    <b>Hidden Need:</b> {data.get('persona_hidden_need', '—')[:60]}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Goal
    st.markdown(
        f"""<div class="cc-card" style="border-left: 4px solid #13a4ec; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 0.5rem 0;">
                <span class="mi" style="color: #13a4ec;">flag</span> Goal</h4>
            <p style="margin: 0; color: #94a3b8;">{data.get('primary_goal', '—')}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # Checkpoints
    if checkpoints:
        cp_html = ""
        for i, cp in enumerate(checkpoints):
            cp_html += f'<div style="padding: 0.4rem 0; display: flex; gap: 8px; align-items: center;">' \
                        f'<span style="background: #13a4ec; color: white; width: 22px; height: 22px; border-radius: 50%; ' \
                        f'display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; flex-shrink: 0;">{i+1}</span>' \
                        f'<span style="font-size: 0.85rem;">{cp.get("name", "—")}</span></div>'
        st.markdown(
            f"""<div class="cc-card" style="margin-bottom: 1rem;">
                <h4 style="margin: 0 0 0.75rem 0;">
                    <span class="mi" style="color: #13a4ec;">fact_check</span> Checkpoints ({len(checkpoints)})</h4>
                {cp_html}
            </div>""",
            unsafe_allow_html=True,
        )

    # Validation
    errors = []
    if not data.get("name"):
        errors.append("Scenario name is required")
    if not data.get("primary_goal"):
        errors.append("Primary goal is required")
    if not data.get("persona_name"):
        errors.append("Customer name is required")

    if errors:
        for e in errors:
            st.error(e)
    else:
        st.success("All required fields are filled. Ready to publish!")

    st.markdown("")

    # Publish button
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        btn_label = "Update Scenario" if is_edit else "Publish Scenario"
        if st.button(btn_label, use_container_width=True, type="primary", disabled=bool(errors)):
            if is_edit:
                update_scenario(scenario_id, data)
                save_checkpoints(scenario_id, checkpoints)
                st.success("Scenario updated!")
            else:
                new_id = create_scenario(data, user.get("id"))
                save_checkpoints(new_id, checkpoints)
                st.success("Scenario published!")

            _cleanup_editor()
            st.session_state["page"] = "scenario_management"
            st.rerun()

    with col_c:
        if st.button("Test Scenario", use_container_width=True):
            if not errors:
                if not is_edit:
                    new_id = create_scenario(data, user.get("id"))
                    save_checkpoints(new_id, checkpoints)
                    st.session_state["selected_scenario_id"] = new_id
                else:
                    update_scenario(scenario_id, data)
                    save_checkpoints(scenario_id, checkpoints)
                    st.session_state["selected_scenario_id"] = scenario_id
                _cleanup_editor()
                st.session_state["page"] = "pre_call_briefing"
                st.rerun()


def _cleanup_editor():
    """Clean up editor session state."""
    for key in ["editor_data", "editor_checkpoints", "editor_step", "edit_scenario_id"]:
        if key in st.session_state:
            del st.session_state[key]
