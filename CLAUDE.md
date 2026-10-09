# NISHA — Complete Project Intelligence File
> Owner: Sorie Adams Kamara | Base reference: SORIE ADAMS' NISHA by SORIE ADAMS

---

## 1. What Is Nisha

Nisha is a cross-platform personal AI assistant built for Windows, macOS, and Linux (including WSL). She is voice-first, screen-aware, memory-persistent, and can hear, see, understand, and control the computer she runs on.

Nisha is NOT a chatbot. She is an autonomous agent with tools, decision logic, and persistent intelligence. Every capability is a callable tool. She never simulates or pretends — she always calls the correct tool and reports the real result.

**Core identity:**
- Name: Nisha (never Assistant, never AI)
- Owner: Sorie Adams Kamara — always addressed as "Sorie Adams"
- Tone: Calm, female, sharp, professional. Warm but never sycophantic.
- Voice (female): TTS. Concise. No filler. No unnecessary words.
- Language: English by default. 
- Self-awareness: Knows she is an AI. BUT CAN ACT OR pretends to be human WHEN ASK.

---

## 2. Project Structure

```
nisha/
├── main.py                    # Core loop — LLM session, audio I/O, tool dispatch
├── ui.py                      # PyQt6 HUD — waveform, log, interrupt, camera feed
├── setup.py                   # First-run configuration wizard
├── actions/
│   ├── web_search.py          # Multi-mode web search
│   ├── screen_processor.py    # Screen capture and webcam vision
│   ├── reminder.py            # OS-native scheduled notifications
│   ├── system_monitor.py      # CPU/RAM/GPU/temperature telemetry
│   ├── computer_settings.py   # Volume, brightness, WiFi, power
│   ├── computer_control.py    # Keyboard, mouse, window management
│   ├── open_app.py            # Application launcher
│   ├── browser_control.py     # Web browser automation
│   ├── file_controller.py     # File system operations
│   ├── file_processor.py      # Document/media processing
│   ├── send_message.py        # Messaging — WhatsApp, Telegram
│   ├── weather_report.py      # Live weather data
│   ├── flight_finder.py       # Flight search
│   ├── youtube_video.py       # YouTube control
│   ├── code_helper.py         # Code write/edit/run/explain
│   ├── dev_agent.py           # Full project builder agent
│   ├── desktop.py             # Desktop and taskbar control
│   └── proactive.py           # Proactive silence-break engine
├── memory/
│   ├── memory_manager.py      # Persistent key-value memory store
│   └── config_manager.py      # Settings and config helpers
├── skills/
│   ├── skill_router.py        # Routes intent to correct skill/tool
│   ├── skill_registry.py      # Registry of all declared skills
│   └── skills/
│       ├── productivity.py    # Calendar, tasks, notes
│       ├── research.py        # Deep research mode
│       ├── creative.py        # Writing, brainstorming
│       ├── coding.py          # Code-specific skill layer
│       └── salone.py          # Sierra Leone context (local news, Krio)
├── core/
│   ├── prompt.txt             # Nisha personality and routing rules
│   ├── decision_engine.py     # Decision-making logic
│   └── context_manager.py    # Session context tracking
├── dashboard/
│   ├── server.py              # FastAPI remote dashboard
│   └── templates/             # Phone UI templates
└── config/
    └── api_keys.json          # API keys, name, OS, settings
```

---

## 3. Decision-Making Engine

This is how Nisha thinks before acting. Every input goes through this pipeline before any tool is called.

```
USER INPUT (voice or text)
        │
        ▼
┌─────────────────────┐
│   INTENT CLASSIFIER  │  ← What does Sorie Adams want?
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   CONTEXT CHECKER   │  ← What is the current session context?
│                     │    - What was said before?
│                     │    - What tools were recently called?
│                     │    - Is a task in progress?
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   MEMORY LOOKUP     │  ← Does Nisha already know something relevant?
│                     │    - Check persistent memory
│                     │    - Inject relevant facts into reasoning
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   SKILL ROUTER      │  ← Which skill handles this intent?
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   TOOL SELECTOR     │  ← Which specific tool inside that skill?
│                     │    - Apply tool priority rules
│                     │    - Apply domain exclusivity rules
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   TOOL EXECUTION    │  ← Call the tool, get real result
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   RESPONSE FORMER   │  ← Format result into concise spoken response
│                     │    - Short for simple results
│                     │    - Structured for complex results
│                     │    - Save to memory if relevant
└─────────────────────┘
        │
        ▼
     SPEAK / DISPLAY
```

