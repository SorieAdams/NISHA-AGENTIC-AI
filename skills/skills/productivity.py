"""
productivity.py — Productivity Skill
Tools: reminder, file_controller, memory
"""
from actions.reminder import reminder as set_reminder
from actions.file_controller import file_controller

def handle(intent: str, context: dict) -> dict:
    if "remind" in intent:
        return {"status": "needs_params", "message": "Please provide date, time, and reminder message."}
    if "file" in intent or "folder" in intent:
        return file_controller(action="list", path="documents")
    return {"status": "ok", "message": "Productivity skill ready. What would you like to do?"}
