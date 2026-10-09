# NISHA — Cloud Deployment Guide

NISHA runs in two modes:
- **Local mode**: Full voice, UI (PyQt6), screen vision, computer control
- **Cloud mode**: Dashboard only — web interface, remote commands, agent API

## Cloud Deployment Options

### Option 1: Railway (recommended — free tier available)
1. Push repo to GitHub (already done)
2. Go to railway.app → New Project → Deploy from GitHub
3. Select NISHA-AGENTIC-AI repo
4. Set environment variables (see below)
5. Railway auto-detects `railway.json` and deploys

### Option 2: Render
1. Go to render.com → New → Web Service
2. Connect GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python dashboard/server.py`

### Option 3: Docker (any VPS)
```bash
docker build -t nisha .
docker run -p 8765:8765 -e NISHA_CLOUD_MODE=true nisha
```

## Required Environment Variables
```
GEMINI_API_KEY=your_key
NISHA_CLOUD_MODE=true
PORT=8765
```

## What the Cloud Dashboard Does
- Real-time conversation log
- Remote command input (text)
- Agent status: Scout, Asha, Mira, Operator
- Governance panel: deviations, audit log
- QR code for phone connection

## Security Notes
- Dashboard uses auth key in QR URL
- HTTPS required in production (use Railway/Render built-in SSL)
- Never store API keys in the repo — use environment variables
