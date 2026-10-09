# skills/skill_router.py
# Routes intent to correct skill/tool

from core.decision_engine import route_intent

# Re-export the route_intent function for compatibility
__all__ = ["route_intent"]