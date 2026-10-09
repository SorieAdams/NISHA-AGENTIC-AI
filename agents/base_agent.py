"""
base_agent.py — Base class for all NISHA sub-agents.
Every sub-agent has: a mission, a memory scope, approval gates, and an audit trail.
"""
import json
import datetime
from pathlib import Path
from typing import Optional
import sys


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()


class BaseAgent:
    """
    Base class for all NISHA sub-agents.
    Sub-agents: Scout, Asha, Mira, Operator.
    """

    name: str = "BaseAgent"
    mission: str = ""
    authority_level: str = "read_only"   # read_only | sandbox | gated

    def __init__(self):
        self.audit_log = BASE_DIR / "memory" / "audit" / f"{self.name.lower()}_audit.jsonl"
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  Audit                                                               #
    # ------------------------------------------------------------------ #

    def _log(self, action: str, detail: str, approved: bool = True, result: str = "") -> None:
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": self.name,
            "action": action,
            "detail": detail,
            "approved": approved,
            "result": result,
        }
        with open(self.audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"[{self.name}] {action}: {detail[:80]}")

    # ------------------------------------------------------------------ #
    #  Approval gate                                                       #
    # ------------------------------------------------------------------ #

    def _requires_approval(self, action: str) -> bool:
        """
        Returns True if the action class requires explicit owner approval.
        Matches APPROVAL_POLICY.md.
        """
        ALWAYS_APPROVE = [
            "send", "publish", "submit", "post", "delete",
            "payment", "purchase", "contract", "login", "mfa",
            "upload_personal", "git_push",
        ]
        return any(k in action.lower() for k in ALWAYS_APPROVE)

    def request_approval(self, intent: str, data_used: str,
                         target_system: str, irreversible: bool,
                         rollback: str, exact_action: str) -> dict:
        """
        Return a structured approval card. Owner must confirm before execution.
        Never auto-approve irreversible or external-publish actions.
        """
        card = {
            "type": "APPROVAL_REQUEST",
            "agent": self.name,
            "intent": intent,
            "data_used": data_used,
            "target_system": target_system,
            "irreversible": irreversible,
            "rollback": rollback,
            "exact_action": exact_action,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        self._log("approval_requested", exact_action, approved=False)
        return card

    # ------------------------------------------------------------------ #
    #  Main run interface                                                  #
    # ------------------------------------------------------------------ #

    def run(self, task: str, context: Optional[dict] = None) -> dict:
        raise NotImplementedError(f"{self.name}.run() must be implemented.")