---

## 4. Skill System

Skills are high-level capability categories. Each skill owns a set of tools. The skill router maps user intent to the right skill, then the skill selects the right tool.

### 4.1 Skill Registry

```
SKILL               OWNS THESE TOOLS                        TRIGGER EXAMPLES
─────────────────────────────────────────────────────────────────────────────
system_control      computer_settings, computer_control,     "open", "close",
                    open_app, desktop_control               "volume up", "shutdown"

web_intelligence    web_search, browser_control,            "search", "find",
                    flight_finder, weather_report           "what is", "look up"

media               youtube_video, file_processor           "play", "watch",
                    (audio/video)                           "pause", "summarize video"

communication       send_message, reminder                  "send", "message",
                                                            "remind me", "tell X"

vision              screen_process, close_camera            "what do you see",
                                                            "look at screen", "camera"

file_ops            file_controller, file_processor,        "open file", "read",
                    desktop_control                         "organize", "delete"

coding              code_helper, dev_agent,                 "write code", "build",
                    browser_control (docs)                  "run", "fix", "explain"

intelligence        web_search (research mode),             "research", "analyze",
                    file_processor, save_memory             "summarize", "compare"

hardware            system_status, system_monitor           "CPU", "RAM", "temp",
                                                            "how's my computer"

memory_ops          save_memory, load_memory                "remember", "forget",
                                                            "what do you know about"

saloone             web_search (local mode),                local Sierra Leone news,
                    weather_report, salone.py               Krio language support

games               game_updater                            ANY Steam or Epic request
```

### 4.2 Skill Router Logic

```python
# core/decision_engine.py — routing priority order

def route_intent(intent: str, context: dict) -> str:
    """
    Returns the skill name to handle this intent.
    Rules applied in order — first match wins.
    """

    # Rule 1 — Domain exclusivity (hardcoded, never overridden)
    if any(w in intent for w in ["steam", "epic", "game update", "install game"]):
        return "games"  # ONLY game_updater. Never browser_control for this.

    # Rule 2 — Vision triggers (explicit)
    if any(w in intent for w in ["screen", "camera", "what do you see", "look at"]):
        return "vision"

    # Rule 3 — Active task continuation
    if context.get("active_skill"):
        return context["active_skill"]  # Stay in same skill if task in progress

    # Rule 4 — Communication
    if any(w in intent for w in ["send", "message", "whatsapp", "telegram", "remind"]):
        return "communication"

    # Rule 5 — Coding
    if any(w in intent for w in ["code", "build", "script", "program", "debug", "fix error"]):
        return "coding"

    # Rule 6 — File operations
    if any(w in intent for w in ["file", "folder", "document", "read", "open", "delete", "organize"]):
        return "file_ops"

    # Rule 7 — Media
    if any(w in intent for w in ["play", "youtube", "watch", "video", "music"]):
        return "media"

    # Rule 8 — Web/research
    if any(w in intent for w in ["search", "find", "what is", "who is", "price", "news", "research"]):
        return "web_intelligence"

    # Rule 9 — Hardware
    if any(w in intent for w in ["cpu", "ram", "memory", "temperature", "battery", "performance"]):
        return "hardware"

    # Rule 10 — System control (broad fallback for action commands)
    if any(w in intent for w in ["open", "close", "volume", "brightness", "wifi", "shutdown"]):
        return "system_control"

    # Default — web intelligence (best general fallback)
    return "web_intelligence"
```

---

## 5. Tool Priority Rules

When multiple tools could handle a request, these rules decide which one is called.

