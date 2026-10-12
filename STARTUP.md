# NISHA — How to Start & Host Online

## ─────────────────────────────────────────────
## STEP 1 — SETUP (one time only)
## ─────────────────────────────────────────────

### 1. Clone the repo (if not done)
```
git clone https://github.com/SorieAdams/NISHA-AGENTIC-AI.git
cd NISHA-AGENTIC-AI
```

### 2. Create a virtual environment
```
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
playwright install chromium
```

### 4. Add your API keys
Open `config/api_keys.json` and fill in:
```json
{
  "gemini_api_key":      "YOUR_GEMINI_KEY",
  "openrouter_api_key":  "YOUR_OPENROUTER_KEY",
  "nvidia_api_key":      "YOUR_NVIDIA_NIM_KEY",
  "cerebras_api_key":    "YOUR_CEREBRAS_KEY"
}
```

Where to get keys (all free):
- Gemini:      https://aistudio.google.com/apikey
- OpenRouter:  https://openrouter.ai/settings/keys
- NVIDIA NIM:  https://build.nvidia.com → click any model → Get API Key
- Cerebras:    https://cloud.cerebras.ai → API Keys

### 5. (Optional) Install Ollama for local/private AI
```
# Windows: download from https://ollama.ai
# Then pull the models:
ollama pull qwen2.5:32b    # NISHA + Asha local brain (needs 24GB RAM)
ollama pull llama3.2       # Scout local brain (needs 12GB RAM)
ollama pull mistral:7b     # Mira local brain (needs 12GB RAM)
ollama pull phi3:medium    # Operator local brain (needs 12GB RAM)
```

---

## ─────────────────────────────────────────────
## STEP 2 — RUN LOCALLY (Desktop App)
## ─────────────────────────────────────────────

```
# From project folder, with venv active:
python main.py
```

NISHA will launch the desktop UI.
- Talk to her via microphone or type in the command bar
- Agent cells show live status
- Right console shows governance + approvals

---

## ─────────────────────────────────────────────
## STEP 3 — RUN THE REMOTE DASHBOARD (Phone access)
## ─────────────────────────────────────────────

The remote dashboard lets you control NISHA from your phone browser.

```
# In a second terminal (with venv active):
python -m uvicorn dashboard.server:app --host 0.0.0.0 --port 8000 --reload
```

Then open on your phone: `http://YOUR_PC_IP:8000`
Find your PC's IP: run `ipconfig` on Windows → look for IPv4 Address

---

## ─────────────────────────────────────────────
## STEP 4 — HOST ONLINE (Free Cloud Hosting)
## ─────────────────────────────────────────────

### Option A: Railway (RECOMMENDED — easiest, free tier)

1. Go to https://railway.app → sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select: SorieAdams/NISHA-AGENTIC-AI
4. Railway reads cloud/railway.json automatically
5. Add environment variables in Railway dashboard:
   ```
   GEMINI_API_KEY=your_key
   OPENROUTER_API_KEY=your_key
   NVIDIA_API_KEY=your_key
   CEREBRAS_API_KEY=your_key
   ```
6. Deploy → Railway gives you a public URL like `nisha.up.railway.app`

⚠️ NOTE: Cloud deployment runs the FastAPI dashboard only (no PyQt6 UI).
The desktop UI runs on your Windows machines locally.

### Option B: Render (also free)

1. Go to https://render.com → sign up with GitHub
2. "New Web Service" → connect SorieAdams/NISHA-AGENTIC-AI
3. Render reads cloud/render.yaml automatically
4. Add the same environment variables
5. Deploy → public URL like `nisha.onrender.com`

### Option C: Self-host on your laptop (no cloud needed)

Use ngrok to expose your local dashboard to the internet:

```
# Install ngrok: https://ngrok.com/download
# Then run (in separate terminal):
ngrok http 8000
```

Ngrok gives you a public URL like `https://abc123.ngrok.io`
Share this URL to access NISHA from anywhere.
Free tier: URL changes every restart. $10/month for fixed URL.

---

## ─────────────────────────────────────────────
## QUICK REFERENCE
## ─────────────────────────────────────────────

| Command | What it does |
|---------|-------------|
| `python main.py` | Launch NISHA desktop app |
| `python -m uvicorn dashboard.server:app --host 0.0.0.0 --port 8000` | Start remote dashboard |
| `python core/brain_router.py` | Test brain routing |
| `python core/voice_manager.py` | Test voice assignments |
| `python core/model_registry.py` | List all registered models |

## Files changed today:
- `ui_nisha.py` — New ZOEY-style UI (replaces old ui.py)
- `ui.py` — Now imports NishaUI from ui_nisha.py (backward compat)
- `config/agent_brains.json` — Brain assignments per agent
- `config/voice_config.json` — Voice assignments per agent
- `config/api_keys.json` — Now includes openrouter, nvidia, cerebras keys
- `core/model_registry.py` — 30+ models declared
- `core/brain_router.py` — Failover routing + daily limit tracking
- `core/voice_manager.py` — TTS/STT per agent voice
- `agents/scout.py` — Wired to brain_router
- `agents/asha.py` — Wired to brain_router
- `agents/mira.py` — Wired to brain_router
- `agents/operator.py` — Wired to brain_router
- `agents/orchestrator.py` — Wired to brain_router + voice_manager
- `requirements.txt` — Added openai, google-generativeai, edge-tts
