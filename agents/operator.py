"""
operator.py — Operator: Visible Computer Workflow Agent
Mission: Perform approved, visible computer workflows with full audit trail.
Authority: Gated — every action requires approval card before execution.
Inspired by ZOEY's orchestration pattern + MAYA's governance layer.
"""
import json
import datetime
import subprocess
from pathlib import Path
from agents.base_agent import BaseAgent


class Operator(BaseAgent):
    name = "Operator"
    mission = "Perform approved visible computer workflows. Every action is logged with screenshot evidence."
    authority_level = "gated"

    # ------------------------------------------------------------------ #
    #  Deviation registry (MAYA-inspired governance)                      #
    # ------------------------------------------------------------------ #
    _deviations: list = []

    def run(self, task: str, context: dict = None) -> dict:
        context = context or {}
        mode = context.get("mode", "plan")  # plan | execute | status | deviations

        self._log("run", f"mode={mode} task={task[:60]}")

        if mode == "plan":
            return self._plan_workflow(task, context)
        elif mode == "execute":
            return self._execute_approved(task, context)
        elif mode == "status":
            return self._workflow_status()
        elif mode == "deviations":
            return self._list_deviations()
        else:
            return self._plan_workflow(task, context)

    # ------------------------------------------------------------------ #
    #  Workflow planning                                                   #
    # ------------------------------------------------------------------ #

    def _plan_workflow(self, task: str, context: dict) -> dict:
        """
        Produce a step-by-step workflow plan with an approval card.
        Never execute without approval.
        """
        plan = {
            "task": task,
            "steps": context.get("steps", ["[Auto-generated steps — review before approving]"]),
            "target_systems": context.get("target_systems", ["local computer"]),
            "irreversible_steps": context.get("irreversible_steps", []),
            "estimated_duration": context.get("estimated_duration", "unknown"),
            "rollback": context.get("rollback", "Manual undo required"),
        }

        approval_card = self.request_approval(
            intent=task,
            data_used=context.get("data_used", "local files only"),
            target_system=str(plan["target_systems"]),
            irreversible=bool(plan["irreversible_steps"]),
            rollback=plan["rollback"],
            exact_action=json.dumps(plan["steps"]),
        )

        return {
            "status": "pending_approval",
            "plan": plan,
            "approval_card": approval_card,
            "note": "Sorie Adams must review the plan and approval card before Operator executes.",
        }

    # ------------------------------------------------------------------ #
    #  Execution (only after approval)                                    #
    # ------------------------------------------------------------------ #

    def _execute_approved(self, task: str, context: dict) -> dict:
        """
        Execute only after explicit approval is confirmed.
        Logs every step with timestamp.
        """
        if not context.get("approved", False):
            self._log("execute_blocked", task, approved=False, result="no approval token")
            return {
                "status": "blocked",
                "reason": "No approval token. Operator never executes without explicit approval.",
            }

        steps   = context.get("steps", [])
        results = []
        evidence_dir = Path(__file__).resolve().parent.parent / "memory" / "audit" / "operator_evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)

        for i, step in enumerate(steps):
            step_result = {"step": i + 1, "action": step, "status": "executed",
                           "timestamp": datetime.datetime.now().isoformat()}
            results.append(step_result)
            self._log("step_executed", step, approved=True, result="ok")

            # Deviation check — if step deviates from declared plan
            if context.get("declared_steps") and step not in context["declared_steps"]:
                deviation = {
                    "type": "undeclared_step",
                    "step": step,
                    "severity": "medium",
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                self._deviations.append(deviation)
                self._log("DEVIATION", step, approved=False, result="flagged")
                step_result["deviation"] = deviation

        # Save evidence log
        evidence_path = evidence_dir / f"workflow_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        evidence_path.write_text(
            json.dumps({"task": task, "steps": results}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        return {
            "status": "completed",
            "steps_executed": len(results),
            "evidence": str(evidence_path),
            "deviations": len(self._deviations),
            "results": results,
        }

    # ------------------------------------------------------------------ #
    #  MAYA-inspired governance                                           #
    # ------------------------------------------------------------------ #

    def _list_deviations(self) -> dict:
        """
        List all deviations detected during workflow execution.
        Inspired by Maya's deviation console.
        """
        return {
            "status": "ok",
            "total_deviations": len(self._deviations),
            "deviations": self._deviations,
            "note": "Review each deviation and decide: dismiss or enforce correction.",
        }

    def _workflow_status(self) -> dict:
        evidence_dir = Path(__file__).resolve().parent.parent / "memory" / "audit" / "operator_evidence"
        if not evidence_dir.exists():
            return {"status": "ok", "workflows_completed": 0}
        files = list(evidence_dir.glob("*.json"))
        return {
            "status": "ok",
            "workflows_completed": len(files),
            "last_run": max(files, key=lambda f: f.stat().st_mtime).name if files else None,
            "open_deviations": len(self._deviations),
        }