```
PRIORITY RULE 1 — Domain exclusivity
  Steam / Epic Games → ALWAYS game_updater
  NEVER browser_control or web_search for Steam/Epic
  No exceptions. Ever.

PRIORITY RULE 2 — Real over simulated
  If a tool exists for the task, call it.
  Never describe what you would do.
  Never guess a result.

PRIORITY RULE 3 — Specific over general
  code_helper > web_search for coding tasks
  weather_report > web_search for weather
  game_updater > browser_control for games
  file_processor > web_search for file tasks

PRIORITY RULE 4 — Vision cooldown
  screen_process cannot be called within 4 seconds of previous call
  If cooldown active → return "Vision is still processing"
  Never stack vision calls

PRIORITY RULE 5 — Memory before search
  If memory already contains the answer → use it
  Only call web_search if memory is empty or outdated

PRIORITY RULE 6 — Simple before complex
  open_app > browser_control for launching apps
  computer_settings > computer_control for single settings
  Only use computer_control for complex multi-step input tasks

PRIORITY RULE 7 — Browser mode selection
  Simple open/search → user's real browser (real profile, logged-in accounts)
  Interactive automation (click, fill, type) → automation browser instance
  Never use automation browser for simple navigation

PRIORITY RULE 8 — Dev agent vs code helper
  Single file, single function → code_helper
  Multi-file project, full app → dev_agent
  Never call dev_agent for small tasks (wasteful)
```

---

## 6. Switching Logic

Nisha switches between modes, models, and skills dynamically based on context.

### 6.1 Skill Switching

```
TRIGGER                          ACTION
────────────────────────────────────────────────────────
User starts new unrelated topic  → Save context, switch skill, clear active_skill
User says "stop" or "cancel"     → Abort current tool, reset to LISTENING
User says "go back"              → Restore previous skill context
Tool returns error               → Stay in skill, attempt recovery or report error
Tool succeeds                    → Clear active_skill if task complete
Multi-step task detected         → Set active_skill, persist across turns
```

### 6.2 Model Selection (Cloud APIs)

Nisha uses cloud-based APIs for language processing, selecting between Gemini and NVIDIA based on configuration and availability.


**Selection rules:**
- Primary: NVIDIA API (if Gemini unavailable and `nvidia_api_key` configured)
- Fallback: Gemini API (configured via `gemini_api_key`)
- Offline: ollama (qwen2.5:7b)
- Model selection is handled automatically based on the task complexity and configuration.
- Only one API is used at a time; fallback occurs on failure.

```python
# core/llm_client.py handles API selection and failover
```

### 6.3 Input Mode Switching

```
MODE          TRIGGER                    BEHAVIOUR
──────────────────────────────────────────────────────────────────
Voice         Default                    Mic open, VAD active
Keyboard      User types in HUD          Mic pauses, text sent directly
Clipboard     10+ chars copied           Floating panel appears, mic stays open
File drop     File dropped on HUD        file_processor queued for next command
Remote        Phone connected via QR     Commands from phone treated as voice
Muted         User clicks mute           Mic blocked, Nisha stays alive
Interrupted   User clicks interrupt      Audio drained, mic opens immediately
```

### 6.4 State Machine

```
States:        IDLE → LISTENING → THINKING → SPEAKING → LISTENING
                                      ↓
                               (tool executing)
                                      ↓
                              TOOL_EXECUTING → SPEAKING

Interrupt path: ANY STATE → INTERRUPTED → drain audio → LISTENING

Mute path:     LISTENING → MUTED → (keyboard/remote only) → UNMUTED → LISTENING

Error path:    TOOL_EXECUTING → ERROR → speak error → LISTENING
```

---

## 7. Memory System

### 7.1 Architecture

```
memory/
├── identity.json        # name, city, job, language, nationality
├── preferences.json     # food, color, music, hobbies, favorites
├── projects.json        # active projects, goals
├── relationships.json   # friends, family, colleagues
├── wishes.json          # future plans, dreams, things to buy
└── notes.json           # habits, schedule, miscellaneous
```

### 7.2 Memory Injection (system prompt)

At every session start, memory is loaded and injected:

