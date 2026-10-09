"""
Utilities package for Nisha AI assistant.
"""
from .llm_tool import llm_chat, llm_text, quick_query
from .connectivity import (
    is_internet_available,
    is_fcc_server_running,
    get_effective_llm_mode,
    should_use_online_model,
    clear_connectivity_cache
)

__all__ = [
    # LLM utilities
    "llm_chat",
    "llm_text",
    "quick_query",

    # Connectivity utilities
    "is_internet_available",
    "is_fcc_server_running",
    "get_effective_llm_mode",
    "should_use_online_model",
    "clear_connectivity_cache"
]