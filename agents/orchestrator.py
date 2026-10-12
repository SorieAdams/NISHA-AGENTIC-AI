"""
orchestrator.py — NISHA Multi-Agent Orchestrator
Inspired by ZOEY's orchestration pattern.
Nisha delegates tasks to Scout, Asha, Mira, and Operator.
Tracks agent identity, coordination, and audit trail (MAYA-inspired).
"""
import json
import datetime
from pathlib import Path
from typing import Optional
import sys

from agents.scout import Scout
from agents.asha import Asha
from agents.mira import Mira
from agents.operator import Operator
from core.brain_router import get_brain, get_router
from core.voice_manager import get_voice_manager



def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()


class NishaOrchestrator:
    """
    The orchestration brain.
    ZOEY-inspired: multi-agent coordination, delegation, audit.
    MAYA-inspired: agent identity tracking, deviation logging, governance.
    """

    AGENT_REGISTRY = {
        "scout":    Scout,
        "asha":     Asha,
        "mira":     Mira,
        "operator": Operator,
    }

    # Agent identity declarations (MAYA-inspired AID concept)
    AGENT_DECLARATIONS = {
        "scout":    {"allowed_providers": ["web_search", "duckduckgo"], "allowed_reach": "public_web"},
        "asha":     {"allowed_providers": ["local_fs", "git", "pytest"],  "allowed_reach": "sandbox_only"},
        "mira":     {"allowed_providers": ["local_fs"],                   "allowed_reach": "local_only"},
        "operator": {"allowed_providers": ["local_fs", "approved_tools"], "allowed_reach": "gated"},
    }

    def __init__(self):
        self._agents: dict = {}
        self._active_workflows: list = []
        self._audit_path = BASE_DIR / "memory" / "audit" / "orchestrator_audit.jsonl"
        self._audit_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  Agent lifecycle                                                     #
    # ------------------------------------------------------------------ #

    def _get_agent(self, name: str):
        name = name.lower()
        if name not in self.AGENT_REGISTRY:
            raise ValueError(f"Unknown agent: {name}. Available: {list(self.AGENT_REGISTRY)}")
        if name not in self._agents:
            self._agents[name] = self.AGENT_REGISTRY[name]()
        return self._agents[name]

    # ------------------------------------------------------------------ #
    #  Delegation                                                         #
    # ------------------------------------------------------------------ #

    def delegate(self, agent_name: str, task: str, context: dict = None) -> dict:
        """
        Delegate a task to a named sub-agent.
        Logs the delegation with timestamp and agent identity.
        """
        context = context or {}
        self._log_delegation(agent_name, task)

        try:
            agent = self._get_agent(agent_name)
            result = agent.run(task, context)
            self._log_result(agent_name, task, result.get("status", "unknown"))
            return result
        except Exception as e:
            self._log_result(agent_name, task, f"ERROR: {e}")
            return {"status": "error", "agent": agent_name, "error": str(e)}

    def delegate_parallel(self, tasks: list[dict]) -> list[dict]:
        """
        Delegate multiple tasks across agents simultaneously.
        ZOEY-inspired multi-agent coordination.
        tasks: [{"agent": "scout", "task": "...", "context": {...}}, ...]
        """
        import threading
        results = [None] * len(tasks)

        def _run(i, t):
            results[i] = self.delegate(t["agent"], t["task"], t.get("context", {}))

        threads = [threading.Thread(target=_run, args=(i, t)) for i, t in enumerate(tasks)]
        for th in threads: th.start()
        for th in threads: th.join()

        return results

    # ------------------------------------------------------------------ #
    #  Smart routing — Nisha describes a task, orchestrator picks agent  #
    # ------------------------------------------------------------------ #

    def route(self, task: str, context: dict = None) -> dict:
        """
        Automatically pick the right agent for a task.
        """
        task_lower = task.lower()

        if any(w in task_lower for w in ["research", "validate", "competitor", "market", "find problem", "score idea"]):
            return self.delegate("scout", task, context)

        if any(w in task_lower for w in ["code", "build", "fix", "test", "github", "issue", "diff", "branch"]):
            return self.delegate("asha", task, context)

        if any(w in task_lower for w in ["job", "career", "apply", "resume", "cv", "opportunity", "interview", "application"]):
            return self.delegate("mira", task, context)

        if any(w in task_lower for w in ["execute", "workflow", "computer task", "automate", "perform"]):
            return self.delegate("operator", task, context)

        # Default: Scout for general intelligence tasks
        return self.delegate("scout", task, context)

    # ------------------------------------------------------------------ #
    #  Status & governance                                                 #
    # ------------------------------------------------------------------ #

    def status(self) -> dict:
        """
        Return the current state of all agents.
        MAYA-inspired: visibility into every active agent.
        """
        active = list(self._agents.keys())
        deviations = []
        for name, agent in self._agents.items():
            if hasattr(agent, "_deviations"):
                for d in agent._deviations:
                    deviations.append({**d, "agent": name})

        return {
            "active_agents": active,
            "agent_declarations": self.AGENT_DECLARATIONS,
            "open_deviations": deviations,
            "total_deviations": len(deviations),
            "active_workflows": self._active_workflows,
        }

    def get_deviations(self) -> list:
        all_deviations = []
        for name, agent in self._agents.items():
            if hasattr(agent, "_deviations"):
                for d in agent._deviations:
                    all_deviations.append({**d, "agent": name})
        return all_deviations

    # ------------------------------------------------------------------ #
    #  Audit                                                               #
    # ------------------------------------------------------------------ #

    def _log_delegation(self, agent: str, task: str) -> None:
        entry = {
            "type": "delegation",
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent,
            "task": task[:100],
            "declared_providers": self.AGENT_DECLARATIONS.get(agent, {}).get("allowed_providers", []),
        }
        with open(self._audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[Orchestrator] → {agent}: {task[:50]}")

    def _log_result(self, agent: str, task: str, status: str) -> None:
        entry = {
            "type": "result",
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent,
            "task": task[:100],
            "status": status,
        }
        with open(self._audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


# Singleton
_orchestrator = None

def get_orchestrator() -> NishaOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = NishaOrchestrator()
    return _orchestrator
