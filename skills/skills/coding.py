"""
coding.py — Coding Skill
Tools: code_helper, dev_agent, browser_control (docs)
"""
from actions.code_helper import code_helper
from actions.dev_agent import dev_agent

def handle(intent: str, context: dict) -> dict:
    if any(w in intent for w in ["project", "app", "full", "multi-file", "build app"]):
        return dev_agent(description=intent)
    return code_helper(action="auto", description=intent)
