"""
NISHA Model Registry — October 2026
All AI providers, models, capabilities, and limits declared here.
Single source of truth for brain_router.py
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Provider(str, Enum):
    GOOGLE     = "google"
    OPENROUTER = "openrouter"
    NVIDIA_NIM = "nvidia_nim"
    CEREBRAS   = "cerebras"
    OLLAMA     = "ollama"
    GROQ       = "groq"


class Modality(str, Enum):
    TEXT  = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    PDF   = "pdf"


@dataclass
class ModelSpec:
    model_id: str
    provider: Provider
    display_name: str
    context_window: int
    modalities: List[Modality]
    tool_calling: bool
    reasoning: bool
    free: bool
    daily_limit: Optional[int]
    rpm_limit: Optional[int]
    speed_tps: Optional[int]
    base_url: str
    api_key_env: Optional[str]
    notes: str = ""
    tags: List[str] = field(default_factory=list)


GOOGLE_MODELS = [
    ModelSpec("gemini-3.8-flash", Provider.GOOGLE, "Gemini 3.8 Flash", 1_000_000,
              [Modality.TEXT, Modality.IMAGE, Modality.VIDEO, Modality.AUDIO, Modality.PDF],
              True, True, True, 1500, 15, 150,
              "https://generativelanguage.googleapis.com/v1beta", "GEMINI_API_KEY",
              "Primary NISHA brain. 1M ctx, all modalities, tool calling.",
              ["orchestration", "multimodal", "long-context", "voice"]),
    ModelSpec("gemini-3.6-flash", Provider.GOOGLE, "Gemini 3.6 Flash", 1_000_000,
              [Modality.TEXT, Modality.IMAGE, Modality.VIDEO, Modality.AUDIO],
              True, True, True, 1500, 15, 120,
              "https://generativelanguage.googleapis.com/v1beta", "GEMINI_API_KEY",
              "Previous-gen Flash. Reliable fallback.", ["general", "multimodal", "fallback"]),
    ModelSpec("gemini-3.5-flash-lite", Provider.GOOGLE, "Gemini 3.5 Flash-Lite", 1_000_000,
              [Modality.TEXT, Modality.IMAGE], True, False, True, 4000, 30, 200,
              "https://generativelanguage.googleapis.com/v1beta", "GEMINI_API_KEY",
              "Fastest Gemini free tier. High throughput.", ["fast", "high-volume"]),
    ModelSpec("gemini-3.8-live", Provider.GOOGLE, "Gemini 3.8 Live", 1_000_000,
              [Modality.AUDIO, Modality.TEXT], True, False, True, 500, 10, None,
              "https://generativelanguage.googleapis.com/v1beta", "GEMINI_API_KEY",
              "Real-time audio-to-audio. Primary voice model.", ["voice", "live", "real-time"]),
    ModelSpec("gemini-3.8-live-extended-thinking", Provider.GOOGLE, "Gemini 3.8 Live Extended Thinking",
              1_000_000, [Modality.AUDIO, Modality.TEXT], True, True, True, 200, 5, None,
              "https://generativelanguage.googleapis.com/v1beta", "GEMINI_API_KEY",
              "High-reasoning live audio.", ["voice", "live", "reasoning"]),
    ModelSpec("gemini-3.8-flash-tts", Provider.GOOGLE, "Gemini 3.8 Flash TTS", 0,
              [Modality.TEXT], False, False, True, 1000, 10, None,
              "https://generativelanguage.googleapis.com/v1beta", "GEMINI_API_KEY",
              "Primary TTS. 30 prebuilt voices, 130 languages.", ["tts"]),
    ModelSpec("gemini-3.5-transcribe", Provider.GOOGLE, "Gemini 3.5 Transcribe", 0,
              [Modality.AUDIO], False, False, True, 500, 10, None,
              "https://generativelanguage.googleapis.com/v1beta", "GEMINI_API_KEY",
              "Primary STT. Speaker diarization, word timestamps.", ["stt"]),
]

OPENROUTER_MODELS = [
    ModelSpec("thinkingmachines/inkling:free", Provider.OPENROUTER, "Thinking Machines: Inkling",
              1_048_576, [Modality.TEXT, Modality.IMAGE, Modality.AUDIO],
              True, True, True, 200, 20, 80,
              "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
              "#1 ranked free model Oct 2026. 41B active / 975B total MoE.",
              ["top-ranked", "research", "multimodal", "long-context"]),
    ModelSpec("thinkingmachines/inkling-small:free", Provider.OPENROUTER, "Thinking Machines: Inkling Small",
              1_048_576, [Modality.TEXT, Modality.IMAGE, Modality.AUDIO],
              True, True, True, 200, 20, 140,
              "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
              "#2 ranked free model. 12B active / 276B MoE. Faster.", ["fast", "multimodal"]),
    ModelSpec("nvidia/nemotron-3-ultra-550b-a55b:free", Provider.OPENROUTER, "NVIDIA Nemotron 3 Ultra 550B",
              1_000_000, [Modality.TEXT], True, True, True, 200, 20, 40,
              "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
              "55B active / 550B total. Frontier reasoning.",
              ["frontier", "reasoning", "long-context"]),
    ModelSpec("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", Provider.OPENROUTER,
              "NVIDIA Nemotron 3 Nano Omni", 256_000,
              [Modality.TEXT, Modality.AUDIO, Modality.IMAGE, Modality.VIDEO],
              True, True, True, 200, 20, 120,
              "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
              "ONLY free model with text+audio+image+VIDEO.",
              ["multimodal", "video", "operator"]),
    ModelSpec("poolside/laguna-s-2.1:free", Provider.OPENROUTER, "Poolside: Laguna S 2.1",
              262_144, [Modality.TEXT], True, True, True, 200, 20, 90,
              "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
              "Best free coding model Oct 2026. 70.2% Terminal-Bench.",
              ["coding", "agentic-coding", "best-coding"]),
    ModelSpec("nvidia/nemotron-3-super-120b-a12b:free", Provider.OPENROUTER, "NVIDIA Nemotron 3 Super 120B",
              262_144, [Modality.TEXT], True, True, True, 200, 20, 60,
              "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
              "12B active / 120B. Multi-agent specialist.", ["multi-agent"]),
    ModelSpec("google/gemma-4-31b-it:free", Provider.OPENROUTER, "Google Gemma 4 31B",
              262_144, [Modality.TEXT, Modality.IMAGE, Modality.VIDEO],
              True, True, True, 200, 20, 70,
              "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
              "Google DeepMind dense model. Vision+video.", ["multimodal", "google"]),
    ModelSpec("inclusionai/ling-3.1-flash", Provider.OPENROUTER, "inclusionAI Ling 3.1 Flash",
              262_144, [Modality.TEXT], True, True, True, 200, 20, 100,
              "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
              "25B active / 560B. NO training on your data.", ["privacy"]),
    ModelSpec("openrouter/free", Provider.OPENROUTER, "OpenRouter Free Router",
              200_000, [Modality.TEXT], False, False, True, 200, 20, None,
              "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
              "Last-resort fallback.", ["fallback", "last-resort"]),
]

NVIDIA_NIM_MODELS = [
    ModelSpec("nvidia/nemotron-3-ultra-550b-a55b", Provider.NVIDIA_NIM, "NVIDIA Nemotron 3 Ultra 550B (NIM)",
              1_000_000, [Modality.TEXT], True, True, True, 1000, 100, 40,
              "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY",
              "Same model as OpenRouter but higher NIM daily limit.", ["frontier", "reasoning"]),
    ModelSpec("moonshotai/kimi-k3", Provider.NVIDIA_NIM, "Kimi K3 (Moonshot AI)",
              131_072, [Modality.TEXT], True, True, True, 1000, 100, 80,
              "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY",
              "Strong coding model. Asha fallback.", ["coding"]),
    ModelSpec("deepseek-ai/deepseek-v4.1-flash", Provider.NVIDIA_NIM, "DeepSeek V4.1 Flash",
              131_072, [Modality.TEXT], True, True, True, 1000, 100, 110,
              "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY",
              "DeepSeek coding/reasoning. Fast flash variant.", ["coding", "fast"]),
    ModelSpec("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", Provider.NVIDIA_NIM,
              "NVIDIA Nemotron 3 Nano Omni (NIM)", 256_000,
              [Modality.TEXT, Modality.AUDIO, Modality.IMAGE, Modality.VIDEO],
              True, True, True, 1000, 100, 120,
              "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY",
              "Full multimodal. Higher NIM limit for Operator.", ["multimodal", "video"]),
    ModelSpec("openai/gpt-oss-20b", Provider.NVIDIA_NIM, "OpenAI GPT-OSS 20B (NIM)",
              131_072, [Modality.TEXT], True, False, True, 1000, 100, 200,
              "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY",
              "OpenAI open weights on NIM. Fast general fallback.", ["fast", "fallback"]),
]

CEREBRAS_MODELS = [
    ModelSpec("gpt-oss-120b", Provider.CEREBRAS, "GPT-OSS 120B (Cerebras)",
              65_536, [Modality.TEXT], True, True, True, None, 30, 3000,
              "https://api.cerebras.ai/v1", "CEREBRAS_API_KEY",
              "World's fastest inference at 3,000 t/s. Speed-critical tasks.", ["fastest", "speed-burst"]),
    ModelSpec("qwen-3.8-27b", Provider.CEREBRAS, "Qwen 3.8 27B (Cerebras)",
              64_000, [Modality.TEXT], True, True, True, None, 30, 1850,
              "https://api.cerebras.ai/v1", "CEREBRAS_API_KEY",
              "1,850 t/s. Good reasoning.", ["fast", "reasoning"]),
]

OLLAMA_MODELS = [
    ModelSpec("qwen2.5:32b", Provider.OLLAMA, "Qwen 2.5 32B (Local)", 32_768,
              [Modality.TEXT], True, True, True, None, None, 15,
              "http://localhost:11434/v1", None, "Runs on 24GB RAM. Private.", ["local", "private"]),
    ModelSpec("llama3.2", Provider.OLLAMA, "Llama 3.2 (Local)", 131_072,
              [Modality.TEXT], False, False, True, None, None, 30,
              "http://localhost:11434/v1", None, "Scout local. Fast on 12GB RAM.", ["local", "private"]),
    ModelSpec("mistral:7b", Provider.OLLAMA, "Mistral 7B (Local)", 32_768,
              [Modality.TEXT], False, False, True, None, None, 35,
              "http://localhost:11434/v1", None, "Mira local fallback.", ["local", "private"]),
    ModelSpec("phi3:medium", Provider.OLLAMA, "Phi-3 Medium (Local)", 131_072,
              [Modality.TEXT], False, False, True, None, None, 40,
              "http://localhost:11434/v1", None, "Operator local fallback.", ["local", "private"]),
]

ALL_MODELS: List[ModelSpec] = GOOGLE_MODELS + OPENROUTER_MODELS + NVIDIA_NIM_MODELS + CEREBRAS_MODELS + OLLAMA_MODELS
_MODEL_MAP = {m.model_id: m for m in ALL_MODELS}

def get_model(model_id: str) -> Optional[ModelSpec]:
    return _MODEL_MAP.get(model_id)

def get_models_by_tag(tag: str) -> List[ModelSpec]:
    return [m for m in ALL_MODELS if tag in m.tags]

def get_free_models() -> List[ModelSpec]:
    return [m for m in ALL_MODELS if m.free]

def get_models_by_provider(provider: Provider) -> List[ModelSpec]:
    return [m for m in ALL_MODELS if m.provider == provider]

def get_models_with_modality(modality: Modality) -> List[ModelSpec]:
    return [m for m in ALL_MODELS if modality in m.modalities]

if __name__ == "__main__":
    print(f"Total models: {len(ALL_MODELS)}")
    print(f"Free models: {len(get_free_models())}")
    print(f"Video-capable: {[m.model_id for m in get_models_with_modality(Modality.VIDEO)]}")
    print(f"Coding models: {[m.model_id for m in get_models_by_tag('coding')]}")
