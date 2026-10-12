"""
scout.py — Scout: Research & Validation Agent
Mission: Find real problems, competitors, target users, opportunities.
Authority: Public web research only. No personal data shared externally.
"""
from agents.base_agent import BaseAgent
from core.brain_router import get_brain
from core.voice_manager import speak

from actions.web_search import web_search
from pathlib import Path
import json, datetime, sys

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()


class Scout(BaseAgent):
    name = "Scout"
    mission = "Find real problems, competitors, target users, and opportunities via public web research."
    authority_level = "read_only"

    def _get_brain(self):
        return get_brain("scout")

    BRIEF_TEMPLATE = {
        "problem": "",
        "evidence": [],
        "alternatives": [],
        "target_user": "",
        "interview_questions": [],
        "confidence": "",
        "source_links": [],
    }

    SCORECARD_TEMPLATE = {
        "idea": "",
        "user_pain": "",
        "target_user": "",
        "evidence": "",
        "demand": "",
        "feasibility": "",
        "launch_speed": "",
        "cost": "",
        "revenue_path": "",
        "risk": "",
        "next_test": "",
        "score": 0,
    }

    def run(self, task: str, context: dict = None) -> dict:
        context = context or {}
        mode = context.get("mode", "research")  # research | validate | compete | score

        self._log("run", f"mode={mode} task={task[:60]}")

        if mode == "research":
            return self._research_brief(task)
        elif mode == "validate":
            return self._validate_idea(task)
        elif mode == "compete":
            return self._competitor_analysis(task)
        elif mode == "score":
            return self._score_idea(task, context.get("idea_data", {}))
        else:
            return self._research_brief(task)

    def _research_brief(self, topic: str) -> dict:
        results = web_search(topic, mode="research")
        news    = web_search(f"{topic} latest news 2025", mode="news")
        brief   = dict(self.BRIEF_TEMPLATE)
        brief["problem"]     = topic
        brief["evidence"]    = [results.get("result", "")]
        brief["alternatives"]= [news.get("result", "")]
        brief["confidence"]  = "medium — based on public web search only"
        brief["source_links"]= results.get("sources", [])
        self._save_brief(topic, brief)
        self._log("research_brief", topic, result="saved")
        return {"status": "ok", "brief": brief}

    def _validate_idea(self, idea: str) -> dict:
        query = f"{idea} market demand user problem 2025"
        result = web_search(query, mode="research")
        comp   = web_search(f"{idea} competitors alternatives", mode="search")
        validation = {
            "idea": idea,
            "demand_evidence": result.get("result", ""),
            "competitors": comp.get("result", ""),
            "verdict": "Needs further validation with real users.",
            "next_step": "Talk to 3-5 target users directly.",
        }
        self._log("validate", idea, result="brief produced")
        return {"status": "ok", "validation": validation}

    def _competitor_analysis(self, market: str) -> dict:
        result = web_search(f"{market} competitors top products 2025", mode="compare")
        analysis = {
            "market": market,
            "competitors": result.get("result", ""),
            "gaps": "Review results above for underserved niches.",
        }
        self._log("compete", market, result="analysis done")
        return {"status": "ok", "analysis": analysis}

    def _score_idea(self, idea: str, idea_data: dict) -> dict:
        card = dict(self.SCORECARD_TEMPLATE)
        card["idea"] = idea
        card.update(idea_data)
        # Simple heuristic scoring (0-10)
        score = 0
        if idea_data.get("user_pain"): score += 2
        if idea_data.get("evidence"): score += 2
        if idea_data.get("revenue_path"): score += 2
        if idea_data.get("feasibility"): score += 2
        if idea_data.get("launch_speed"): score += 1
        if idea_data.get("next_test"): score += 1
        card["score"] = score
        self._save_scorecard(idea, card)
        self._log("score", idea, result=f"score={score}/10")
        return {"status": "ok", "scorecard": card}

    def _save_brief(self, topic: str, brief: dict) -> None:
        ideas_dir = BASE_DIR / "ideas"
        ideas_dir.mkdir(exist_ok=True)
        slug = topic[:30].replace(" ", "_").lower()
        path = ideas_dir / f"brief_{slug}_{datetime.date.today()}.json"
        path.write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")

    def _save_scorecard(self, idea: str, card: dict) -> None:
        ideas_dir = BASE_DIR / "ideas"
        ideas_dir.mkdir(exist_ok=True)
        slug = idea[:30].replace(" ", "_").lower()
        path = ideas_dir / f"score_{slug}_{datetime.date.today()}.json"
        path.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")
