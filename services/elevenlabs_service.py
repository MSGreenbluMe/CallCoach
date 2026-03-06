"""ElevenLabs Conversational AI API wrapper."""

import json
import requests as _requests
from config import ELEVENLABS_API_KEY, ELEVENLABS_DEFAULT_VOICE_ID
from utils.prompt_templates import build_customer_persona_prompt

_BASE_URL = "https://api.elevenlabs.io/v1"


def create_agent_for_scenario(scenario: dict) -> str | None:
    """Create an ElevenLabs Conversational AI agent via REST API.

    Returns agent_id. Raises RuntimeError with details on failure.
    """
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not set.")

    system_prompt = scenario.get("system_prompt") or build_customer_persona_prompt(scenario)
    voice_id = scenario.get("voice_id") or ELEVENLABS_DEFAULT_VOICE_ID or "JBFqnCBsd6RMkjVDRZzb"
    first_message = scenario.get("first_message") or "Dobrý deň."
    language = scenario.get("language", "cs")
    temperature = scenario.get("temperature", 0.7)
    agent_name = f"CallCoach - {scenario.get('name', 'Scenario')}"

    # Non-English agents require "gemini-2.0-flash-001" won't work — use flash v2_5
    llm_model = "gpt-4o-mini" if language == "en" else "gemini-2.5-flash"

    payload = {
        "name": agent_name,
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": system_prompt,
                    "llm": llm_model,
                    "temperature": temperature,
                },
                "first_message": first_message,
                "language": language,
            },
            "tts": {
                "voice_id": voice_id,
            },
        },
    }

    resp = _requests.post(
        f"{_BASE_URL}/convai/agents/create",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )

    if resp.status_code not in (200, 201):
        detail = resp.text[:500]
        raise RuntimeError(f"HTTP {resp.status_code}: {detail}")

    data = resp.json()
    agent_id = data.get("agent_id")
    if not agent_id:
        raise RuntimeError(f"No agent_id in response: {json.dumps(data)[:300]}")
    return agent_id


def get_signed_url(agent_id: str) -> str | None:
    """Get a signed URL for starting a conversation with an agent."""
    if not ELEVENLABS_API_KEY or not agent_id:
        return None

    try:
        from elevenlabs import ElevenLabs

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        response = client.conversational_ai.get_signed_url(agent_id=agent_id)
        return response.signed_url

    except Exception as e:
        print(f"ElevenLabs signed URL error: {e}")
        return None


def get_conversation_transcript(conversation_id: str) -> str | None:
    """Retrieve transcript for a completed conversation."""
    if not ELEVENLABS_API_KEY or not conversation_id:
        return None

    try:
        from elevenlabs import ElevenLabs

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        conversation = client.conversational_ai.get_conversation(conversation_id=conversation_id)

        transcript_lines = []
        for turn in conversation.transcript:
            role = "Zákazník" if turn.role == "agent" else "Agent"
            transcript_lines.append(f"{role}: {turn.message}")

        return "\n".join(transcript_lines)

    except Exception as e:
        print(f"ElevenLabs transcript error: {e}")
        return None


def get_conversation_audio_url(conversation_id: str) -> str | None:
    """Get audio URL for a conversation recording."""
    if not ELEVENLABS_API_KEY or not conversation_id:
        return None

    try:
        from elevenlabs import ElevenLabs

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        conversation = client.conversational_ai.get_conversation(conversation_id=conversation_id)
        return getattr(conversation, "recording_url", None)

    except Exception as e:
        print(f"ElevenLabs audio error: {e}")
        return None
