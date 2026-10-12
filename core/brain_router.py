"""
NISHA Brain Router — October 2026
Routes each agent to its assigned model. Handles failover chain. Tracks daily usage.
"""

import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, date

from core.model_registry import get_model, ModelSpec, Provider, Modality

logger = logging.getLogger("nisha.brain_router")

BRAINS_CONFIG = Path(__file__).parent.parent / "config" / "agent_brains.json"
USAGE_FILE    = Path(__file__).parent.parent / "memory" / "usage_tracker.json"


# ─────────────────────────────────────────────
# Usage tracker  (daily limit awareness)
# ─────────────────────────────────────────────
class UsageTracker:
    def __init__(self):
        self._data: Dict[str, Dict] = {}
        self._today = str(date.today())
        self._load()

    def _load(self):
        if USAGE_FILE.exists():
            try:
                raw = json.loads(USAGE_FILE.read_text())
                # Reset if stale day
                if raw.get("date") != self._today:
                    self._data = {"date": self._today, "counts": {}}
                else:
                    self._data = raw
            except Exception:
                self._data = {"date": self._today, "counts": {}}
        else:
            self._data = {"date": self._today, "counts": {}}

    def _save(self):
        USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        USAGE_FILE.write_text(json.dumps(self._data, indent=2))

    def increment(self, model_id: str):
        counts = self._data.setdefault("counts", {})
        counts[model_id] = counts.get(model_id, 0) + 1
        self._save()

    def get_count(self, model_id: str) -> int:
        return self._data.get("counts", {}).get(model_id, 0)

    def is_limit_reached(self, model: ModelSpec) -> bool:
        if model.daily_limit is None:
            return False
        used = self.get_count(model.model_id)
        # Leave 10% buffer
        return used >= int(model.daily_limit * 0.90)

    def status(self) -> Dict:
        return {
            "date": self._data.get("date"),
            "usage": self._data.get("counts", {})
        }


_tracker = UsageTracker()


# ─────────────────────────────────────────────
# Brain loader
# ─────────────────────────────────────────────
def _load_brains() -> Dict:
    return json.loads(BRAINS_CONFIG.read_text())


# ─────────────────────────────────────────────
# Core router
# ─────────────────────────────────────────────
class BrainRouter:
    """
    Routes agent calls to the right model.
    Respects: daily limits, privacy flag, speed flag, modality requirements.
    Failover chain: primary → fallback → fallback_nim → local
    """

    def __init__(self):
        self._config = _load_brains()
        self._agents = self._config["agents"]
        self._special = self._config["special"]
        self._rules   = self._config["routing_rules"]

    def get_brain(
        self,
        agent_name: str,
        *,
        private: bool = False,
        speed_critical: bool = False,
        required_modalities: Optional[List[str]] = None,
        force_tier: Optional[str] = None,   # "primary" | "fallback" | "local"
    ) -> Dict[str, Any]:
        """
        Returns a dict with: model_id, provider, base_url, api_key_env, display_name
        Ready to pass directly to an LLM client.
        """
        # Always use local for private tasks
        if private:
            return self._resolve_tier(agent_name, "local")

        # Speed burst — Cerebras if short task
        if speed_critical:
            spec = get_model("gpt-oss-120b")
            if spec and not _tracker.is_limit_reached(spec):
                logger.info(f"[BrainRouter] {agent_name} → SPEED BURST → Cerebras gpt-oss-120b")
                _tracker.increment(spec.model_id)
                return self._spec_to_dict(spec)

        if force_tier:
            return self._resolve_tier(agent_name, force_tier)

        # Normal failover chain
        for tier in ["primary", "fallback", "fallback_nim", "local"]:
            agent_cfg = self._agents.get(agent_name, {})
            tier_cfg  = agent_cfg.get(tier)
            if not tier_cfg:
                continue

            model_id = tier_cfg["model"]
            spec     = get_model(model_id)

            # Check daily limits
            if spec and _tracker.is_limit_reached(spec):
                logger.warning(f"[BrainRouter] {agent_name} {tier} limit reached ({model_id}), trying next tier")
                continue

            # Check modality requirements
            if required_modalities and spec:
                missing = [m for m in required_modalities if m not in [mod.value for mod in spec.modalities]]
                if missing:
                    logger.warning(f"[BrainRouter] {model_id} missing modalities {missing}, trying next tier")
                    continue

            logger.info(f"[BrainRouter] {agent_name} → {tier.upper()} → {model_id}")
            if spec:
                _tracker.increment(spec.model_id)
            return tier_cfg

        # Absolute last resort
        logger.error(f"[BrainRouter] All tiers exhausted for {agent_name}. Using openrouter/free.")
        return {
            "provider": "openrouter",
            "model": "openrouter/free",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key_env": "OPENROUTER_API_KEY",
        }

    def _resolve_tier(self, agent_name: str, tier: str) -> Dict:
        agent_cfg = self._agents.get(agent_name, {})
        tier_cfg  = agent_cfg.get(tier)
        if tier_cfg:
            logger.info(f"[BrainRouter] {agent_name} → FORCED {tier.upper()} → {tier_cfg['model']}")
            spec = get_model(tier_cfg["model"])
            if spec:
                _tracker.increment(spec.model_id)
            return tier_cfg
        # Fallback if tier not found
        return self.get_brain(agent_name)

    def _spec_to_dict(self, spec: ModelSpec) -> Dict:
        return {
            "provider":    spec.provider.value,
            "model":       spec.model_id,
            "base_url":    spec.base_url,
            "api_key_env": spec.api_key_env,
            "display_name": spec.display_name,
        }

    def get_tts_config(self) -> Dict:
        return self._special["tts"]

    def get_stt_config(self) -> Dict:
        return self._special["stt"]

    def get_live_config(self, extended_thinking: bool = False) -> Dict:
        cfg = self._special["voice_live"]
        model = cfg["fallback"] if extended_thinking else cfg["primary"]
        return {"model": model, "provider": cfg["provider"], "api_key_env": cfg["api_key_env"]}

    def get_speed_burst_config(self) -> Dict:
        return self._special["speed_burst"]

    def usage_status(self) -> Dict:
        return _tracker.status()

    def reload(self):
        """Hot-reload config without restart."""
        self._config = _load_brains()
        self._agents = self._config["agents"]
        self._special = self._config["special"]
        self._rules   = self._config["routing_rules"]
        logger.info("[BrainRouter] Config reloaded.")


# Singleton
_router: Optional[BrainRouter] = None

def get_router() -> BrainRouter:
    global _router
    if _router is None:
        _router = BrainRouter()
    return _router

def get_brain(agent_name: str, **kwargs) -> Dict:
    """Convenience function — call from any agent."""
    return get_router().get_brain(agent_name, **kwargs)


if __name__ == "__main__":
    router = BrainRouter()
    for agent in ["nisha", "scout", "asha", "mira", "operator"]:
        brain = router.get_brain(agent)
        print(f"{agent:10} → {brain.get('model')}")
    print("\nUsage:", router.usage_status())
