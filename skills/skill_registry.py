# skills/skill_registry.py
# Registry of all declared skills

SKILL_REGISTRY = {
    "system_control": {
        "tools": ["computer_settings", "computer_control", "open_app", "desktop_control"],
        "triggers": ["open", "close", "volume up", "shutdown"]
    },
    "web_intelligence": {
        "tools": ["web_search", "browser_control", "flight_finder", "weather_report"],
        "triggers": ["search", "find", "what is", "look up"]
    },
    "media": {
        "tools": ["youtube_video", "file_processor"],
        "triggers": ["play", "watch", "pause", "summarize video"]
    },
    "communication": {
        "tools": ["send_message", "reminder"],
        "triggers": ["send", "message", "remind me", "tell X"]
    },
    "vision": {
        "tools": ["screen_process", "close_camera"],
        "triggers": ["what do you see", "look at screen", "camera"]
    },
    "file_ops": {
        "tools": ["file_controller", "file_processor", "desktop_control"],
        "triggers": ["open file", "read", "organize", "delete"]
    },
    "coding": {
        "tools": ["code_helper", "dev_agent", "browser_control"],
        "triggers": ["write code", "build", "run", "fix", "explain"]
    },
    "intelligence": {
        "tools": ["web_search", "file_processor", "save_memory"],
        "triggers": ["research", "analyze", "summarize", "compare"]
    },
    "hardware": {
        "tools": ["system_status", "system_monitor"],
        "triggers": ["CPU", "RAM", "temperature", "how's my computer"]
    },
    "memory_ops": {
        "tools": ["save_memory", "load_memory"],
        "triggers": ["remember", "forget", "what do you know about"]
    },
    "saloone": {
        "tools": ["web_search", "weather_report"],
        "triggers": ["local Sierra Leone news", "Krio language support"]
    },
    "games": {
        "tools": ["game_updater"],
        "triggers": ["Steam", "Epic", "game update", "install game"]
    }
}

def get_skill_tools(skill_name):
    """Return the list of tools for a given skill."""
    return SKILL_REGISTRY.get(skill_name, {}).get("tools", [])

def get_skill_triggers(skill_name):
    """Return the list of triggers for a given skill."""
    return SKILL_REGISTRY.get(skill_name, {}).get("triggers", [])