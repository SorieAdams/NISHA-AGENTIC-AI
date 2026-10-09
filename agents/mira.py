"""
mira.py — Mira: Career & Admin Operations Agent
Mission: Manage career pipeline, draft applications, track opportunities.
Authority: Drafts and tracker updates only. Never sends without explicit approval.
"""
import json
import datetime
from pathlib import Path
from agents.base_agent import BaseAgent


class Mira(BaseAgent):
    name = "Mira"
    mission = "Career/admin operations — applications, resume, opportunity tracker, follow-ups."
    authority_level = "read_only"   # drafts only; sends require approval

    OPPORTUNITY_SCHEMA = {
        "id": "",
        "source": "",
        "role_or_client": "",
        "relevance": "",
        "date_found": "",
        "next_action": "",
        "follow_up": "",
        "outcome": "",
        "status": "open",
        "draft_path": None,
    }

    def run(self, task: str, context: dict = None) -> dict:
        context = context or {}
        mode = context.get("mode", "draft")

        self._log("run", f"mode={mode} task={task[:60]}")

        if mode == "draft_application":
            return self._draft_application(task, context)
        elif mode == "add_opportunity":
            return self._add_opportunity(context)
        elif mode == "list_opportunities":
            return self._list_opportunities(context.get("filter_status", "open"))
        elif mode == "interview_prep":
            return self._interview_prep(task, context)
        elif mode == "weekly_pipeline":
            return self._weekly_pipeline_summary()
        else:
            return self._draft_application(task, context)

    def _draft_application(self, role: str, context: dict) -> dict:
        """
        Draft a job/freelance application. NEVER send without approval.
        """
        drafts_dir = Path(__file__).resolve().parent.parent / "memory" / "career" / "drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)

        draft = {
            "role": role,
            "company": context.get("company", ""),
            "tone": context.get("tone", "professional and warm"),
            "highlights": context.get("highlights", [
                "IT Administrator experience",
                "Information Systems student at IPAM",
                "Flutter/Python/Supabase developer",
                "Christian faith and integrity",
            ]),
            "body": (
                f"Dear Hiring Team,\n\n"
                f"I am writing to express my interest in the {role} position. "
                f"As an IT Administrator and Information Systems student with hands-on "
                f"experience in Flutter, Python, and Supabase, I bring a strong technical "
                f"foundation combined with a servant-leadership mindset.\n\n"
                f"[Tailor this paragraph to the specific role and company.]\n\n"
                f"I would welcome the opportunity to discuss how I can contribute to your team.\n\n"
                f"Warm regards,\nSorie Adams Kamara"
            ),
            "status": "draft — NOT sent",
            "created": datetime.datetime.now().isoformat(),
        }

        slug = role[:20].replace(" ", "_").lower()
        path = drafts_dir / f"draft_{slug}_{datetime.date.today()}.json"
        path.write_text(json.dumps(draft, indent=2), encoding="utf-8")

        self._log("draft_application", role, result=f"draft saved at {path.name}")
        return {
            "status": "ok",
            "draft": draft,
            "saved_at": str(path),
            "note": "Draft saved. Sorie Adams must review and explicitly approve before any submission.",
        }

    def _add_opportunity(self, data: dict) -> dict:
        pipeline_dir = Path(__file__).resolve().parent.parent / "memory" / "career"
        pipeline_dir.mkdir(parents=True, exist_ok=True)
        pipeline_path = pipeline_dir / "pipeline.json"

        pipeline = []
        if pipeline_path.exists():
            try:
                pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
            except Exception:
                pipeline = []

        entry = dict(self.OPPORTUNITY_SCHEMA)
        entry.update(data)
        entry["id"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        entry["date_found"] = entry["date_found"] or datetime.date.today().isoformat()

        pipeline.append(entry)
        pipeline_path.write_text(json.dumps(pipeline, indent=2), encoding="utf-8")

        self._log("add_opportunity", entry.get("role_or_client", "unknown"), result="added to pipeline")
        return {"status": "ok", "entry": entry, "pipeline_count": len(pipeline)}

    def _list_opportunities(self, status_filter: str = "open") -> dict:
        pipeline_path = (
            Path(__file__).resolve().parent.parent / "memory" / "career" / "pipeline.json"
        )
        if not pipeline_path.exists():
            return {"status": "ok", "opportunities": [], "note": "No pipeline yet."}

        pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
        filtered = [o for o in pipeline if o.get("status") == status_filter] if status_filter != "all" else pipeline

        return {"status": "ok", "opportunities": filtered, "count": len(filtered)}

    def _interview_prep(self, role: str, context: dict) -> dict:
        prompts = [
            f"Tell me about yourself and why you're interested in {role}.",
            "Describe a technical challenge you solved recently.",
            "How do you handle tight deadlines or changing priorities?",
            "What are your strongest technical skills?",
            "Where do you see yourself in 3 years?",
            "What does integrity mean to you in a professional context?",
        ]
        return {
            "status": "ok",
            "role": role,
            "interview_questions": prompts,
            "tip": "Practice your answers aloud. Nisha can coach you through each one.",
        }

    def _weekly_pipeline_summary(self) -> dict:
        result = self._list_opportunities("all")
        opps = result.get("opportunities", [])
        open_count    = sum(1 for o in opps if o.get("status") == "open")
        applied_count = sum(1 for o in opps if o.get("status") == "applied")
        followed_up   = sum(1 for o in opps if o.get("follow_up"))
        return {
            "status": "ok",
            "summary": {
                "total": len(opps),
                "open": open_count,
                "applied": applied_count,
                "followed_up": followed_up,
                "needs_action": [o for o in opps if not o.get("next_action")],
            },
        }
