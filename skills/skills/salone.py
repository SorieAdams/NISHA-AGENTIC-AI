"""
salone.py — Sierra Leone Skill
Tools: web_search (local mode), weather_report
Supports: local Sierra Leone news, Krio language context
"""
from actions.web_search import web_search
from actions.weather_report import weather_action

def handle(intent: str, context: dict) -> dict:
    if "weather" in intent:
        return weather_action("Freetown")
    if "krio" in intent.lower():
        return {"status": "ok", "message": "Krio support active. How can I help, na Salone way?"}
    return web_search(f"Sierra Leone {intent}", mode="news")
