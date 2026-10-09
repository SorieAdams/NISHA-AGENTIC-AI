"""
core/context_manager.py — NISHA Session Context Manager
Tracks session state across turns for coherent multi-step tasks.
ZOEY-inspired: persistent context + real-time monitoring.
"""
import datetime
from typing import Optional


class ContextManager:
    """
    Tracks everything NISHA needs to remember within a session.
    Separate from long-term memory (memory_manager) and RAG (rag_memory).
    """

    def __init__(self):
        self.context: dict = {}
        self.active_skill: Optional[str] = None
        self.active_agent: Optional[str] = None
        self.last_user_speech: Optional[float] = None
        self.active_project: Optional[str] = None
        self.time_of_day: Optional[str] = None
        self.current_file: Optional[str] = None
        self.pending_approval: Optional[dict] = None
        self.session_start: str = datetime.datetime.now().isoformat()
        self._history: list = []   # Recent (intent, skill, result) tuples, max 20

    # ------------------------------------------------------------------ #
    #  Core context ops                                                   #
    # ------------------------------------------------------------------ #

    def update(self, key: str, value) -> None:
        self.context[key] = value
        if hasattr(self, key):
            setattr(self, key, value)

    def get(self, key: str, default=None):
        return self.context.get(key, default)

    def set_active_skill(self, skill: str) -> None:
        self.active_skill = skill
        self.context["active_skill"] = skill

    def clear_active_skill(self) -> None:
        self.active_skill = None
        self.context.pop("active_skill", None)

    def set_active_agent(self, agent: Optional[str]) -> None:
        self.active_agent = agent
        self.context["active_agent"] = agent

    def set_pending_approval(self, card: dict) -> None:
        self.pending_approval = card
        self.context["pending_approval"] = card

    def clear_pending_approval(self) -> None:
        self.pending_approval = None
        self.context.pop("pending_approval", None)

    # ------------------------------------------------------------------ #
    #  History                                                             #
    # ------------------------------------------------------------------ #

    def add_history(self, intent: str, skill: str, result: str) -> None:
        self._history.append({
            "intent": intent[:80],
            "skill":  skill,
            "result": result[:80],
            "ts":     datetime.datetime.now().isoformat(),
        })
        if len(self._history) > 20:
            self._history = self._history[-20:]

    def recent_history(self, n: int = 5) -> list:
        return self._history[-n:]

    # ------------------------------------------------------------------ #
    #  State machine helpers                                              #
    # ------------------------------------------------------------------ #

    def get_time_of_day(self) -> str:
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    # ------------------------------------------------------------------ #
    #  Serialization                                                       #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "active_skill":     self.active_skill,
            "active_agent":     self.active_agent,
            "last_user_speech": self.last_user_speech,
            "active_project":   self.active_project,
            "time_of_day":      self.get_time_of_day(),
            "current_file":     self.current_file,
            "pending_approval": self.pending_approval,
            "session_start":    self.session_start,
            **self.context,
        }