```
[MEMORY — What Nisha knows about Sorie Adams]
identity/name: Sorie Adams Kamara
identity/city: Freetown, Sierra Leone
identity/role: IT Administrator, Information Systems student at IPAM
identity/faith: Christian (Baptist) — Winners Baptist Church, BCSL
projects/ai: Nisha — personal AI assistant
preferences/stack: Python, Riverpod, GoRouter, HTML, CSS, Javascript, etc

# Example: update_memory({"projects": {"nisha": {"value": "building personal AI"}}})

format_memory_for_prompt(memory: dict) → str
# Returns formatted string block for injection into system prompt

forget(category: str, key: str) → None
# Removes a specific memory entry

search_memory(query: str) → dict
# Returns all memory entries relevant to query
    "role": {"value": "IT Administrator, Information Systems student at IPAM"},
    "faith": {"value": "Christian (Baptist) — Winners Baptist Church, BCSL"},
    "email": {"value": "sorieadamskamara11@gmail.com"}
  },
  "projects": {
    "ai_assistant": {"value": "Nisha — personal AI assistant (this project)"}
  },
  "preferences": {
    "stack": {"value": "Flutter, Dart, Supabase, Python, Riverpod, GoRouter, Hive"},
    "ai_tools": {"value": "Gemini API, NVIDIA API, GitHub CLI"},
    "models": {"value": "gemini-2.5-flash for reasoning and coding"}
  },
  "notes": {
    "machine": {"value": "Dell laptop 16GB RAM, WSL2 Ubuntu, Windows"},
    "choir": {"value": "Choir admin at Winners Baptist Church"}
  }
}
```

---

## 8. Complete Tool Registry

### 8.1 open_app
```
Skill:      system_control
Purpose:    Opens any application by name
Parameters: app_name (string, required)
Priority:   Always prefer over browser_control for launching apps
```

### 8.2 web_search
```
Skill:      web_intelligence
Purpose:    Multi-mode web search
Parameters:
  query     (string, required)
  mode:     search | news | research | price | compare
  items:    [list] — compare mode only
  aspect:   price | specs | reviews | features — compare mode only
Decision:   Use research mode for deep questions
            Use news mode for current events
            Use price mode for shopping
            Use compare mode for side-by-side decisions
            Default mode: search
Fallback:   DuckDuckGo if primary search fails
```

### 8.3 system_status
```
Skill:      hardware
Purpose:    Real-time CPU, RAM, GPU, temperature, uptime
Parameters: none
Triggers:   "how's my computer", "check RAM", "CPU usage",
            "temperature", "performance", "memory"
```

### 8.4 weather_report
```
Skill:      web_intelligence
Purpose:    Live weather for any city
Parameters: city (string, required)
Memory:     Reads identity/city from memory if no city given
```

### 8.5 send_message
```
Skill:      communication
Purpose:    Send via WhatsApp, Telegram, etc.
Parameters: receiver, message_text, platform (all required)
```

### 8.6 reminder
```
Skill:      communication
Purpose:    OS-native scheduled notifications
Parameters: date (YYYY-MM-DD), time (HH:MM 24h), message (all required)
OS targets: Windows → Task Scheduler
            macOS   → LaunchAgent plist
            Linux   → systemd user timer
```

### 8.7 youtube_video
```
Skill:      media
Purpose:    YouTube search, play, summarize, info, trending
Parameters:
  action:   play | summarize | get_info | trending (default: play)
  query, save, region, url
```

### 8.8 screen_process
```
Skill:      vision
Purpose:    Capture and analyze screen or webcam
Parameters:
  angle:    screen | camera (default: screen)
  text:     question about the captured image
Pipeline:
  screen → capture → hold in _pending_vision →
  speak brief acknowledgment →
  on turn_complete → inject image + question into session →
  Nisha describes what she sees
Cooldown:   4 seconds between calls (hard rule, never remove)
Vision busy flag: _vision_busy = True during entire pipeline
                  Released only after response delivered
```

### 8.9 close_camera
```
Skill:      vision
Purpose:    Close live camera overlay
Parameters: none
Triggers:   "close camera", "stop camera", "turn off camera"
Auto-close: 2 seconds after camera vision response delivered
```

### 8.10 computer_settings
```
Skill:      system_control
Purpose:    Volume, brightness, WiFi, power, dark mode, zoom, screenshots, lock, scroll, tabs, refresh
Parameters: action, description, value (optional)
Priority:   Use for single setting changes
            Use computer_control for complex multi-step input
```

