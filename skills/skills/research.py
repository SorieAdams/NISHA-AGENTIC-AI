"""
research.py — Research & Intelligence Skill
Tools: web_search (research mode), file_processor, save_memory
Uses Scout sub-agent for deep research tasks.
"""
from actions.web_search import web_search

def handle(intent: str, context: dict) -> dict:
    mode = "research" if "deep" in intent or "research" in intent else "search"
    return web_search(intent, mode=mode)
