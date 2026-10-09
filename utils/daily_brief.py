"""
daily_brief.py — NISHA Daily Brief Generator
Produces morning brief, evening review, and weekly review.
Aligned with NISHA_SOUL.md spiritual rhythm.
"""
import datetime
from pathlib import Path
from typing import Optional
import sys


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()

ANCHOR_SCRIPTURE = "Isaiah 60:22 — \"At the right time, I, the Lord, will make it happen.\" (NLT)"

MORNING_PRAYER = (
    "Lord, guide Sorie Adams through this day. "
    "Let every task be done with integrity, every decision with wisdom, "
    "and every moment with gratitude. Amen."
)

EVENING_PRAYER = (
    "Lord, thank you for today. "
    "Help Sorie Adams rest well, reflect honestly, "
    "and wake ready for tomorrow. Amen."
)


def morning_brief(priorities: list = None, tasks: list = None, open_approvals: list = None) -> dict:
    today = datetime.date.today().strftime("%A, %d %B %Y")
    hour  = datetime.datetime.now().strftime("%H:%M")

    brief = {
        "type": "morning_brief",
        "date": today,
        "time": hour,
        "scripture": ANCHOR_SCRIPTURE,
        "prayer":    MORNING_PRAYER,
        "top_priorities": priorities or ["No priorities set — add them now."],
        "focus_blocks": [
            {"block": 1, "time": "09:00–11:00", "task": tasks[0] if tasks else "Most important task"},
            {"block": 2, "time": "14:00–16:00", "task": tasks[1] if len(tasks or []) > 1 else "Second priority"},
        ],
        "open_approvals": open_approvals or [],
        "reminder": "People are waiting for your success — honor that hope through faithful, steady work.",
    }
    _save_brief("morning", brief)
    return brief


def evening_review(completed: list = None, blockers: list = None, gratitude: str = "") -> dict:
    brief = {
        "type": "evening_review",
        "date": datetime.date.today().isoformat(),
        "completed": completed or [],
        "blockers": blockers or [],
        "gratitude": gratitude or "One thing I'm grateful for today.",
        "prayer": EVENING_PRAYER,
        "tomorrow_first_task": "Review morning brief and set top 3 priorities.",
    }
    _save_brief("evening", brief)
    return brief


def weekly_review() -> dict:
    review = {
        "type": "weekly_review",
        "week_of": datetime.date.today().isoformat(),
        "sections": [
            "1. Spiritual consistency — prayer, Scripture, Church attendance",
            "2. Relationships — Denisha, family, colleagues",
            "3. Health — sleep, exercise, meals",
            "4. Finances — income, spending, savings",
            "5. Product validation — evidence, user conversations",
            "6. Project progress — GitHub, code, MVP",
            "7. Career pipeline — opportunities, applications, follow-ups",
            "8. What to stop, continue, or simplify",
            "9. Next week plan — realistic for 8–12 hours",
        ],
        "scripture": ANCHOR_SCRIPTURE,
    }
    _save_brief("weekly", review)
    return review


def _save_brief(brief_type: str, data: dict) -> None:
    import json
    log_dir = BASE_DIR / "memory" / "daily_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{brief_type}_{datetime.date.today()}.json"
    path = log_dir / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def format_morning_brief(brief: dict) -> str:
    lines = [
        f"Good morning, Sorie Adams. Today is {brief['date']}.",
        "",
        f"📖 {brief['scripture']}",
        "",
        f"🙏 {brief['prayer']}",
        "",
        "Today's priorities:",
    ]
    for i, p in enumerate(brief["top_priorities"], 1):
        lines.append(f"  {i}. {p}")
    lines += [
        "",
        "Focus blocks:",
        f"  ▸ {brief['focus_blocks'][0]['time']} — {brief['focus_blocks'][0]['task']}",
        f"  ▸ {brief['focus_blocks'][1]['time']} — {brief['focus_blocks'][1]['task']}",
    ]
    if brief.get("open_approvals"):
        lines.append(f"\n⚠️  {len(brief['open_approvals'])} pending approval(s).")
    lines.append(f"\n💬 {brief['reminder']}")
    return "\n".join(lines)
