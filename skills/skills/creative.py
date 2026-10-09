"""
creative.py — Creative Skill
Tools: LLM direct (writing, brainstorming)
"""
def handle(intent: str, context: dict) -> dict:
    return {
        "status": "ok",
        "mode": "creative",
        "message": "Creative mode active. Send your request and I'll draft it for you.",
    }