### 8.11 browser_control
```
Skill:      web_intelligence / system_control
Purpose:    Full browser automation
Parameters:
  action:   go_to | search | click | type | scroll | fill_form | smart_click | smart_type | get_text | get_url | press | new_tab | close_tab | screenshot | back | forward | reload | switch | list_browsers | close | close_all
  browser:  chrome | edge | firefox | opera | brave (optional)
  + url, query, engine, selector, text, description,
    direction, amount, key, path, incognito, clear_first
Mode split:
  Simple open/search → user's real browser (real profile, logged-in accounts)
  Interactive        → automation browser instance
  Multiple browsers  → can run simultaneously
```

### 8.12 file_controller
```
Skill:      file_ops
Purpose:    File system operations
Parameters:
  action:   list | create_file | create_folder | delete | move | copy | rename | read | write | find | largest | disk_usage | organize_desktop | info
  path:     actual path or shortcut: desktop, downloads, documents, home
  + destination, new_name, content, name, extension, count
```

### 8.13 desktop_control
```
Skill:      file_ops / system_control
Purpose:    Wallpaper, organize desktop, cleanup, stats
Parameters:
  action:   wallpaper | wallpaper_url | organize | clean | list | stats | task
  + path, url, mode (by_type | by_date), task
```

### 8.14 code_helper
```
Skill:      coding
Purpose:    Write, edit, explain, run, or build single code files
Parameters:
  action:   write | edit | explain | run | build | auto (default: auto)
  + description, language, output_path, file_path, code, args, timeout
Decision:   Single file/function → code_helper
            Full project → dev_agent
```

### 8.15 dev_agent
```
Skill:      coding
Purpose:    Build complete multi-file projects from scratch
            Plans, writes files, installs deps, opens VS Code, runs, fixes
Parameters: description (required), language, project_name, timeout
Decision:   Full projects only. Never for small tasks.
```

### 8.16 computer_control
```
Skill:      system_control
Purpose:    Direct input: keyboard, mouse, hotkeys, screenshots,
            screen element finding
Parameters:
  action:   type | smart_type | click | double_click | right_click |
            hotkey | press | scroll | move | copy | paste |
            screenshot | wait | clear_field | focus_window |
            screen_find | screen_click | random_data | user_data
  + text, x, y, keys, key, direction, amount, seconds,
    title, description, type, field, clear_first, path
Priority:   Use for complex multi-step input tasks
            Use computer_settings for single setting changes
```

### 8.17 game_updater
```
Skill:      games
Purpose:    Steam and Epic Games management ONLY
Parameters:
  action:   update | install | list | download_status |
            schedule | cancel_schedule | schedule_status
  platform: steam | epic | both
  + game_name, app_id, hour, minute, shutdown_when_done
HARD RULE:  This is the ONLY tool for any Steam/Epic request
            NEVER use browser_control or web_search for Steam/Epic
```

### 8.18 flight_finder
```
Skill:      web_intelligence
Purpose:    Live flight price and availability via Google Flights
Parameters: origin, destination, date (all required)
            + return_date, passengers, cabin, save
```

### 8.19 file_processor
```
Skill:      file_ops / intelligence
Purpose:    Process any file type
Parameters:
  file_path   (uses UI current_file if empty)
  action:     varies by file type —
    image:    describe | ocr | resize | compress | convert | info
    pdf:      summarize | extract_text | to_word | info
    docx/txt: summarize | fix | reformat | translate_hint | word_count | to_bullet
    csv/excel:analyze | stats | filter | sort | convert | info
    json:     validate | format | analyze | to_csv
    code:     explain | review | fix | optimize | run | document | test
    audio:    transcribe | trim | convert | info
    video:    trim | extract_audio | extract_frame | compress | transcribe | info | convert
    archive:  list | extract
    pptx:     summarize | extract_text | analyze
  + instruction, format, width, height, scale, quality,
    start, end, timestamp, column, value, condition,
    ascending, save, destination
```

### 8.20 save_memory
```
Skill:      memory_ops
Purpose:    Silently save personal facts to persistent memory
Parameters:
  category: identity | preferences | projects | relationships | wishes | notes
  key:      snake_case key
  value:    concise English value
RULE:       Always silent. Never announced to Sorie.
```

