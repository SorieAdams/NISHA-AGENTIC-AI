import requests
import socket
import time
from typing import Optional
from pathlib import Path
import sys

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

# Cache for connectivity checks to avoid excessive network calls
_connectivity_cache = {
    "internet_available": None,
    "internet_checked_at": 0,
    "fcc_server_running": None,
    "fcc_checked_at": 0,
}
_CACHE_DURATION = 5  # seconds

def is_internet_available() -> bool:
    """Check if we have internet connectivity by trying to reach reliable endpoints."""
    global _connectivity_cache

    now = time.time()
    if (now - _connectivity_cache["internet_checked_at"]) < _CACHE_DURATION:
        return _connectivity_cache["internet_available"]

    # Try multiple reliable endpoints
    test_urls = [
        "https://8.8.8.8",  # Google DNS
        "https://1.1.1.1",  # Cloudflare DNS
        "https://github.com",  # GitHub
        "https://google.com",  # Google
    ]

    for url in test_urls:
        try:
            # Try to establish a connection (HTTP HEAD request)
            response = requests.head(url, timeout=3)
            if response.status_code < 400:
                _connectivity_cache["internet_available"] = True
                _connectivity_cache["internet_checked_at"] = now
                return True
        except Exception:
            continue

    _connectivity_cache["internet_available"] = False
    _connectivity_cache["internet_checked_at"] = now
    return False

def is_fcc_server_running() -> bool:
    """Check if the fcc-server is running and accessible."""
    global _connectivity_cache

    now = time.time()
    if (now - _connectivity_cache["fcc_checked_at"]) < _CACHE_DURATION:
        return _connectivity_cache["fcc_server_running"]

    try:
        # Try to reach the health endpoint of fcc-server
        response = requests.get("http://localhost:8082/health", timeout=3)
        if response.status_code == 200:
            _connectivity_cache["fcc_server_running"] = True
            _connectivity_cache["fcc_checked_at"] = now
            return True
    except Exception:
        pass

    # Try alternative endpoints that might exist
    try:
        response = requests.get("http://localhost:8082", timeout=3)
        if response.status_code < 500:  # Any response that's not server error
            _connectivity_cache["fcc_server_running"] = True
            _connectivity_cache["fcc_checked_at"] = now
            return True
    except Exception:
        pass

    _connectivity_cache["fcc_server_running"] = False
    _connectivity_cache["fcc_checked_at"] = now
    return False

def get_effective_llm_mode() -> str:
    """Return 'online' or 'offline' based on connectivity and server status."""
    if is_internet_available() and is_fcc_server_running():
        return "online"
    return "offline"

def should_use_online_model(prefer_when_available: bool = True) -> bool:
    """Determine if we should use the online/proxy model."""
    if not prefer_when_available:
        return False
    return get_effective_llm_mode() == "online"

def clear_connectivity_cache():
    """Clear the connectivity cache (useful for testing or forced refresh)."""
    global _connectivity_cache
    _connectivity_cache = {
        "internet_available": None,
        "internet_checked_at": 0,
        "fcc_server_running": None,
        "fcc_checked_at": 0,
    }

# For testing purposes
if __name__ == "__main__":
    print("Internet available:", is_internet_available())
    print("FCC server running:", is_fcc_server_running())
    print("Effective LLM mode:", get_effective_llm_mode())
    print("Should use online model:", should_use_online_model())