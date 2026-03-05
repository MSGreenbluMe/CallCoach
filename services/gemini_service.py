"""Gemini API wrapper for call evaluation."""

import json
from config import GEMINI_API_KEY
from utils.prompt_templates import build_evaluation_prompt


def evaluate_transcript(scenario: dict, checkpoints: list[dict], transcript: str) -> dict:
    """Send transcript to Gemini for evaluation. Returns parsed JSON result."""
    if not GEMINI_API_KEY:
        return _mock_evaluation(checkpoints)

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = build_evaluation_prompt(scenario, checkpoints, transcript)

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.3,
            },
        )

        result = json.loads(response.text)
        return result

    except Exception as e:
        print(f"Gemini evaluation error: {e}")
        return _mock_evaluation(checkpoints)


def _mock_evaluation(checkpoints: list[dict]) -> dict:
    """Return mock evaluation for testing without API key."""
    import random

    cp_results = []
    for cp in checkpoints:
        cp_results.append({
            "checkpoint_id": cp["id"],
            "passed": random.random() > 0.3,
            "evidence": f"Mock evidence for: {cp['name']}",
        })

    return {
        "communication_clarity": {"score": random.randint(5, 9), "evidence": "Mock: Agent komunikoval zrozumiteľne.", "recommendation": "Skúste štrukturovať myšlienky ešte jasnejšie."},
        "empathy_rapport": {"score": random.randint(4, 9), "evidence": "Mock: Agent prejavil empatiu.", "recommendation": "Viac parafrázujte zákazníkove pocity."},
        "active_listening": {"score": random.randint(5, 8), "evidence": "Mock: Agent kládol doplňujúce otázky.", "recommendation": "Skúste viac parafrázovať."},
        "professional_language": {"score": random.randint(6, 10), "evidence": "Mock: Profesionálny jazyk.", "recommendation": "Udržujte profesionálny tón."},
        "call_structure": {"score": random.randint(5, 9), "evidence": "Mock: Hovor mal logickú štruktúru.", "recommendation": "Dbajte na plynulé prechody."},
        "call_control": {"score": random.randint(4, 8), "evidence": "Mock: Agent viedol hovor.", "recommendation": "Buďte asertívnejší pri vedení hovoru."},
        "objection_handling": {"score": random.randint(4, 8), "evidence": "Mock: Agent zvládol námietky.", "recommendation": "Pripravte si viac argumentov."},
        "checkpoints": cp_results,
        "checkpoint_order_correct": random.random() > 0.3,
        "goal_achieved": random.choice(["ACHIEVED", "PARTIAL", "FAILED"]),
        "hidden_need_found": random.random() > 0.5,
        "summary": "Mock: Agent zvládol hovor na dobrej úrovni. Komunikácia bola profesionálna, zákazník bol v konečnom dôsledku spokojný.",
        "strengths": [
            "Profesionálny a priateľský tón",
            "Dobrá štruktúra hovoru",
            "Aktívne počúvanie zákazníka",
        ],
        "improvements": [
            "Viac empatie na začiatku hovoru",
            "Lepšie zistenie skrytých potrieb",
            "Rýchlejšie ponúknuť riešenie",
        ],
        "coaching_tip": "Skúste na začiatku hovoru parafrázovať problém zákazníka vlastnými slovami — pomáha to budovať dôveru.",
    }
