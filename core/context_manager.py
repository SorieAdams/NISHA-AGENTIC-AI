# core/context_manager.py
# Session context tracking

class ContextManager:
    def __init__(self):
        self.context = {}
        self.active_skill = None
        self.last_user_speech = None
        self.active_project = None
        self.time_of_day = None

    def update(self, key, value):
        self.context[key] = value
        setattr(self, key, value)

    def get(self, key, default=None):
        return self.context.get(key, default)

    def clear_active_skill(self):
        self.active_skill = None

    def set_active_skill(self, skill):
        self.active_skill = skill

    def to_dict(self):
        return {
            "active_skill": self.active_skill,
            "last_user_speech": self.last_user_speech,
            "active_project": self.active_project,
            "time_of_day": self.time_of_day,
            **self.context
        }