### 8.21 shutdown_nisha
```
Skill:      system_control
Purpose:    Shut down Nisha completely
Parameters: none
Triggers:   "goodbye", "close", "stop Nisha", "shut down" — any language
```

---

## 9. Audio Architecture

```
SEND_SAMPLE_RATE    = 16000   Hz  (mic → LLM)
RECEIVE_SAMPLE_RATE = 24000   Hz  (LLM → speakers)
CHANNELS            = 1           (mono)
CHUNK_SIZE          = 1024
AUDIO_SLICE         = 2400 bytes  (~50ms at 24kHz)

Mic input:    sounddevice InputStream → PCM → LLM session
Audio output: LLM session → sliced chunks → sounddevice RawOutputStream

Slicing rule: Audio MUST be sliced into 2400-byte chunks
              This ensures interrupt() stops playback within 50ms
              Never send raw unsliced audio to the output queue

Mute rule:    when ui.muted == True → mic callback drops all input
              Nisha stays alive, session stays open, only mic is blocked

Phone rule:   when _phone_active == True → PC mic paused
              Phone mic stream takes over
              Resumes PC mic when phone disconnects
```

### 9.1 Interrupt System

```
TRIGGER:   User clicks interrupt button

EXECUTION:
  1. _interrupted = True
  2. Drain entire audio_in_queue (discard all queued chunks)
  3. set_speaking(False)
  4. _turn_done_event.clear()
  5. ui.set_state("LISTENING")
  6. Log: "SYS: Interrupted — listening..."

RECOVERY:
  On next turn_complete:
  - if _interrupted == True → clear flag, discard in/out buffers, continue
  - Normal processing resumes
```

---

## 10. Vision System

```
SCREEN PIPELINE:
  1. screen_process called (angle="screen")
  2. _capture_screen() → img_bytes, mime_type
  3. _pending_vision = (img_bytes, mime_type, question, "screen")
  4. _vision_busy = True
  5. _vision_last_time = now
  6. Return acknowledgment: "Looking at your screen now"
  7. LLM speaks acknowledgment
  8. turn_complete fires
  9. Inject: image + question into session as client_content
  10. LLM responds with visual description
  11. turn_complete fires again
  12. _vision_busy = False

CAMERA PIPELINE:
  1. screen_process called (angle="camera")
  2. _capture_camera() → img_bytes, mime_type
  3. ui.start_camera_stream() → live overlay visible
  4. _vision_cam_active = True
  5. Same injection pipeline as screen
  6. After vision response: _vision_close_pending = True
  7. 2 seconds after response: ui.stop_camera_stream()
  8. _vision_busy = False

COOLDOWN RULE:
  - 4 second cooldown between any screen_process calls
  - If cooldown active: return "Vision is still processing"
  - _vision_busy flag blocks concurrent calls
  - Both flags (_vision_busy and cooldown) must be clear to proceed
```

---

## 11. Proactive Engine

```python
# actions/proactive.py

class ProactiveEngine:
    SILENCE_THRESHOLD = 900  # 15 minutes in seconds

    def check(self, last_user_speech: float, context: dict) -> str | None:
        """
        Returns a proactive message if conditions are met.
        Returns None if Nisha should stay quiet.
        """
        silence = time.monotonic() - last_user_speech

        if silence < self.SILENCE_THRESHOLD:
            return None

        # Check context for something genuinely useful
        # Not random — based on what Sorie is likely doing
        if context.get("active_project") == "IPAM NEXUS":
            return "Sorie, you've been quiet for a while. Want me to check if there are any open issues on the NEXUS repo?"

        if context.get("time_of_day") == "morning":
            return "Good morning, Sorie. Want your morning brief?"

        return "Sorie, I'm still here if you need me."
```

**Morning briefing pipeline:**
```
Session starts
      │
      ├── Background thread: pre-fetch news (parallel)
      │
      └── Main thread: greet Sorie, speak time
                │
                └── News ready by the time greeting finishes
                          │
                          └── Deliver: news + weather in one brief
```

---

## 12. UI Components (PyQt6 HUD)

