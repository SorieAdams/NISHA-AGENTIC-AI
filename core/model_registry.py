"""
NISHA Model Registry — October 2026
All AI providers, models, capabilities, limits declared here.
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
    daily_limit: Optional[int]           # None = unlimited (local)
    rpm_limit: Optional[int]             # requests per minute
    speed_tps: Optional[int]             # tokens per second estimate
    base_url: str
    api_key_env: Optional[str]
    notes: str = ""
    tags: List[str] = field(default_factory=list)


# ─────────────────────────────────────────────
# GOOGLE GEMINI  (free tier, no billing needed)
# ─────────────────────────────────────────────
GOOGLE_MODELS = [
    ModelSpec(
        model_id       = "gemini-3.8-flash",
        provider       = Provider.GOOGLE,
        display_name   = "Gemini 3.8 Flash",
        context_window = 1_000_000,
        modalities     = [Modality.TEXT, Modality.IMAGE, Modality.VIDEO, Modality.AUDIO, Modality.PDF],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 1500,
        rpm_limit      = 15,
        speed_tps      = 150,
        base_url       = "https://generativelanguage.googleapis.com/v1beta",
        api_key_env    = "GEMINI_API_KEY",
        notes          = "Primary NISHA brain. 1M ctx, all modalities, tool calling. Best free model for orchestration.",
        tags           = ["orchestration", "multimodal", "long-context", "voice"],
    ),
    ModelSpec(
        model_id       = "gemini-3.6-flash",
        provider       = Provider.GOOGLE,
        display_name   = "Gemini 3.6 Flash",
        context_window = 1_000_000,
        modalities     = [Modality.TEXT, Modality.IMAGE, Modality.VIDEO, Modality.AUDIO],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 1500,
        rpm_limit      = 15,
        speed_tps      = 120,
        base_url       = "https://generativelanguage.googleapis.com/v1beta",
        api_key_env    = "GEMINI_API_KEY",
        notes          = "Previous-gen Flash. Reliable fallback for Mira and general tasks.",
        tags           = ["general", "multimodal", "fallback"],
    ),
    ModelSpec(
        model_id       = "gemini-3.5-flash-lite",
        provider       = Provider.GOOGLE,
        display_name   = "Gemini 3.5 Flash-Lite",
        context_window = 1_000_000,
        modalities     = [Modality.TEXT, Modality.IMAGE],
        tool_calling   = True,
        reasoning      = False,
        free           = True,
        daily_limit    = 4000,
        rpm_limit      = 30,
        speed_tps      = 200,
        base_url       = "https://generativelanguage.googleapis.com/v1beta",
        api_key_env    = "GEMINI_API_KEY",
        notes          = "Fastest Gemini free tier. High throughput. Good for quick tasks.",
        tags           = ["fast", "high-volume", "fallback"],
    ),
    ModelSpec(
        model_id       = "gemini-3.8-live",
        provider       = Provider.GOOGLE,
        display_name   = "Gemini 3.8 Live",
        context_window = 1_000_000,
        modalities     = [Modality.AUDIO, Modality.TEXT],
        tool_calling   = True,
        reasoning      = False,
        free           = True,
        daily_limit    = 500,
        rpm_limit      = 10,
        speed_tps      = None,
        base_url       = "https://generativelanguage.googleapis.com/v1beta",
        api_key_env    = "GEMINI_API_KEY",
        notes          = "Real-time audio-to-audio. Primary voice model for NISHA live conversation.",
        tags           = ["voice", "live", "real-time"],
    ),
    ModelSpec(
        model_id       = "gemini-3.8-live-extended-thinking",
        provider       = Provider.GOOGLE,
        display_name   = "Gemini 3.8 Live Extended Thinking",
        context_window = 1_000_000,
        modalities     = [Modality.AUDIO, Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 5,
        speed_tps      = None,
        base_url       = "https://generativelanguage.googleapis.com/v1beta",
        api_key_env    = "GEMINI_API_KEY",
        notes          = "High-reasoning live audio. Use when voice needs deep thinking.",
        tags           = ["voice", "live", "reasoning"],
    ),
    ModelSpec(
        model_id       = "gemini-3.8-flash-tts",
        provider       = Provider.GOOGLE,
        display_name   = "Gemini 3.8 Flash TTS",
        context_window = 0,
        modalities     = [Modality.TEXT],
        tool_calling   = False,
        reasoning      = False,
        free           = True,
        daily_limit    = 1000,
        rpm_limit      = 10,
        speed_tps      = None,
        base_url       = "https://generativelanguage.googleapis.com/v1beta",
        api_key_env    = "GEMINI_API_KEY",
        notes          = "Primary TTS. 30 prebuilt voices, 130 languages, studio-grade fidelity.",
        tags           = ["tts", "voice-output"],
    ),
    ModelSpec(
        model_id       = "gemini-3.5-transcribe",
        provider       = Provider.GOOGLE,
        display_name   = "Gemini 3.5 Transcribe",
        context_window = 0,
        modalities     = [Modality.AUDIO],
        tool_calling   = False,
        reasoning      = False,
        free           = True,
        daily_limit    = 500,
        rpm_limit      = 10,
        speed_tps      = None,
        base_url       = "https://generativelanguage.googleapis.com/v1beta",
        api_key_env    = "GEMINI_API_KEY",
        notes          = "Primary STT. Speaker diarization, word timestamps, language auto-detect.",
        tags           = ["stt", "transcription"],
    ),
]

# ─────────────────────────────────────────────
# OPENROUTER  (free tier: 200 req/day, 20 RPM)
# ─────────────────────────────────────────────
OPENROUTER_MODELS = [
    ModelSpec(
        model_id       = "thinkingmachines/inkling:free",
        provider       = Provider.OPENROUTER,
        display_name   = "Thinking Machines: Inkling",
        context_window = 1_048_576,
        modalities     = [Modality.TEXT, Modality.IMAGE, Modality.AUDIO],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = 80,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "#1 ranked free model Oct 2026. 41B active / 975B total MoE. General reasoning, coding, agentic.",
        tags           = ["top-ranked", "research", "orchestration", "multimodal", "long-context"],
    ),
    ModelSpec(
        model_id       = "thinkingmachines/inkling-small:free",
        provider       = Provider.OPENROUTER,
        display_name   = "Thinking Machines: Inkling Small",
        context_window = 1_048_576,
        modalities     = [Modality.TEXT, Modality.IMAGE, Modality.AUDIO],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = 140,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "#2 ranked free model. 12B active / 276B MoE. Faster sibling of Inkling.",
        tags           = ["fast", "multimodal", "long-context"],
    ),
    ModelSpec(
        model_id       = "nvidia/nemotron-3-ultra-550b-a55b:free",
        provider       = Provider.OPENROUTER,
        display_name   = "NVIDIA Nemotron 3 Ultra 550B",
        context_window = 1_000_000,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = 40,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "55B active / 550B total. Frontier reasoning + orchestration. Also on NVIDIA NIM.",
        tags           = ["frontier", "reasoning", "orchestration", "long-context"],
    ),
    ModelSpec(
        model_id       = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        provider       = Provider.OPENROUTER,
        display_name   = "NVIDIA Nemotron 3 Nano Omni",
        context_window = 256_000,
        modalities     = [Modality.TEXT, Modality.AUDIO, Modality.IMAGE, Modality.VIDEO],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = 120,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "ONLY free model with text+audio+image+VIDEO. Perfect for screen/UI understanding.",
        tags           = ["multimodal", "video", "operator", "screen"],
    ),
    ModelSpec(
        model_id       = "poolside/laguna-s-2.1:free",
        provider       = Provider.OPENROUTER,
        display_name   = "Poolside: Laguna S 2.1",
        context_window = 262_144,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = 90,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "Best free coding model Oct 2026. 8B active / 118B total. 70.2% Terminal-Bench 2.1.",
        tags           = ["coding", "agentic-coding", "best-coding"],
    ),
    ModelSpec(
        model_id       = "nvidia/nemotron-3-super-120b-a12b:free",
        provider       = Provider.OPENROUTER,
        display_name   = "NVIDIA Nemotron 3 Super 120B",
        context_window = 262_144,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = 60,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "12B active / 120B. Multi-agent specialist.",
        tags           = ["multi-agent", "orchestration"],
    ),
    ModelSpec(
        model_id       = "nvidia/nemotron-3.5-lightning:free",
        provider       = Provider.OPENROUTER,
        display_name   = "NVIDIA Nemotron 3.5 Lightning",
        context_window = 1_000_000,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = False,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = 250,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "3B active / 30B. High-throughput fast tasks. 1M context.",
        tags           = ["fast", "high-throughput", "long-context"],
    ),
    ModelSpec(
        model_id       = "google/gemma-4-31b-it:free",
        provider       = Provider.OPENROUTER,
        display_name   = "Google Gemma 4 31B",
        context_window = 262_144,
        modalities     = [Modality.TEXT, Modality.IMAGE, Modality.VIDEO],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = 70,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "Google DeepMind dense model. Vision + video. Good general fallback.",
        tags           = ["multimodal", "google", "vision"],
    ),
    ModelSpec(
        model_id       = "inclusionai/ling-3.1-flash",
        provider       = Provider.OPENROUTER,
        display_name   = "inclusionAI Ling 3.1 Flash",
        context_window = 262_144,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = 100,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "25B active / 560B MoE. NO training on your data. Privacy-friendly cloud option.",
        tags           = ["privacy", "reasoning"],
    ),
    ModelSpec(
        model_id       = "openrouter/free",
        provider       = Provider.OPENROUTER,
        display_name   = "OpenRouter Free Router",
        context_window = 200_000,
        modalities     = [Modality.TEXT],
        tool_calling   = False,
        reasoning      = False,
        free           = True,
        daily_limit    = 200,
        rpm_limit      = 20,
        speed_tps      = None,
        base_url       = "https://openrouter.ai/api/v1",
        api_key_env    = "OPENROUTER_API_KEY",
        notes          = "Rotates randomly among free models. Last-resort fallback only.",
        tags           = ["fallback", "last-resort"],
    ),
]

# ─────────────────────────────────────────────
# NVIDIA NIM  (free: ~1,000 req/day, high RPM)
# ─────────────────────────────────────────────
NVIDIA_NIM_MODELS = [
    ModelSpec(
        model_id       = "nvidia/nemotron-3-ultra-550b-a55b",
        provider       = Provider.NVIDIA_NIM,
        display_name   = "NVIDIA Nemotron 3 Ultra 550B (NIM)",
        context_window = 1_000_000,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 1000,
        rpm_limit      = 100,
        speed_tps      = 40,
        base_url       = "https://integrate.api.nvidia.com/v1",
        api_key_env    = "NVIDIA_API_KEY",
        notes          = "Same model as OpenRouter but higher daily limit on NIM.",
        tags           = ["frontier", "reasoning", "long-context"],
    ),
    ModelSpec(
        model_id       = "moonshotai/kimi-k3",
        provider       = Provider.NVIDIA_NIM,
        display_name   = "Kimi K3 (Moonshot AI)",
        context_window = 131_072,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 1000,
        rpm_limit      = 100,
        speed_tps      = 80,
        base_url       = "https://integrate.api.nvidia.com/v1",
        api_key_env    = "NVIDIA_API_KEY",
        notes          = "Strong coding model. Asha fallback.",
        tags           = ["coding", "reasoning"],
    ),
    ModelSpec(
        model_id       = "deepseek-ai/deepseek-v4.1-flash",
        provider       = Provider.NVIDIA_NIM,
        display_name   = "DeepSeek V4.1 Flash",
        context_window = 131_072,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 1000,
        rpm_limit      = 100,
        speed_tps      = 110,
        base_url       = "https://integrate.api.nvidia.com/v1",
        api_key_env    = "NVIDIA_API_KEY",
        notes          = "DeepSeek coding/reasoning. Fast flash variant.",
        tags           = ["coding", "fast"],
    ),
    ModelSpec(
        model_id       = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
        provider       = Provider.NVIDIA_NIM,
        display_name   = "NVIDIA Nemotron 3 Nano Omni (NIM)",
        context_window = 256_000,
        modalities     = [Modality.TEXT, Modality.AUDIO, Modality.IMAGE, Modality.VIDEO],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = 1000,
        rpm_limit      = 100,
        speed_tps      = 120,
        base_url       = "https://integrate.api.nvidia.com/v1",
        api_key_env    = "NVIDIA_API_KEY",
        notes          = "Full multimodal. Higher NIM limit for Operator agent.",
        tags           = ["multimodal", "video", "operator"],
    ),
    ModelSpec(
        model_id       = "openai/gpt-oss-20b",
        provider       = Provider.NVIDIA_NIM,
        display_name   = "OpenAI GPT-OSS 20B (NIM)",
        context_window = 131_072,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = False,
        free           = True,
        daily_limit    = 1000,
        rpm_limit      = 100,
        speed_tps      = 200,
        base_url       = "https://integrate.api.nvidia.com/v1",
        api_key_env    = "NVIDIA_API_KEY",
        notes          = "OpenAI open weights on NIM. Fast, reliable general fallback.",
        tags           = ["fast", "general", "fallback"],
    ),
]

# ─────────────────────────────────────────────
# CEREBRAS  (free tier: 65K ctx, ~3,000 t/s)
# ─────────────────────────────────────────────
CEREBRAS_MODELS = [
    ModelSpec(
        model_id       = "gpt-oss-120b",
        provider       = Provider.CEREBRAS,
        display_name   = "GPT-OSS 120B (Cerebras)",
        context_window = 65_536,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = None,
        rpm_limit      = 30,
        speed_tps      = 3000,
        base_url       = "https://api.cerebras.ai/v1",
        api_key_env    = "CEREBRAS_API_KEY",
        notes          = "World's fastest inference at 3,000 t/s. Use for speed-critical short tasks only. 65K ctx on free.",
        tags           = ["fastest", "speed-burst"],
    ),
    ModelSpec(
        model_id       = "qwen-3.8-27b",
        provider       = Provider.CEREBRAS,
        display_name   = "Qwen 3.8 27B (Cerebras)",
        context_window = 64_000,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = None,
        rpm_limit      = 30,
        speed_tps      = 1850,
        base_url       = "https://api.cerebras.ai/v1",
        api_key_env    = "CEREBRAS_API_KEY",
        notes          = "1,850 t/s. Good reasoning. Cerebras only has 2 models on free shared inference.",
        tags           = ["fast", "reasoning"],
    ),
]

# ─────────────────────────────────────────────
# OLLAMA  (local, unlimited, private)
# ─────────────────────────────────────────────
OLLAMA_MODELS = [
    ModelSpec(
        model_id       = "qwen2.5:32b",
        provider       = Provider.OLLAMA,
        display_name   = "Qwen 2.5 32B (Local)",
        context_window = 32_768,
        modalities     = [Modality.TEXT],
        tool_calling   = True,
        reasoning      = True,
        free           = True,
        daily_limit    = None,
        rpm_limit      = None,
        speed_tps      = 15,
        base_url       = "http://localhost:11434/v1",
        api_key_env    = None,
        notes          = "Runs on 24GB RAM. Primary local for NISHA and Asha. Fully private.",
        tags           = ["local", "private", "offline"],
    ),
    ModelSpec(
        model_id       = "llama3.2",
        provider       = Provider.OLLAMA,
        display_name   = "Llama 3.2 (Local)",
        context_window = 131_072,
        modalities     = [Modality.TEXT],
        tool_calling   = False,
        reasoning      = False,
        free           = True,
        daily_limit    = None,
        rpm_limit      = None,
        speed_tps      = 30,
        base_url       = "http://localhost:11434/v1",
        api_key_env    = None,
        notes          = "Scout local fallback. Fast on 12GB RAM machine.",
        tags           = ["local", "private", "fast-local"],
    ),
    ModelSpec(
        model_id       = "mistral:7b",
        provider       = Provider.OLLAMA,
        display_name   = "Mistral 7B (Local)",
        context_window = 32_768,
        modalities     = [Modality.TEXT],
        tool_calling   = False,
        reasoning      = False,
        free           = True,
        daily_limit    = None,
        rpm_limit      = None,
        speed_tps      = 35,
        base_url       = "http://localhost:11434/v1",
        api_key_env    = None,
        notes          = "Mira local fallback. Lightweight drafting model.",
        tags           = ["local", "private", "drafting"],
    ),
    ModelSpec(
        model_id       = "phi3:medium",
        provider       = Provider.OLLAMA,
        display_name   = "Phi-3 Medium (Local)",
        context_window = 131_072,
        modalities     = [Modality.TEXT],
        tool_calling   = False,
        reasoning      = False,
        free           = True,
        daily_limit    = None,
        rpm_limit      = None,
        speed_tps      = 40,
        base_url       = "http://localhost:11434/v1",
        api_key_env    = None,
        notes          = "Operator local fallback. Efficient on 12GB RAM.",
        tags           = ["local", "private"],
    ),
]

# ─────────────────────────────────────────────
# MASTER REGISTRY
# ─────────────────────────────────────────────
ALL_MODELS: List[ModelSpec] = (
    GOOGLE_MODELS +
    OPENROUTER_MODELS +
    NVIDIA_NIM_MODELS +
    CEREBRAS_MODELS +
    OLLAMA_MODELS
)

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
    print(f"Total models in registry: {len(ALL_MODELS)}")
    print(f"Free models: {len(get_free_models())}")
    print(f"Models with video: {[m.model_id for m in get_models_with_modality(Modality.VIDEO)]}")
    print(f"Coding models: {[m.model_id for m in get_models_by_tag('coding')]}")
