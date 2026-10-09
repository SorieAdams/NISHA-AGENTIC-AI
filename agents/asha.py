"""
asha.py — Asha: Coding & GitHub Agent
Mission: Build, test, and maintain product code for Sorie Adams.
Authority: Sandbox/repo changes only. No external publishing without explicit approval.
"""
import subprocess
import json
import datetime
from pathlib import Path
from agents.base_agent import BaseAgent


class Asha(BaseAgent):
    name = "Asha"
    mission = "Build, test, and maintain product code. Propose changes; never push without approval."
    authority_level = "sandbox"

    def run(self, task: str, context: dict = None) -> dict:
        context = context or {}
        mode = context.get("mode", "plan")  # plan | write | test | review | issue | diff

        self._log("run", f"mode={mode} task={task[:60]}")

        if mode == "plan":
            return self._plan(task, context)
        elif mode == "issue":
            return self._create_issue(task, context)
        elif mode == "diff":
            return self._show_diff(context.get("path", "."))
        elif mode == "review":
            return self._review_code(context.get("file_path", ""), task)
        elif mode == "test":
            return self._run_tests(context.get("path", "."))
        else:
            return self._plan(task, context)

    def _plan(self, feature: str, context: dict) -> dict:
        """Produce a structured implementation plan."""
        plan = {
            "feature": feature,
            "steps": [
                f"1. Understand requirement: {feature}",
                "2. Identify affected files and modules",
                "3. Write tests first (TDD where practical)",
                "4. Implement in a branch/sandbox",
                "5. Review diff before any commit",
                "6. Request approval before git push",
            ],
            "files_likely_affected": context.get("files", ["TBD — run diff after implementation"]),
            "approval_required_before": "git push, external publish",
            "note": "Asha proposes code changes. Sorie Adams approves before any push.",
        }
        self._log("plan", feature, result="plan produced")
        return {"status": "ok", "plan": plan}

    def _create_issue(self, title: str, context: dict) -> dict:
        """
        Creates a local issue record. Does NOT open GitHub issues without approval.
        """
        issues_dir = Path(__file__).resolve().parent.parent / "memory" / "issues"
        issues_dir.mkdir(parents=True, exist_ok=True)
        issue = {
            "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "title": title,
            "body": context.get("body", ""),
            "labels": context.get("labels", []),
            "status": "open",
            "created": datetime.datetime.now().isoformat(),
            "agent": "Asha",
            "approval_to_push": False,
        }
        path = issues_dir / f"issue_{issue['id']}.json"
        path.write_text(json.dumps(issue, indent=2), encoding="utf-8")
        self._log("create_issue", title, result=f"saved locally at {path.name}")
        return {
            "status": "ok",
            "issue": issue,
            "note": "Issue saved locally. Sorie Adams must approve before opening on GitHub.",
        }

    def _show_diff(self, path: str) -> dict:
        """Show current git diff for review."""
        try:
            result = subprocess.run(
                ["git", "diff", "--stat"],
                capture_output=True, text=True, cwd=path, timeout=15
            )
            diff = subprocess.run(
                ["git", "diff"],
                capture_output=True, text=True, cwd=path, timeout=15
            )
            return {
                "status": "ok",
                "stat": result.stdout,
                "diff": diff.stdout[:3000] + ("..." if len(diff.stdout) > 3000 else ""),
                "note": "Review diff above. Approval required before git push.",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _review_code(self, file_path: str, instructions: str) -> dict:
        """Read a file and return a review structure."""
        try:
            content = Path(file_path).read_text(encoding="utf-8")
            return {
                "status": "ok",
                "file": file_path,
                "lines": len(content.splitlines()),
                "review_instructions": instructions,
                "content_preview": content[:1500],
                "note": "Asha has read the file. Full LLM review occurs in next Nisha turn.",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _run_tests(self, path: str) -> dict:
        """Run pytest in sandbox mode."""
        if self._requires_approval("external"):
            pass  # tests are local, fine to run
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=short", "-q"],
                capture_output=True, text=True, cwd=path, timeout=60
            )
            return {
                "status": "ok" if result.returncode == 0 else "failed",
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-500:],
            }
        except FileNotFoundError:
            return {"status": "error", "error": "pytest not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
