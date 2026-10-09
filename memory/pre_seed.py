"""
pre_seed.py — Pre-seed Sorie Adams' known context into NISHA's memory.
Run once during setup. Safe to re-run (idempotent).
"""
from memory.memory_manager import update_memory

def seed():
    update_memory({
        "identity": {
            "name":        {"value": "Sorie Adams Kamara"},
            "city":        {"value": "Freetown, Sierra Leone"},
            "role":        {"value": "IT Administrator, Information Systems student at IPAM"},
            "faith":       {"value": "Christian (Baptist) — Winners Baptist Church, BCSL"},
            "email":       {"value": "sorieadamskamara11@gmail.com"},
            "nationality": {"value": "Sierra Leonean"},
        },
        "projects": {
            "ai_assistant": {"value": "NISHA — personal agentic AI (this project)"},
            "wassce_app":   {"value": "WASSCE Prep App — AI-powered study platform for West Africa students"},
        },
        "preferences": {
            "stack":     {"value": "Flutter, Dart, Supabase, Python, Riverpod, GoRouter, Hive"},
            "ai_tools":  {"value": "Gemini API, NVIDIA API, GitHub CLI, Ollama"},
            "models":    {"value": "gemini-2.5-flash for reasoning and coding"},
            "address":   {"value": "Sorie Adams or Soriel Adams"},
        },
        "notes": {
            "machine": {"value": "Two Windows laptops: 12 GB RAM/500 GB and 24 GB RAM/256 GB, WSL2 Ubuntu"},
            "choir":   {"value": "Choir admin at Winners Baptist Church, BCSL"},
            "anchor":  {"value": "Isaiah 60:22 — At the right time, I, the Lord, will make it happen."},
        },
    })
    print("[PreSeed] ✅ Sorie Adams' context seeded into NISHA memory.")

if __name__ == "__main__":
    seed()
