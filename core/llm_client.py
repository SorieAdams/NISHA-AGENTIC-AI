"""
Local LLM client for NISHA.

Supports two backends — selected via  "llm_provider"  in config/api_keys.json:

  "llm_provider": "gemini"   (default)
        Uses Google's Gemini API.
        Get API key from: https://makersuite.google.com/

  "llm_provider": "nvidia"
        Uses NVIDIA API (via NVIDIA AI Foundations).
        Get API key from: https://build.nvidia.com/

Automatic failover: if the primary backend fails (e.g., quota exceeded, unavailable),
the client will automatically try the secondary backend.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Generator, Optional

import requests

# Matches a sentence boundary: [.!?] followed by whitespace, or a blank line.
# Avoids splitting on decimals (3.5) because those have no space after the dot.
_SENT_END = re.compile(r'(?<=[.!?])\s+|(?<=\n)\s*\n')


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR    = get_base_dir()
CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"


def _load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_llm_provider() -> str:
    """Returns 'gemini' or 'nvidia' based on configuration and availability."""
    config = _load_config()
    provider = config.get("llm_provider", "gemini").lower()
    if provider not in ("gemini", "nvidia"):
        # Fallback to gemini if invalid
        return "gemini"
    return provider


def get_llm_settings() -> tuple[str, str]:
    """Returns (base_url, model_name) for the selected provider."""
    provider = get_llm_provider()
    config = _load_config()

    if provider == "nvidia":
        url = config.get("nvidia_url", "https://integrate.api.nvidia.com/v1").rstrip("/")
        model = config.get("nvidia_model", "nemotron-3-22b-instruct-v1")
    else:  # gemini
        url = config.get("llm_url", "https://generativelanguage.googleapis.com/v1beta/models/").rstrip("/")
        model = config.get("llm_model", "gemini-2.5-flash")

    return url, model


def get_api_key(provider: str = None) -> str:
    """Get API key for the specified provider."""
    if provider is None:
        provider = get_llm_provider()
    config = _load_config()
    if provider == "nvidia":
        return config.get("nvidia_api_key", "")
    else:  # gemini
        return config.get("gemini_api_key", "")


def check_model_available(log: Callable | None = None) -> bool:
    """
    Always returns True for cloud APIs (no local model to check).
    Logs an informational message if logger provided.
    """
    if log:
        log("INFO: Using cloud API — no local model check needed.")
    return True


def _call_llm_provider(provider: str, messages: list, tools: list | None, timeout: int) -> dict:
    """Internal function to call a specific provider."""
    url, model = get_llm_settings_for_provider(provider)
    api_key = get_api_key(provider)

    if not api_key:
        raise RuntimeError(f"{provider.upper()} API key not configured")

    if provider == "nvidia":
        # NVIDIA API format (OpenAI-compatible)
        endpoint = f"{url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "max_tokens": 150,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            choice = data.get("choices", [{}])[0]
            msg = choice.get("message", {})
            # OpenAI tool_calls format → normalise to Ollama-style
            raw_tc  = msg.get("tool_calls") or []
            tc_list = [
                {
                    "id":       t.get("id", ""),
                    "function": {
                        "name":      t["function"]["name"],
                        "arguments": (
                            json.loads(t["function"]["arguments"])
                            if isinstance(t["function"].get("arguments"), str)
                            else t["function"].get("arguments", {})
                        ),
                    },
                }
                for t in raw_tc
            ]
            return {
                "content":    (msg.get("content") or "").strip(),
                "tool_calls": tc_list,
            }
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"NVIDIA API request failed: {e}") from e
    else:  # gemini
        # Google Gemini API format
        endpoint = f"{url}/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": m["content"]} for m in messages if m["role"] == "user"]}],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 150,
            },
        }
        if tools:
            # Convert tools to Gemini format (simplified)
            # This is a placeholder; actual implementation would need to map tools to Gemini's function calling.
            pass
        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            # Extract text from Gemini response
            text_parts = []
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "text" in part:
                        text_parts.append(part["text"])
            content = "\n".join(text_parts).strip()
            # Tool calls not implemented for Gemini in this simplified version
            return {
                "content": content,
                "tool_calls": [],
            }
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Gemini API request failed: {e}") from e


def get_llm_settings_for_provider(provider: str) -> tuple[str, str]:
    """Returns (base_url, model_name) for the given provider."""
    config = _load_config()
    if provider == "nvidia":
        url = config.get("nvidia_url", "https://integrate.api.nvidia.com/v1").rstrip("/")
        model = config.get("nvidia_model", "nemotron-3-22b-instruct-v1")
    else:  # gemini
        url = config.get("llm_url", "https://generativelanguage.googleapis.com/v1beta/models/").rstrip("/")
        model = config.get("llm_model", "gemini-2.5-flash")
    return url, model


def call_llm(
    messages: list,
    tools:    list | None = None,
    timeout:  int = 120,
) -> dict:
    """
    Unified LLM call for Gemini or NVIDIA with automatic failover.
    Tries the primary backend (from config), then the secondary on failure.
    Returns: {"content": str, "tool_calls": list}
    """
    primary = get_llm_provider()
    secondary = "nvidia" if primary == "gemini" else "gemini"
    last_error = None
    for provider in (primary, secondary):
        try:
            return _call_llm_provider(provider, messages, tools, timeout)
        except Exception as e:
            last_error = e
            # Optionally log the failure here if desired
            continue
    # If both fail, raise the last error
    raise last_error


def call_llm_stream(
    messages: list,
    tools:    list | None = None,
    timeout:  int = 120,
) -> Generator[dict, None, None]:
    """
    Streaming LLM call for Gemini or NVIDIA with automatic failover.
    For simplicity, we fall back to non-streaming and yield the whole response as one sentence.
    A full implementation would handle streaming properly with failover.
    """
    # For simplicity, we fall back to non-streaming and yield the whole response as one sentence.
    # A full implementation would handle streaming properly.
    primary = get_llm_provider()
    secondary = "nvidia" if primary == "gemini" else "gemini"
    last_error = None
    for provider in (primary, secondary):
        try:
            result = _call_llm_provider(provider, messages, tools, timeout)
            yield {"type": "sentence", "text": result["content"]}
            yield {"type": "done", "content": result["content"], "tool_calls": result["tool_calls"]}
            return
        except Exception as e:
            last_error = e
            continue
    # If both fail, raise the last error
    raise last_error


def ensure_model_loaded(model_name: str) -> bool:
    """Always returns True for cloud APIs."""
    return True


def warmup_model(system_prompt: str | None = None) -> bool:
    """Always returns True for cloud APIs."""
    return True


def get_current_loaded_model() -> Optional[str]:
    """Not applicable for cloud APIs."""
    return None


def set_current_loaded_model(model_name: Optional[str]) -> None:
    """No-op for cloud APIs."""
    pass


def maybe_unload_model() -> None:
    """No-op for cloud APIs."""
    pass