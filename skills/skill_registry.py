"""
skill_registry.py — NISHA Skill Registry
All skills and their tool mappings, triggers, and handlers.
"""
from skills.skills import coding, research, productivity, creative, salone

SKILL_REGISTRY = {
    "system_control": {
        "tools": ["open_app", "computer_settings", "computer_control", "desktop_control"],
        "triggers": ["open", "close", "volume", "brightness", "wifi", "shutdown", "launch"],
        "handler": None,
    },
    "web_intelligence": {
        "tools": ["web_search", "browser_control", "flight_finder", "weather_report"],
        "triggers": ["search", "find", "what is", "who is", "price", "news", "look up", "research"],
        "handler": research.handle,
    },
    "media": {
        "tools": ["youtube_video", "file_processor"],
        "triggers": ["play", "youtube", "watch", "video", "music", "pause"],
        "handler": None,
    },
    "communication": {
        "tools": ["send_message", "reminder"],
        "triggers": ["send", "message", "whatsapp", "telegram", "remind", "tell"],
        "handler": None,
    },
    "vision": {
        "tools": ["screen_process", "close_camera"],
        "triggers": ["screen", "camera", "what do you see", "look at"],
        "handler": None,
    },
    "file_ops": {
        "tools": ["file_controller", "file_processor", "desktop_control"],
        "triggers": ["file", "folder", "document", "read", "delete", "organize"],
        "handler": productivity.handle,
    },
    "coding": {
        "tools": ["code_helper", "dev_agent", "browser_control"],
        "triggers": ["code", "build", "script", "program", "debug", "fix error", "develop"],
        "handler": coding.handle,
    },
    "intelligence": {
        "tools": ["web_search", "file_processor", "save_memory"],
        "triggers": ["analyze", "summarize", "compare", "report", "deep research"],
        "handler": research.handle,
    },
    "hardware": {
        "tools": ["system_status", "system_monitor"],
        "triggers": ["cpu", "ram", "memory", "temperature", "battery", "performance"],
        "handler": None,
    },
    "memory_ops": {
        "tools": ["save_memory", "load_memory"],
        "triggers": ["remember", "forget", "what do you know about"],
        "handler": None,
    },
    "salone": {
        "tools": ["web_search", "weather_report"],
        "triggers": ["sierra leone", "freetown", "krio", "salone", "local news"],
        "handler": salone.handle,
    },
    "games": {
        "tools": ["game_updater"],
        "triggers": ["steam", "epic", "game update", "install game"],
        "handler": None,
    },
    "agents": {
        "tools": ["scout", "asha", "mira", "operator"],
        "triggers": ["scout", "asha", "mira", "operator", "research agent", "code agent",
                     "career agent", "validate idea", "research idea"],
        "handler": None,
    },
}


def get_skill(name: str) -> dict:
    return SKILL_REGISTRY.get(name, SKILL_REGISTRY["web_intelligence"])


def get_all_skills() -> dict:
    return SKILL_REGISTRY
