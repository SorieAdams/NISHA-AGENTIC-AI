"""
core/decision_engine.py — NISHA Decision Engine
Full intent → skill → tool routing pipeline.
ZOEY-inspired: goal-based reasoning before tool selection.
"""
from typing import Optional


def route_intent(intent: str, context: dict) -> str:
    """
    Returns the skill name to handle this intent.
    Rules applied in order — first match wins.
    """
    intent_lower = intent.lower()

    # Rule 0 — Sub-agent delegation check
    if any(w in intent_lower for w in ["scout", "asha", "mira", "operator",
                                        "research agent", "validate idea",
                                        "build project", "career agent"]):
        return "agents"

    # Rule 1 — Domain exclusivity (hardcoded, never overridden)
    if any(w in intent_lower for w in ["steam", "epic", "game update", "install game"]):
        return "games"

    # Rule 2 — Vision triggers (explicit)
    if any(w in intent_lower for w in ["screen", "camera", "what do you see", "look at"]):
        return "vision"

    # Rule 3 — Active task continuation
    if context.get("active_skill"):
        return context["active_skill"]

    # Rule 4 — Sierra Leone / local context
    if any(w in intent_lower for w in ["sierra leone", "salone", "freetown", "krio", "local news"]):
        return "salone"

    # Rule 5 — Communication
    if any(w in intent_lower for w in ["send", "message", "whatsapp", "telegram", "remind", "tell "]):
        return "communication"

    # Rule 6 — Coding
    if any(w in intent_lower for w in ["code", "build", "script", "program", "debug",
                                        "fix error", "develop", "flutter", "python", "github"]):
        return "coding"

    # Rule 7 — File operations
    if any(w in intent_lower for w in ["file", "folder", "document", "organize", "desktop"]):
        return "file_ops"

    # Rule 8 — Media
    if any(w in intent_lower for w in ["play", "youtube", "watch", "video", "music"]):
        return "media"

    # Rule 9 — Hardware
    if any(w in intent_lower for w in ["cpu", "ram", "memory", "temperature", "battery", "performance"]):
        return "hardware"

    # Rule 10 — Intelligence / Deep research
    if any(w in intent_lower for w in ["research", "analyze", "summarize", "compare", "report"]):
        return "intelligence"

    # Rule 11 — Web/search
    if any(w in intent_lower for w in ["search", "find", "what is", "who is", "price",
                                        "news", "look up", "how do", "when is"]):
        return "web_intelligence"

    # Rule 12 — Memory
    if any(w in intent_lower for w in ["remember", "forget", "what do you know"]):
        return "memory_ops"

    # Rule 13 — System control
    if any(w in intent_lower for w in ["open", "close", "volume", "brightness", "wifi", "shutdown"]):
        return "system_control"

    # Default — web intelligence
    return "web_intelligence"


def select_model(task_complexity: str, is_private: bool, config: dict) -> str:
    """
    Select the best LLM for the task.
    ZOEY-inspired model routing by complexity.
    """
    if is_private:
        return "ollama"   # local-first for private data

    backend = config.get("llm_backend", "gemini")

    if task_complexity == "simple":
        return backend
    elif task_complexity == "complex":
        # Use best available
        if config.get("nvidia_api_key"):
            return "nvidia"
        return backend
    else:
        return backend


def assess_complexity(intent: str) -> str:
    """
    Estimate task complexity for model selection.
    """
    complex_signals = ["build", "develop", "full app", "multi-file", "architecture",
                       "analyze", "research", "compare", "generate report"]
    simple_signals  = ["open", "close", "volume", "weather", "play", "remind"]

    intent_lower = intent.lower()
    if any(s in intent_lower for s in complex_signals):
        return "complex"
    if any(s in intent_lower for s in simple_signals):
        return "simple"
    return "medium"
