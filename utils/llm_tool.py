"""
Utility functions for tools to use the enhanced LLM client with intelligent model selection.
"""
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

def llm_chat(
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict]] = None,
    temperature: float = 0.2,
    max_tokens: int = 150
) -> dict:
    """
    Chat with LLM using intelligent model selection.

    Args:
        messages: List of message dicts with 'role' and 'content'
        tools: Optional list of tool definitions for function calling
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens to generate

    Returns:
        Dict with 'content' and 'tool_calls' keys
    """
    # Import here to avoid circular dependencies
    try:
        from core.llm_client import call_llm
    except ImportError:
        # Fallback to direct import if needed
        sys.path.append(str(get_base_dir()))
        from core.llm_client import call_llm

    # Prepare the request
    payload_messages = []
    for msg in messages:
        payload_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Call the LLM
    result = call_llm(
        messages=payload_messages,
        tools=tools,
        timeout=30  # Reasonable timeout for tool operations
    )

    return result

def llm_text(
    prompt: str,
    system: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 500
) -> str:
    """
    Simple text generation using LLM.

    Args:
        prompt: The user prompt
        system: Optional system message
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text string
    """
    response = llm_chat(
        messages=[
            {"role": "system", "content": system}] if system else [] +
        [{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.get("content", "")

# Convenience function for quick queries
def quick_query(question: str, context: str = "") -> str:
    """
    Quick question answering with optional context.

    Args:
        question: The question to answer
        context: Optional background context

    Returns:
        Answer string
    """
    prompt = question
    if context:
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"

    return llm_text(
        prompt=prompt,
        system="You are a helpful AI assistant. Provide clear, concise, and accurate answers.",
        temperature=0.1,
        max_tokens=300
    )