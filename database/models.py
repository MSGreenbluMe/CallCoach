from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class User:
    id: Optional[int] = None
    name: str = ""
    email: Optional[str] = None
    role: str = "agent"
    team: Optional[str] = None
    avatar_url: Optional[str] = None
    xp: int = 0
    level: int = 1
    streak_days: int = 0
    last_active: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class Scenario:
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    category: str = "COMPLAINTS"
    difficulty: int = 1
    language: str = "cs"
    estimated_duration_min: Optional[int] = None
    max_duration_min: Optional[int] = None
    persona_name: Optional[str] = None
    persona_background: Optional[str] = None
    persona_mood: Optional[str] = None
    persona_patience: Optional[int] = None
    persona_comm_style: Optional[str] = None
    persona_hidden_need: Optional[str] = None
    primary_goal: Optional[str] = None
    success_definition: Optional[str] = None
    fail_conditions: Optional[str] = None
    elevenlabs_agent_id: Optional[str] = None
    voice_id: Optional[str] = None
    system_prompt: Optional[str] = None
    first_message: Optional[str] = None
    knowledge_base_config: Optional[str] = None
    temperature: float = 0.7
    evaluation_weights: Optional[str] = None
    bonus_criteria: Optional[str] = None
    penalty_criteria: Optional[str] = None
    is_active: bool = True
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Checkpoint:
    id: Optional[int] = None
    scenario_id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    order_index: int = 0
    is_order_strict: bool = False
    detection_hint: Optional[str] = None


@dataclass
class Session:
    id: Optional[int] = None
    user_id: Optional[int] = None
    scenario_id: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    elevenlabs_conversation_id: Optional[str] = None
    status: str = "in_progress"
    created_at: Optional[datetime] = None


@dataclass
class Evaluation:
    id: Optional[int] = None
    session_id: Optional[int] = None
    overall_score: Optional[float] = None
    communication_clarity: Optional[float] = None
    empathy_rapport: Optional[float] = None
    active_listening: Optional[float] = None
    professional_language: Optional[float] = None
    call_structure: Optional[float] = None
    call_control: Optional[float] = None
    objection_handling: Optional[float] = None
    checkpoint_results: Optional[str] = None
    checkpoint_order_ok: Optional[bool] = None
    goal_achieved: Optional[str] = None
    hidden_need_found: Optional[bool] = None
    bonus_points: float = 0.0
    penalty_points: float = 0.0
    summary: Optional[str] = None
    strengths: Optional[str] = None
    improvements: Optional[str] = None
    coaching_tip: Optional[str] = None
    raw_llm_response: Optional[str] = None
    evaluated_at: Optional[datetime] = None


@dataclass
class Achievement:
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    icon: Optional[str] = None
    condition_type: str = ""
    condition_value: str = ""
    category: Optional[str] = None


@dataclass
class UserAchievement:
    id: Optional[int] = None
    user_id: Optional[int] = None
    achievement_id: Optional[int] = None
    earned_at: Optional[datetime] = None


@dataclass
class XpLog:
    id: Optional[int] = None
    user_id: Optional[int] = None
    session_id: Optional[int] = None
    xp_earned: int = 0
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
