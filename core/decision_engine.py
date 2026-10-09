# core/decision_engine.py — routing priority order

def route_intent(intent: str, context: dict) -> str:
    """
    Returns the skill name to handle this intent.
    Rules applied in order — first match wins.
    """

    # Rule 1 — Domain exclusivity (hardcoded, never overridden)
    if any(w in intent for w in ["steam", "epic", "game update", "install game"]):
        return "games"  # ONLY game_updater. Never browser_control for this.

    # Rule 2 — Vision triggers (explicit)
    if any(w in intent for w in ["screen", "camera", "what do you see", "look at"]):
        return "vision"

    # Rule 3 — Active task continuation
    if context.get("active_skill"):
        return context["active_skill"]  # Stay in same skill if task in progress

    # Rule 4 — Communication
    if any(w in intent for w in ["send", "message", "whatsapp", "telegram", "remind"]):
        return "communication"

    # Rule 5 — Coding
    if any(w in intent for w in ["code", "build", "script", "program", "debug", "fix error"]):
        return "coding"

    # Rule 6 — File operations
    if any(w in intent for w in ["file", "folder", "document", "read", "open", "delete", "organize"]):
        return "file_ops"

    # Rule 7 — Media
    if any(w in intent for w in ["play", "youtube", "watch", "video", "music"]):
        return "media"

    # Rule 8 — Web/research
    if any(w in intent for w in ["search", "find", "what is", "who is", "price", "news", "research"]):
        return "web_intelligence"

    # Rule 9 — Hardware
    if any(w in intent for w in ["cpu", "ram", "memory", "temperature", "battery", "performance"]):
        return "hardware"

    # Rule 10 — System control (broad fallback for action commands)
    if any(w in intent for w in ["open", "close", "volume", "brightness", "wifi", "shutdown"]):
        return "system_control"

    # Default — web intelligence (best general fallback)
    return "web_intelligence"