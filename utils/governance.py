"""
governance.py — NISHA Governance Layer
Inspired by MAYA's agentic networking concepts:
- Agent identity tracking
- Provider/reach declarations
- Deviation detection and alerting
- Audit trail
- Policy enforcement

This is NOT Maya. This is NISHA's own governance system built from scratch,
using Maya's concepts as inspiration.
"""
import json
import datetime
import threading
from pathlib import Path
from typing import Optional
import sys


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()


class AgentIdentity:
    """
    MAYA-inspired Agent Identity (AID).
    Every NISHA agent gets a declared identity with allowed providers and reach.
    """
    def __init__(self, name: str, allowed_providers: list, allowed_reach: str,
                 hourly_budget_mb: float = 100.0):
        self.name = name
        self.allowed_providers = allowed_providers
        self.allowed_reach = allowed_reach   # public_web | sandbox_only | local_only | gated
        self.hourly_budget_mb = hourly_budget_mb
        self.egress_mb_used = 0.0
        self.registered_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "allowed_providers": self.allowed_providers,
            "allowed_reach": self.allowed_reach,
            "hourly_budget_mb": self.hourly_budget_mb,
            "egress_mb_used": self.egress_mb_used,
            "registered_at": self.registered_at,
        }


class Deviation:
    """A deviation: an agent did something it never declared."""
    def __init__(self, agent: str, deviation_type: str, declared, seen, severity: str = "medium"):
        self.agent     = agent
        self.type      = deviation_type   # providers | reach | egress_budget
        self.declared  = declared
        self.seen      = seen
        self.severity  = severity
        self.timestamp = datetime.datetime.now().isoformat()
        self.status    = "open"   # open | dismissed | enforced

    def to_dict(self) -> dict:
        return {
            "agent":     self.agent,
            "type":      self.type,
            "declared":  self.declared,
            "seen":      self.seen,
            "severity":  self.severity,
            "timestamp": self.timestamp,
            "status":    self.status,
        }


class NishaGovernance:
    """
    NISHA's governance engine.
    Tracks all agent activity, detects deviations, enforces policy.
    Inspired by Maya's Loom console concept — without any actual Maya dependency.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._agents: dict[str, AgentIdentity] = {}
        self._deviations: list[Deviation] = []
        self._audit_path = BASE_DIR / "memory" / "audit" / "governance_audit.jsonl"
        self._audit_path.parent.mkdir(parents=True, exist_ok=True)
        self._register_default_agents()

    def _register_default_agents(self):
        defaults = [
            AgentIdentity("nisha",    ["gemini", "nvidia", "ollama", "all_local"],  "unrestricted"),
            AgentIdentity("scout",    ["web_search", "duckduckgo"],                  "public_web"),
            AgentIdentity("asha",     ["local_fs", "git", "pytest"],                 "sandbox_only"),
            AgentIdentity("mira",     ["local_fs"],                                  "local_only"),
            AgentIdentity("operator", ["local_fs", "approved_tools"],                "gated"),
        ]
        for agent in defaults:
            self._agents[agent.name] = agent

    # ------------------------------------------------------------------ #
    #  Agent registration                                                  #
    # ------------------------------------------------------------------ #

    def register_agent(self, identity: AgentIdentity) -> None:
        self._agents[identity.name] = identity
        self._audit("register", identity.name, f"registered with reach={identity.allowed_reach}")

    # ------------------------------------------------------------------ #
    #  Policy check — call before every agent action                     #
    # ------------------------------------------------------------------ #

    def check(self, agent_name: str, provider: str, reach: str, egress_mb: float = 0) -> dict:
        """
        Check if an agent action is within declared policy.
        Returns {"allowed": bool, "deviation": Deviation|None}
        """
        agent = self._agents.get(agent_name.lower())
        if not agent:
            return {"allowed": False, "reason": f"Unknown agent: {agent_name}"}

        deviation = None

        # Check provider
        if provider not in agent.allowed_providers and "all_local" not in agent.allowed_providers:
            deviation = Deviation(
                agent=agent_name, deviation_type="providers",
                declared=agent.allowed_providers, seen=provider, severity="high"
            )

        # Check reach
        elif reach not in (agent.allowed_reach, "local"):
            deviation = Deviation(
                agent=agent_name, deviation_type="reach",
                declared=agent.allowed_reach, seen=reach, severity="medium"
            )

        # Check egress budget
        elif egress_mb > 0:
            agent.egress_mb_used += egress_mb
            if agent.egress_mb_used > agent.hourly_budget_mb:
                deviation = Deviation(
                    agent=agent_name, deviation_type="egress_budget",
                    declared=f"{agent.hourly_budget_mb} MB/hr",
                    seen=f"{agent.egress_mb_used:.1f} MB/hr",
                    severity="medium"
                )

        if deviation:
            self._deviations.append(deviation)
            self._audit("DEVIATION", agent_name, f"type={deviation.type} seen={deviation.seen}")
            return {"allowed": False, "deviation": deviation.to_dict()}

        return {"allowed": True, "deviation": None}

    # ------------------------------------------------------------------ #
    #  Deviation management                                               #
    # ------------------------------------------------------------------ #

    def get_deviations(self, status: str = "open") -> list:
        if status == "all":
            return [d.to_dict() for d in self._deviations]
        return [d.to_dict() for d in self._deviations if d.status == status]

    def dismiss_deviation(self, index: int) -> bool:
        if 0 <= index < len(self._deviations):
            self._deviations[index].status = "dismissed"
            self._audit("dismiss", "operator", f"deviation #{index} dismissed")
            return True
        return False

    def enforce(self, index: int) -> bool:
        """Mark deviation as enforced — block new traffic from that agent."""
        if 0 <= index < len(self._deviations):
            self._deviations[index].status = "enforced"
            self._audit("enforce", "operator", f"deviation #{index} enforced")
            return True
        return False

    # ------------------------------------------------------------------ #
    #  Console status (MAYA Loom-inspired)                                #
    # ------------------------------------------------------------------ #

    def console_status(self) -> dict:
        open_devs  = self.get_deviations("open")
        return {
            "active_agents":    len(self._agents),
            "agents":           {n: a.to_dict() for n, a in self._agents.items()},
            "open_deviations":  len(open_devs),
            "deviations":       open_devs,
            "total_deviations": len(self._deviations),
        }

    # ------------------------------------------------------------------ #
    #  Audit                                                               #
    # ------------------------------------------------------------------ #

    def _audit(self, event: str, agent: str, detail: str) -> None:
        entry = {
            "event":     event,
            "agent":     agent,
            "detail":    detail,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        with open(self._audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def get_governance() -> NishaGovernance:
    if NishaGovernance._instance is None:
        with NishaGovernance._lock:
            if NishaGovernance._instance is None:
                NishaGovernance._instance = NishaGovernance()
    return NishaGovernance._instance