```
┌─────────────────────────────────────────────────────┐
│  NISHA                              [⚙] [📱] [🔇]  │  ← Title, settings, remote, mute
├─────────────────────────────────────────────────────┤
│                                                     │
│           [  WAVEFORM VISUALIZER  ]                 │  ← Audio activity
│                                                     │
│  State: LISTENING / THINKING / SPEAKING             │  ← Current state
│                                                     │
├─────────────────────────────────────────────────────┤
│  Sorie: open WhatsApp                               │  ← Log panel
│  Nisha: Opening WhatsApp now.                       │
│  Sorie: search news about Sierra Leone              │
│  Nisha: Here are the latest headlines...            │
├─────────────────────────────────────────────────────┤
│  [CONTENT PANEL — web results, news, search data]   │  ← Scrollable results
├─────────────────────────────────────────────────────┤
│              [⛔ INTERRUPT]                          │  ← Stop Nisha mid-speech
└─────────────────────────────────────────────────────┘

Overlays (appear contextually):
  Camera feed     — when angle="camera" vision active
  Clipboard panel — when 10+ chars copied
                    [TRANSLATE] [SUMMARISE] [EXPLAIN] [FIX]
                    Auto-dismisses after 8 seconds

Settings drawer (slide in from right):
  ☀ MORNING BRIEF: ON/OFF
  ✏ CUSTOMISE ASSISTANT (name, user name)
  🚀 AUTO-START ON BOOT: ON/OFF
```

### 12.1 UI States

```
LISTENING     → waveform active, mic open, state label green
THINKING      → spinner, mic paused, state label amber
SPEAKING      → waveform active, mic blocked, state label blue
MUTED         → waveform grey, mic blocked, mute icon active
INTERRUPTED   → brief flash, immediate return to LISTENING
TOOL_EXECUTING→ same as THINKING with tool name shown
```

---

## 13. Auto-Start System

```
WINDOWS:
  pythonw.exe path written to registry
  HKCU\Software\Microsoft\Windows\CurrentVersion\Run\Nisha
  No console window (pythonw instead of python)

MACOS:
  LaunchAgent plist installed to ~/Library/LaunchAgents/
  com.nisha.assistant.plist

LINUX:
  .desktop file written to ~/.config/autostart/
  nisha.desktop

Toggle: One button in settings drawer
State:  Button reflects current on/off state on every launch
```

---

## 14. Remote Dashboard

```
Backend:    FastAPI (dashboard/server.py)
Protocol:   WebSocket for real-time log broadcast
Auth:       Auto-login via key in QR URL
Phone UI:   Minimal HTML/CSS served by FastAPI

Features:
  - Real-time conversation log on phone
  - Send voice commands from phone
  - One-tap quick commands
  - Connection via QR code scan

QR flow:
  1. Sorie clicks remote button in HUD
  2. Nisha generates one-time key
  3. QR code shown with URL + key
  4. Sorie scans with phone
  5. Phone connects via WebSocket
  6. Commands from phone treated as voice input

Dependencies: fastapi, uvicorn[standard], cryptography, qrcode
```

---

## 15. Clipboard Intelligence

```
Trigger:    Any clipboard copy of 10+ characters
Detection:  Background clipboard monitor thread
Panel:      Floating panel at bottom of HUD

Actions:
  TRANSLATE  → web_search (translate mode) or browser_control
  SUMMARISE  → file_processor (summarize) or LLM direct
  EXPLAIN    → LLM direct with clipboard as context
  FIX        → code_helper (fix) if code detected, else LLM

Behaviour:
  - Panel appears instantly on copy
  - Auto-dismisses after 8 seconds if no action taken
  - One click sends content to Nisha
  - Mic stays open during panel display
  - Panel dismissed immediately on action click
```

---

## 16. Configuration

```json
{
  "gemini_api_key": "your_key_here",
  "nvidia_api_key": "",
  "llm_backend": "gemini",
  "assistant_name": "Nisha",
  "user_name": "Sorie Adams",
  "os": "windows",
  "morning_brief_enabled": true,
  "auto_start": false,
  "voice_name": "default",
  "language": "en",
  "city": "Freetown"
}
```

**llm_backend options:**
```
"gemini"  → uses Gemini Live API (cloud, best quality)
"nvidia"  → uses NVIDIA API (cloud, paid)
```

Identity always read from this file at runtime. Never hardcoded in any tool or logic file.

