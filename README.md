# NISHA — Ultimate Agentic AI

> *"At the right time, I, the Lord, will make it happen."* — Isaiah 60:22 (NLT)

**Owner:** Sorie Adams Kamara  
**Status:** Active Build — v0.2

---

## What is NISHA?

NISHA is not a chatbot. She is a **cross-platform personal agentic AI** — voice-first, screen-aware, memory-persistent, and capable of autonomous action with a strong ethical charter.

She is Sorie Adams' warm, direct **chief of staff and thinking partner**: rooted in Christian faith, built for real productivity, and designed to protect what matters most.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NISHA CORE                              │
│   Soul (NISHA_SOUL.md) · Voice · HUD (PyQt6) · Memory          │
├─────────────────────────────────────────────────────────────────┤
│                   ORCHESTRATION LAYER                           │
│   NishaOrchestrator → Scout · Asha · Mira · Operator           │
│   Multi-agent delegation · Parallel task execution              │
├─────────────────────────────────────────────────────────────────┤
│                   GOVERNANCE LAYER                              │
│   NishaGovernance · Agent Identity (AID) · Deviation Detection  │
│   Audit Trail · Approval Gates · Policy Enforcement             │
├─────────────────────────────────────────────────────────────────┤
│                   MEMORY SYSTEM                                 │
│   Long-term (JSON) · RAG/Vector (TF-IDF) · Vault (encrypted)   │
│   Episodic History · Career · Audit Logs                        │
├─────────────────────────────────────────────────────────────────┤
│                   SKILL ROUTER (12 skills)                      │
│   system · web · media · comms · vision · files                 │
│   coding · intelligence · hardware · memory · salone · games    │
├─────────────────────────────────────────────────────────────────┤
│                   TOOLS (21 real tools)                         │
│   web_search · browser_control · computer_control               │
│   file_controller · code_helper · dev_agent · send_message      │
│   reminder · screen_process · youtube_video · weather_report    │
│   system_monitor · computer_settings · desktop_control          │
│   flight_finder · game_updater · file_processor · save_memory   │
├─────────────────────────────────────────────────────────────────┤
│                   LLM BACKENDS                                  │
│   Gemini Flash (primary) → NVIDIA API → Ollama (offline)        │
├─────────────────────────────────────────────────────────────────┤
│               CLOUD / REMOTE DASHBOARD                          │
│   FastAPI · WebSocket · Phone UI · QR Auth                      │
│   Deploy: Railway · Render · Docker                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sub-Agent Roster

| Agent | Mission | Authority |
|---|---|---|
| **Nisha** | Orchestrate, plan, remember, delegate, protect values | Read + planning by default |
| **Scout** | Research problems, validate ideas, competitor analysis | Public web research only |
| **Asha** | Build, test, and maintain code | Sandbox/repo; no push without approval |
| **Mira** | Career pipeline, draft applications, opportunity tracker | Drafts + local tracker only |
| **Operator** | Execute approved visible computer workflows | Fully gated — approval required |

---

## Governance (MAYA-inspired)

Every agent has a declared **identity** with:
- Allowed **providers** (which APIs it may call)
- Allowed **reach** (public_web / sandbox / local / gated)
- **Egress budget** (MB/hr limit)

When an agent does something it never declared → **deviation fires**:
```
Type: providers | reach | egress_budget
Severity: high | medium | low
Status: open → dismissed | enforced
```

Check governance status at any time:
```python
from utils.governance import get_governance
print(get_governance().console_status())
```

---

## Memory System

| Store | Purpose | Encrypted |
|---|---|---|
| `long_term.json` | Identity, preferences, projects, relationships | No |
| `rag_store.json` | Episodic history — retrieved by similarity | No |
| `vault/.nisha_vault.enc` | Credentials, API keys, secrets | ✅ Yes |
| `audit/*.jsonl` | Every agent action, approval, deviation | No |
| `career/pipeline.json` | Job/opportunity tracker | No |
| `daily_logs/` | Morning brief, evening review, weekly review | No |

---

## Project Structure

```
nisha/
├── NISHA_SOUL.md          # Soul & Operating Charter
├── APPROVAL_POLICY.md     # Approval rules for all agents
├── MEMORY_SCHEMA.md       # Full memory architecture
├── main.py                # Core loop — LLM, audio, tool dispatch
├── ui.py                  # PyQt6 HUD
├── setup.py               # First-run wizard
├── agents/
│   ├── orchestrator.py    # Multi-agent orchestrator
│   ├── scout.py           # Research & validation agent
│   ├── asha.py            # Coding & GitHub agent
│   ├── mira.py            # Career & admin agent
│   └── operator.py        # Computer workflow agent
├── utils/
│   ├── governance.py      # Agent governance & deviation detection
│   ├── approval_gate.py   # Approval card system
│   └── daily_brief.py     # Morning/evening/weekly templates
├── memory/
│   ├── memory_manager.py  # Long-term memory CRUD
│   ├── rag_memory.py      # Vector/RAG episodic memory
│   ├── vault.py           # Encrypted secrets vault
│   └── pre_seed.py        # Seed Sorie's known context
├── core/
│   ├── decision_engine.py # Intent → skill → tool routing
│   ├── context_manager.py # Session context tracking
│   ├── llm_client.py      # LLM backend selection
│   └── prompt.txt         # NISHA personality & routing rules
├── actions/               # 21 real tools (no simulation)
├── skills/                # 12 skill categories + router
├── dashboard/             # FastAPI remote dashboard
└── cloud/                 # Railway, Render, Docker configs
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/SorieAdams/NISHA-AGENTIC-AI.git
cd NISHA-AGENTIC-AI

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Add your API key
# Edit config/api_keys.json → add gemini_api_key

# 4. First-run setup
python setup.py

# 5. Seed memory
python memory/pre_seed.py

# 6. Launch NISHA
python main.py
```

---

## Cloud Deployment

See `cloud/README_CLOUD.md` for:
- Railway (recommended — free tier)
- Render
- Docker (any VPS)

---

## Key Rules (from NISHA_SOUL.md)

1. **Never simulate** — every tool calls real APIs, returns real results
2. **Never announce memory saves** — save_memory is always silent
3. **Vision cooldown** — 4 seconds between screen_process calls
4. **Domain exclusivity** — Steam/Epic → game_updater only, no exceptions
5. **Interrupt must feel instant** — audio chunks 2400 bytes max (~50ms)
6. **Memory before search** — if the answer is in memory, use it
7. **Approval before action** — send, push, delete, publish always require approval
8. **Agent governance** — every agent has a declared identity; deviations are logged

---

## 30-Day Build Plan

See `readme.md` (the original full spec) for the complete 30-day plan with:
- Week 1: Safety & foundation
- Week 2: Product discovery system
- Week 3: Career & portfolio operating system
- Week 4: MVP launch workflow

---

*Built by Sorie Adams Kamara with faith, focus, and the conviction that small, faithful steps taken consistently become meaningful progress.*
