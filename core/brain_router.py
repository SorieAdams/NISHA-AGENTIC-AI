"""
NISHA Brain Router — October 2026
Routes each agent to its assigned model. Handles 3-tier failover. Tracks daily usage.
"""
import json, logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import date

from core.model_registry import get_model, ModelSpec, Provider

logger = logging.getLogger("nisha.brain_router")

BRAINS_CONFIG = Path(__file__).parent.parent / "config" / "agent_brains.json"
USAGE_FILE    = Path(__file__).parent.parent / "memory"  / "usage_tracker.json"


class UsageTracker:
    def __init__(self):
        self._today = str(date.today())
        self._data: Dict = {}
        self._load()

    def _load(self):
        if USAGE_FILE.exists():
            try:
                raw = json.loads(USAGE_FILE.read_text())
                self._data = raw if raw.get("date") == self._today else {"date": self._today, "counts": {}}
            except Exception:
                self._data = {"date": self._today, "counts": {}}
        else:
            self._data = {"date": self._today, "counts": {}}

    def _save(self):
        USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        USAGE_FILE.write_text(json.dumps(self._data, indent=2))

    def increment(self, model_id: str):
        self._data.setdefault("counts", {})[model_id] = self._data["counts"].get(model_id, 0) + 1
        self._save()

    def is_limit_reached(self, model: ModelSpec) -> bool:
        if model.daily_limit is None:
            return False
        return self._data.get("counts", {}).get(model.model_id, 0) >= int(model.daily_limit * 0.90)

    def status(self) -> Dict:
        return {"date": self._data.get("date"), "usage": self._data.get("counts", {})}


_tracker = UsageTracker()


class BrainRouter:
    def __init__(self):
        cfg = json.loads(BRAINS_CONFIG.read_text())
        self._agents  = cfg["agents"]
        self._special = cfg["special"]

    def get_brain(self, agent_name: str, *, private: bool = False,
                  speed_critical: bool = False,
                  required_modalities: Optional[List[str]] = None,
                  force_tier: Optional[str] = None) -> Dict[str, Any]:
        # Always local for private tasks
        if private:
            return self._tier(agent_name, "local")

        # Cerebras speed burst
        if speed_critical:
            spec = get_model("gpt-oss-120b")
            if spec and not _tracker.is_limit_reached(spec):
                logger.info(f"[BrainRouter] {agent_name} → SPEED BURST → Cerebras")
                _tracker.increment(spec.model_id)
                return {"provider": spec.provider.value, "model": spec.model_id,
                        "base_url": spec.base_url, "api_key_env": spec.api_key_env}

        if force_tier:
            return self._tier(agent_name, force_tier)

        # Normal failover chain
        for tier in ["primary", "fallback", "fallback_nim", "local"]:
            cfg = self._agents.get(agent_name, {}).get(tier)
            if not cfg:
                continue
            spec = get_model(cfg["model"])
            if spec and _tracker.is_limit_reached(spec):
                logger.warning(f"[BrainRouter] {agent_name} {tier} limit reached, trying next")
                continue
            if required_modalities and spec:
                missing = [m for m in required_modalities if m not in [mod.value for mod in spec.modalities]]
                if missing:
                    logger.warning(f"[BrainRouter] {cfg['model']} missing modalities {missing}")
                    continue
            logger.info(f"[BrainRouter] {agent_name} → {tier.upper()} → {cfg['model']}")
            if spec:
                _tracker.increment(spec.model_id)
            return cfg

        logger.error(f"[BrainRouter] All tiers exhausted for {agent_name}")
        return {"provider": "openrouter", "model": "openrouter/free",
                "base_url": "https://openrouter.ai/api/v1", "api_key_env": "OPENROUTER_API_KEY"}

    def _tier(self, agent_name: str, tier: str) -> Dict:
        cfg = self._agents.get(agent_name, {}).get(tier)
        if cfg:
            spec = get_model(cfg["model"])
            if spec:
                _tracker.increment(spec.model_id)
            return cfg
        return self.get_brain(agent_name)

    def get_tts_config(self)  -> Dict: return self._special["tts"]
    def get_stt_config(self)  -> Dict: return self._special["stt"]
    def get_live_config(self, extended: bool = False) -> Dict:
        cfg = self._special["voice_live"]
        return {"model": cfg["fallback"] if extended else cfg["primary"],
                "provider": cfg["provider"], "api_key_env": cfg["api_key_env"]}
    def usage_status(self) -> Dict: return _tracker.status()


_router: Optional[BrainRouter] = None

def get_router() -> BrainRouter:
    global _router
    if _router is None:
        _router = BrainRouter()
    return _router

def get_brain(agent_name: str, **kwargs) -> Dict:
    """Convenience — call from any agent: brain = get_brain('asha')"""
    return get_router().get_brain(agent_name, **kwargs)


if __name__ == "__main__":
    router = BrainRouter()
    for agent in ["nisha", "scout", "asha", "mira", "operator"]:
        brain = router.get_brain(agent)
        print(f"  {agent:10} → {brain.get('model')}")
    print(f"\nUsage: {router.usage_status()}")