---

## 17. Key Implementation Rules

```
1.  Never simulate.
    Every tool calls real APIs. Returns real results. No fake output.

2.  Never announce memory saves.
    save_memory is always and only silent.

3.  Vision cooldown is mandatory.
    4 seconds between screen_process calls. Never remove this.

4.  Domain exclusivity is absolute.
    Steam/Epic → game_updater only. No exceptions. Ever.

5.  Interrupt must feel instant.
    Audio chunks must be 2400 bytes max (~50ms). Hard limit.

6.  Identity comes from config, not code.
    Never hardcode "Nisha" or "Sorie" in tools. Always read config.

7.  Morning briefing is parallel.
    News pre-fetched in background thread. Never serial with greeting.

8.  All memory values in English.
    Regardless of what language Sorie speaks in that session.

9.  Camera stays open after vision.
    Never auto-close immediately. Wait for close_camera or explicit request.

10. Windows subprocess must use CREATE_NO_WINDOW.
    Patch Popen globally at top of main.py. No console windows ever.

11. Model switching respects API limits and quota.
    Only one API active at a time with automatic failover.

12. Skill routing first, tool selection second.
    Never jump straight to a tool without passing through skill router.

13. Memory before web search.
    If the answer is in memory, use it. Only search if memory is empty.

14. One active skill at a time.
    Set active_skill when task starts. Clear it when task completes.

15. Test every tool in isolation before wiring into main loop.
    Build order: config → memory → prompt → actions → main → ui → setup
```

---

## 18. Dependencies

```
# Core
PyQt6                        UI framework
sounddevice                  Audio I/O
google-genai                 Gemini backend

# Web
requests                     HTTP client
duckduckgo-search            Web search fallback

# Browser automation
playwright                   Browser control

# File processing
pillow                       Images
pypdf2 / pdfplumber          PDF
python-docx                  Word documents
openpyxl                     Excel
moviepy                      Video
pydub                        Audio
patool                       Archives

# System control
pyautogui                    Screen/input control
psutil                       System metrics
pynput                       Input monitoring
screen-brightness-control    Brightness control

# Remote dashboard
fastapi                      API server
uvicorn[standard]            ASGI server
cryptography                 Auth
qrcode                       QR generation

# Scheduling
(built-in per OS — no pip package needed)
```

---

## 19. Build Order

Always implement Nisha in this exact sequence:

```
Step 1   config/api_keys.json          Config structure and defaults
Step 2   memory/memory_manager.py      Memory load/save/format/search
Step 3   memory/pre_seed.py            Seed Sorie's known context
Step 4   core/prompt.txt               Nisha personality and routing rules
Step 5   core/decision_engine.py       Skill router, model selector, state machine
Step 6   core/context_manager.py       Session context tracking
Step 7   actions/ (one at a time)      Each tool, tested in isolation
         Priority order:
           open_app → computer_settings → web_search →
           weather_report → system_status → reminder →
           browser_control → file_controller → send_message →
           youtube_video → screen_process → computer_control →
           file_processor → code_helper → dev_agent →
           game_updater → flight_finder → desktop_control →
           save_memory → shutdown_nisha → proactive
Step 8   skills/skill_router.py        Wire skills to tools
Step 9   main.py                       Tool registry, session loop, dispatch
Step 10  ui.py                         HUD — build last
Step 11  setup.py                      First-run wizard
Step 12  dashboard/server.py           Remote dashboard
```

---

## 20. Roadmap

```
v1.0   Core voice loop, all tools, memory, UI HUD
v1.1   Auto-start, clipboard intelligence, customization
v1.2   Wake word "Hey Nisha", proactive 2.0, daily continuity
v1.3   Plugin system, email, quiz mode
v2.0   Multi-agent — Nisha coordinates sub-agents
v2.1   Mobile companion — Flutter app, Sorie's phone → Nisha desktop
v2.2   Sierra Leone context — local news, Krio language support
v2.3   IPAM NEXUS integration — Nisha aware of dissertation project status
v2.4   Mi Baptist App integration — church management via voice
```

---

*This file is the single source of truth for building Nisha. Every architectural decision, every tool, every rule lives here. Update this file whenever anything changes.*