"""
skill_router.py — NISHA Skill Router
Routes user intent to the correct skill, then the correct tool.
Also handles sub-agent delegation.
"""
from core.decision_engine import route_intent
from skills.skill_registry import SKILL_REGISTRY

__all__ = ["route_intent", "route_to_agent"]


def route_to_agent(intent: str, context: dict) -> str:
    """
    Returns agent name if the task should be delegated to a sub-agent.
    Returns None if Nisha handles it directly.
    """
    intent_lower = intent.lower()

    if any(w in intent_lower for w in ["scout", "research idea", "validate idea", "find opportunity"]):
        return "scout"
    if any(w in intent_lower for w in ["asha", "build project", "github issue", "run tests", "code review"]):
        return "asha"
    if any(w in intent_lower for w in ["mira", "job search", "career", "apply for", "draft application", "opportunity tracker"]):
        return "mira"
    if any(w in intent_lower for w in ["operator", "execute workflow", "computer workflow", "automate task"]):
        return "operator"

    return None  # Nisha handles directly
