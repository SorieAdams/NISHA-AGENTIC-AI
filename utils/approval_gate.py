"""
approval_gate.py — NISHA Approval Gate
Centralizes all approval logic. Any action requiring owner approval goes through here.
Produces approval cards. Logs decisions.
"""
import json
import datetime
from pathlib import Path
import sys

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()

# Actions always requiring approval
ALWAYS_APPROVE = [
    "send_email", "send_message", "publish", "submit", "post",
    "git_push", "delete_file", "delete_account",
    "payment", "purchase", "contract",
    "login", "mfa_bypass",
    "upload_personal_data", "share_with_third_party",
]

# Actions that may proceed with logging only
LOG_ONLY = [
    "web_search", "file_read", "memory_read", "local_draft",
    "local_file_write", "git_stage", "run_tests",
]


def requires_approval(action: str) -> bool:
    return any(a in action.lower() for a in ALWAYS_APPROVE)


def may_proceed(action: str) -> bool:
    return any(a in action.lower() for a in LOG_ONLY)


def create_approval_card(
    agent: str,
    intent: str,
    data_used: str,
    target_system: str,
    irreversible: bool,
    rollback: str,
    exact_action: str,
) -> dict:
    card = {
        "type":          "APPROVAL_REQUIRED",
        "agent":         agent,
        "intent":        intent,
        "data_used":     data_used,
        "target_system": target_system,
        "irreversible":  irreversible,
        "rollback":      rollback if not irreversible else "Cannot be undone",
        "exact_action":  exact_action,
        "timestamp":     datetime.datetime.now().isoformat(),
        "status":        "pending",
    }
    _log_card(card)
    return card


def approve(card: dict, owner_confirmed: bool = True) -> dict:
    card["status"]    = "approved" if owner_confirmed else "denied"
    card["decided_at"] = datetime.datetime.now().isoformat()
    _log_card(card)
    return card


def _log_card(card: dict) -> None:
    audit_dir = BASE_DIR / "memory" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    path = audit_dir / "approval_log.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(card, ensure_ascii=False) + "\n")
