import sys
import socket
import urllib.request
import json
import re
import threading
import time
import traceback
from pathlib import Path
from typing import Optional, Dict, Any
import os
import datetime

import sounddevice as sd
import asyncio
from google import genai
from google.genai import types

os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import local modules
from ui import NishaUI
from memory.memory_manager import load_memory, format_memory_for_prompt, update_memory
from memory.config_manager import get_brief_enabled
from actions.proactive import ProactiveEngine
from actions.web_search import web_search
from actions.open_app import open_app
from actions.weather_report import weather_action
from actions.browser_control import browser_control
from actions.file_controller import file_controller
from actions.send_message import send_message
from actions.reminder import reminder
from actions.youtube_video import youtube_video
from actions.screen_processor import _capture_screen, _capture_camera
from actions.computer_settings import computer_settings
from actions.desktop import desktop_control
from actions.code_helper import code_helper
from actions.dev_agent import dev_agent
from actions.file_processor import file_processor
from actions.computer_control import computer_control
from actions.game_updater import game_updater
from actions.flight_finder import flight_finder
from actions.system_monitor import get_system_status
from core.llm_client import get_llm_provider, get_api_key, get_llm_settings_for_provider


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


BASE_DIR        = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
PROMPT_PATH     = BASE_DIR / "core" / "prompt.txt"
CHANNELS            = 1
SEND_SAMPLE_RATE    = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE          = 1024


def _get_api_key(backend: Optional[str] = None, config: Optional[dict] = None) -> str:
    """Get API key for the specified backend."""
    if config is None:
        config = _load_full_config()

    if backend == "gemini":
        return config.get("gemini_api_key", "")
    elif backend == "nvidia":
        return config.get("nvidia_api_key", "")
    else:
        # Default to Gemini for backward compatibility
        return config.get("gemini_api_key", "")


def _load_system_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return (
            "You are Nisha, Sorie Adams' personal AI assistant. "
            "Be concise, direct, and always use the provided tools to complete tasks. "
            "Never simulate or guess results — always call the appropriate tool."
        )


def _load_full_config() -> dict:
    """Load the full configuration from api_keys.json."""
    try:
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Config] Error loading config: {e}")
        return {}


def _is_online() -> bool:
    """Check if we have internet connectivity by trying to reach a reliable host."""
    try:
        # Try to connect to Google's DNS server (8.8.8.8) on port 53
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        pass
    try:
        # Try to reach Google homepage
        urllib.request.urlopen("http://www.google.com", timeout=3)
        return True
    except Exception:
        pass


def _clean_transcript(text: str) -> str:
    text = _CTRL_RE.sub("", text)
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)
    return text.strip()


_CTRL_RE = re.compile(r"<ctrl\d+>", re.IGNORECASE)


TOOL_DECLARATIONS = [
    {
        "name": "open_app",
        "description": (
            "Opens any application on the computer. "
            "Use this whenever the user asks to open, launch, or start any app, "
            "website, or program. Always call this tool — never just say you opened it."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {
                    "type": "STRING",
                    "description": "Exact name of the application (e.g. 'WhatsApp', 'Chrome', 'Spotify')"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "web_search",
        "description": (
            "Searches the web. Use for ANY question about current facts, events, prices, "
            "or topics — always prefer this over guessing. "
            "Modes: 'search' (default), 'news' (latest headlines on a topic), "
            "'research' (deep comprehensive answer), 'price' (product cost lookup), "
            "'compare' (side-by-side comparison of items)."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query":  {"type": "STRING", "description": "Search query or topic"},
                "mode":   {"type": "STRING", "description": "search | news | research | price | compare"},
                "items":  {"type": "ARRAY",  "items": {"type": "STRING"}, "description": "Items to compare (compare mode)"},
                "aspect": {"type": "STRING", "description": "Comparison aspect: price | specs | reviews | features"},
            },
            "required": ["query"]
        }
    },
    {
        "name": "weather_report",
        "description": "Live weather for any city",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING", "description": "City name for weather report"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "send_message",
        "description": "Send via WhatsApp, Telegram, etc.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "receiver": {"type": "STRING", "description": "Receiver of the message"},
                "message_text": {"type": "STRING", "description": "Text content of the message"},
                "platform": {"type": "STRING", "description": "Platform to use (whatsapp, telegram)"}
            },
            "required": ["receiver", "message_text", "platform"]
        }
    },
    {
        "name": "reminder",
        "description": "OS-native scheduled notifications",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "date": {"type": "STRING", "description": "Date (YYYY-MM-DD)"},
                "time": {"type": "STRING", "description": "Time (HH:MM 24h)"},
                "message": {"type": "STRING", "description": "Reminder message"}
            },
            "required": ["date", "time", "message"]
        }
    },
    {
        "name": "youtube_video",
        "description": "YouTube search, play, summarize, info, trending",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "play | summarize | get_info | trending (default: play)"},
                "query": {"type": "STRING", "description": "Search query"},
                "save": {"type": "BOOLEAN", "description": "Whether to save the video"},
                "region": {"type": "STRING", "description": "Region code"},
                "url": {"type": "STRING", "description": "YouTube URL"}
            }
        }
    },
    {
        "name": "screen_process",
        "description": "Capture and analyze screen or webcam",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "angle": {"type": "STRING", "description": "screen | camera (default: screen)"},
                "text": {"type": "STRING", "description": "Question about the captured image"}
            }
        }
    },
    {
        "name": "close_camera",
        "description": "Close live camera overlay",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "computer_settings",
        "description": "Volume, brightness, WiFi, power, dark mode, zoom, screenshots, lock, scroll, tabs, refresh",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "volume | brightness | wifi | power | dark_mode | zoom | screenshot | lock | scroll | tabs | refresh"},
                "description": {"type": "STRING", "description": "Optional description"},
                "value": {"type": "NUMBER", "description": "Optional value"}
            }
        }
    },
    {
        "name": "browser_control",
        "description": "Full browser automation",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "go_to | search | click | type | scroll | fill_form | smart_click | smart_type | get_text | get_url | press | new_tab | close_tab | screenshot | back | forward | reload | switch | list_browsers | close | close_all"},
                "browser": {"type": "STRING", "description": "chrome | edge | firefox | opera | brave (optional)"},
                "url": {"type": "STRING", "description": "URL to navigate to"},
                "query": {"type": "STRING", "description": "Search query"},
                "engine": {"type": "STRING", "description": "Search engine (google, bing, duckduckgo)"},
                "selector": {"type": "STRING", "description": "CSS selector"},
                "text": {"type": "STRING", "description": "Text to type"},
                "description": {"type": "STRING", "description": "Description of the action"},
                "direction": {"type": "STRING", "description": "Direction to scroll (up, down, left, right)"},
                "amount": {"type": "NUMBER", "description": "Amount to scroll"},
                "key": {"type": "STRING", "description": "Key to press"},
                "path": {"type": "STRING", "description": "Path for screenshot"},
                "incognito": {"type": "BOOLEAN", "description": "Use incognito mode"},
                "clear_first": {"type": "BOOLEAN", "description": "Clear field before typing"}
            }
        }
    },
    {
        "name": "file_controller",
        "description": "File system operations",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "list | create_file | create_folder | delete | move | copy | rename | read | write | find | largest | disk_usage | organize_desktop | info"},
                "path": {"type": "STRING", "description": "Actual path or shortcut: desktop, downloads, documents, home"},
                "destination": {"type": "STRING", "description": "Destination path for move/copy"},
                "new_name": {"type": "STRING", "description": "New name for rename"},
                "content": {"type": "STRING", "description": "Content to write"},
                "name": {"type": "STRING", "description": "Name for new file/folder"},
                "extension": {"type": "STRING", "description": "File extension"},
                "count": {"type": "NUMBER", "description": "Number of items to create"}
            }
        }
    },
    {
        "name": "desktop_control",
        "description": "Wallpaper, organize desktop, cleanup, stats",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "wallpaper | wallpaper_url | organize | clean | list | stats | task"},
                "path": {"type": "STRING", "description": "Path for wallpaper or organize"},
                "url": {"type": "STRING", "description": "URL for wallpaper"},
                "mode": {"type": "STRING", "description": "Mode for organize (by_type | by_date)"},
                "task": {"type": "STRING", "description": "Task to perform"}
            }
        }
    },
    {
        "name": "code_helper",
        "description": "Write, edit, explain, run, or build single code files",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "write | edit | explain | run | build | auto (default: auto)"},
                "description": {"type": "STRING", "description": "Description of the code task"},
                "language": {"type": "STRING", "description": "Programming language"},
                "output_path": {"type": "STRING", "description": "Output file path"},
                "file_path": {"type": "STRING", "description": "Input file path"},
                "code": {"type": "STRING", "description": "Code to write or edit"},
                "args": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Arguments for running the code"},
                "timeout": {"type": "NUMBER", "description": "Timeout in seconds"}
            }
        }
    },
    {
        "name": "dev_agent",
        "description": "Build complete multi-file projects from scratch",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "description": {"type": "STRING", "description": "Description of the project to build"},
                "language": {"type": "STRING", "description": "Programming language"},
                "project_name": {"type": "STRING", "description": "Name of the project"},
                "timeout": {"type": "NUMBER", "description": "Timeout in seconds"}
            }
        }
    },
    {
        "name": "game_updater",
        "description": "Steam and Epic Games management ONLY",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "update | install | list | download_status | schedule | cancel_schedule | schedule_status"},
                "platform": {"type": "STRING", "description": "steam | epic | both"},
                "game_name": {"type": "STRING", "description": "Name of the game"},
                "app_id": {"type": "STRING", "description": "Application ID"},
                "hour": {"type": "NUMBER", "description": "Hour to schedule (0-23)"},
                "minute": {"type": "NUMBER", "description": "Minute to schedule (0-59)"},
                "shutdown_when_done": {"type": "BOOLEAN", "description": "Shutdown when done"}
            }
        }
    },
    {
        "name": "flight_finder",
        "description": "Live flight price and availability via Google Flights",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "origin": {"type": "STRING", "description": "Origin city"},
                "destination": {"type": "STRING", "description": "Destination city"},
                "date": {"type": "STRING", "description": "Departure date (YYYY-MM-DD)"},
                "return_date": {"type": "STRING", "description": "Return date (YYYY-MM-DD)"},
                "passengers": {"type": "NUMBER", "description": "Number of passengers"},
                "cabin": {"type": "STRING", "description": "Cabin class (economy, business, first)"},
                "save": {"type": "BOOLEAN", "description": "Save flight"}
            }
        }
    },
    {
        "name": "file_processor",
        "description": "Process any file type",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_path": {"type": "STRING", "description": "Path to the file to process"},
                "action": {"type": "STRING", "description": "Action to perform (varies by file type)"},
                "instruction": {"type": "STRING", "description": "Additional instruction"},
                "format": {"type": "STRING", "description": "Output format"},
                "width": {"type": "NUMBER", "description": "Width for resizing"},
                "height": {"type": "NUMBER", "description": "Height for resizing"},
                "scale": {"type": "NUMBER", "description": "Scaling factor"},
                "quality": {"type": "NUMBER", "description": "Quality for compression"},
                "start": {"type": "NUMBER", "description": "Start position"},
                "end": {"type": "NUMBER", "description": "End position"},
                "timestamp": {"type": "STRING", "description": "Timestamp for extraction"},
                "column": {"type": "STRING", "description": "Column for CSV/Excel"},
                "value": {"type": "STRING", "description": "Value for filtering"},
                "condition": {"type": "STRING", "description": "Condition for filtering"},
                "ascending": {"type": "BOOLEAN", "description": "Sort order"},
                "save": {"type": "BOOLEAN", "description": "Save processed file"},
                "destination": {"type": "STRING", "description": "Destination path"}
            }
        }
    },
    {
        "name": "save_memory",
        "description": "Silently save personal facts to persistent memory",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category": {"type": "STRING", "description": "identity | preferences | projects | relationships | wishes | notes"},
                "key": {"type": "STRING", "description": "Snake_case key"},
                "value": {"type": "STRING", "description": "Concise English value"}
            },
            "required": ["category", "key", "value"]
        }
    },
    {
        "name": "shutdown_nisha",
        "description": "Shut down Nisha completely",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "set_model",
        "description": "Change the AI model being used (e.g., 'nemotron-3-22b-instruct-v1', 'mistral-nemo-instruct-2407')",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "model": {"type": "STRING", "description": "The model identifier to use"}
            },
            "required": ["model"]
        }
    }
]


class NishaLive:

    def __init__(self, ui):
        self.ui             = ui
        self._asst_name     = "NISHA"   # updated each session from config
        self.session              = None
        self.audio_in_queue       = None
        self.out_queue            = None
        self._loop                = None
        self._is_speaking         = False
        self._speaking_lock       = threading.Lock()
        self._phone_active        = False   # True while phone mic is streaming; pauses PC mic
        self._pending_vision       = None    # (img_bytes, mime_type, question, angle) to inject after tool response
        self._vision_cam_active    = False   # True if camera was opened for vision → auto-close after response
        self._vision_close_pending = False   # True after vision injected; next turn_complete closes camera
        self._vision_last_time     = 0.0     # monotonic time of last screen_process call (cooldown guard)
        self._vision_busy          = False   # True while a vision capture/inject cycle is in flight
        self._interrupted          = False   # True while draining audio after user interrupt
        self.ui.on_text_command   = self._on_text_command
        self.ui.on_remote_clicked = self._make_remote_key
        self.ui.on_interrupt      = self.interrupt
        self._turn_done_event: asyncio.Event | None = None
        self._dashboard     = None
        self._briefing_sent    = False          # morning briefing fires once per process
        self._proactive        = ProactiveEngine()
        self._last_user_speech = time.monotonic()  # updated on every user utterance

    def _get_llm_config(self) -> dict:
        """
        Determine the LLM configuration based on our policy:
        - Use NVIDIA API if configured (primary)
        - Otherwise fall back to GEMINI API
        """
        config = _load_full_config()

        # Default values (will be overridden based on conditions)
        llm_config = {
            "backend": "unknown",
            "base_url": "",
            "api_key": "",
            "model": ""
        }

        # Check if we have an explicit backend preference in config
        preferred_backend = config.get("llm_backend", "").lower()
        valid_backends = ("gemini", "nvidia")
        if preferred_backend in valid_backends:
            llm_config["preferred"] = preferred_backend

        # Determine which backend to use - NVIDIA first as primary
        nvidia_key = config.get("nvidia_api_key")
        gemini_key = config.get("gemini_api_key")

        if nvidia_key:
            llm_config["backend"] = "nvidia"
            llm_config["base_url"] = config.get("nvidia_base_url", "https://integrate.api.nvidia.com/v1")
            llm_config["api_key"] = nvidia_key
            llm_config["model"] = config.get("nvidia_model", "nemotron-3-22b-instruct-v1")
        elif gemini_key:
            llm_config["backend"] = "gemini"
            llm_config["base_url"] = "https://generativelanguage.googleapis.com/v1beta/models/"
            llm_config["api_key"] = gemini_key
            llm_config["model"] = config.get("gemini_model", "gemini-2.5-flash-native-audio-preview-12-2025")
        else:
            # Fallback to Gemini (will likely fail if no key, but that's okay)
            llm_config["backend"] = "gemini"
            llm_config["base_url"] = "https://generativelanguage.googleapis.com/v1beta/models/"
            llm_config["api_key"] = config.get("gemini_api_key", "")
            llm_config["model"] = config.get("gemini_model", "gemini-2.5-flash-native-audio-preview-12-2025")

        # Override with preferred backend if specified and valid
        llm_context = "default_selection"  # Initialize with default context
        preferred = llm_config.get("preferred")
        if preferred == "nvidia" and nvidia_key:
            llm_config["backend"] = "nvidia"
            llm_config["base_url"] = config.get("nvidia_base_url", "https://integrate.api.nvidia.com/v1")
            llm_config["api_key"] = nvidia_key
            llm_config["model"] = config.get("nvidia_model", "nemotron-3-22b-instruct-v1")
            llm_context = "user_preferred_nvidia"
        elif preferred == "gemini" and gemini_key:
            llm_config["backend"] = "gemini"
            llm_config["base_url"] = "https://generativelanguage.googleapis.com/v1beta/models/"
            llm_config["api_key"] = gemini_key
            llm_config["model"] = config.get("gemini_model", "gemini-2.5-flash-native-audio-preview-12-2025")
            llm_context = "user_preferred_gemini"
        # If preferred is something else or missing key, we keep whatever we decided above

        # Log the decision
        print(f"[LLM] Selected backend: {llm_config['backend']} ({llm_context})")

        return llm_config

    def _make_remote_key(self):
        """Called from Qt main thread when user presses Remote Control."""
        if self._dashboard is None:
            self.ui.write_log(
                "SYS: Dashboard unavailable. "
                "Run: pip install fastapi \"uvicorn[standard]\" cryptography"
            )
            return None
        key    = self._dashboard.new_key()
        url    = self._dashboard.get_url()
        manual = self._dashboard.get_manual_url()
        return url, key, f"{url}/auto-login?key={key}", manual

    def _on_text_command(self, text: str):
        if not self._loop or not self.session:
            return
        # Store the user's speech text for complexity analysis (optional)
        self._last_user_speech_text = text
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns={"parts": [{"text": text}]},
                turn_complete=True
            ),
            self._loop
        )

    def set_speaking(self, value: bool):
        with self._speaking_lock:
            self._is_speaking = value
        if value:
            self.ui.set_state("SPEAKING")
        elif not self.ui.muted:
            self.ui.set_state("LISTENING")

    def interrupt(self) -> None:
        """Stop NISHA mid-speech: drain queued audio and open mic immediately."""
        self._interrupted = True
        q = self.audio_in_queue
        if q:
            drained = 0
            while True:
                try:
                    q.get_nowait()
                    drained += 1
                except Exception:
                    break
            if drained:
                print(f"[NISHA] Interrupted — {drained} audio chunks discarded")
        self.set_speaking(False)
        if self._turn_done_event:
            self._turn_done_event.clear()
        self.ui.write_log("SYS: Interrupted — listening...")

    def speak(self, text: str):
        if not self._loop or not self.session:
            return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns={"parts": [{"text": text}]},
                turn_complete=True
            ),
            self._loop
        )

    def speak_error(self, tool_name: str, error: str):
        short = str(error)[:120]
        self.ui.write_log(f"ERR: {tool_name} — {short}")
        self.speak(f"Sir, {tool_name} encountered an error. {short}")

    def _build_config(self) -> types.LiveConnectConfig:
        from datetime import datetime

        # Load customization from config
        try:
            _cfg = json.loads(open(API_CONFIG_PATH, encoding="utf-8").read())
            self._asst_name = (_cfg.get("assistant_name") or "NISHA").strip()
            _user_name = (_cfg.get("user_name") or "").strip()
        except Exception:
            self._asst_name = "NISHA"
            _user_name = ""

        memory     = load_memory()
        mem_str    = format_memory_for_prompt(memory)
        sys_prompt = _load_system_prompt()

        now      = datetime.now()
        time_str = now.strftime("%A, %B %d, %Y — %I:%M %p")
        time_ctx = (
            f"[CURRENT DATE & TIME]\n"
            f"Right now it is: {time_str}\n"
            f"Use this to calculate exact times for reminders.\n\n"
        )

        # Identity injection — overrides any hardcoded name in prompt.txt
        _addr = (f"ADDRESS: Always call the user '{_user_name}'."
                 if _user_name
                 else "ADDRESS: When speaking Turkish → always say \"efendim\". "
                       "When speaking English → say \"sir\". Never mix languages.")
        identity_ctx = (
            f"[IDENTITY]\n"
            f"Your name is {self._asst_name}. "
            f"Always refer to yourself as {self._asst_name}\n"
            f"{_addr}\n\n"
        )

        parts = [time_ctx, identity_ctx]
        if mem_str:
            parts.append(mem_str)
        parts.append(sys_prompt)

        return types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            output_audio_transcription=types.AudioTranscriptionConfig(),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            system_instruction="\n".join(parts),
            tools=[{"function_declarations": TOOL_DECLARATIONS}],
            session_resumption=types.SessionResumptionConfig(),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Aoede"
                    )
                )
            ),
        )

    async def _execute_tool(self, fc) -> types.FunctionResponse:
        name = fc.name
        args = dict(fc.args or {})

        print(f"[NISHA] �� 🔧 {name}  {args}")
        self.ui.set_state("THINKING")

        if name == "save_memory":
            category = args.get("category", "notes")
            key      = args.get("key", "")
            value    = args.get("value", "")
            if key and value:
                update_memory({category: {key: {"value": value}}})
                print(f"[Memory] �� 💾 save_memory: {category}/{key} = {value}")
            if not self.ui.muted:
                self.ui.set_state("LISTENING")
            return types.FunctionResponse(
                id=fc.id, name=name,
                response={"result": "ok", "silent": True}
            )

        loop   = asyncio.get_event_loop()
        result = "Done."

        try:
            if name == "open_app":
                r = await loop.run_in_executor(None, lambda: open_app(parameters=args, response=None, player=self.ui))
                result = r or f"Opened {args.get('app_name')}."
            elif name == "weather_report":
                r = await loop.run_in_executor(None, lambda: weather_action(parameters=args, player=self.ui))
                result = r or "Weather delivered."
            elif name == "browser_control":
                r = await loop.run_in_executor(None, lambda: browser_control(parameters=args, player=self.ui))
                result = r or "Done."
            elif name == "file_controller":
                r = await loop.run_in_executor(None, lambda: file_controller(parameters=args, player=self.ui))
                result = r or "Done."
            elif name == "send_message":
                r = await loop.run_in_executor(None, lambda: send_message(parameters=args, response=None, player=self.ui, session_memory=None))
                result = r or f"Message sent to {args.get('receiver')}."
            elif name == "reminder":
                r = await loop.run_in_executor(None, lambda: reminder(parameters=args, response=None, player=self.ui))
                result = r or "Reminder set."
            elif name == "youtube_video":
                r = await loop.run_in_executor(None, lambda: youtube_video(parameters=args, response=None, player=self.ui))
                result = r or "Done."
            elif name == "screen_process":
                import time as _t_mod
                _now = _t_mod.monotonic()
                _cooldown = 4.0  # seconds — covers echo window after speaking ends
                if self._vision_busy or (_now - self._vision_last_time) < _cooldown:
                    _wait = max(0, _cooldown - (_now - self._vision_last_time))
                    print(f"[Vision] �� ⏳ Cooldown active ({_wait:.1f}s remaining) — ignoring duplicate call")
                    result = "Vision is still processing the previous request. I will not call this again."
                else:
                    self._vision_busy      = True
                    self._vision_last_time = _now
                    angle     = args.get("angle", "screen").lower()
                    user_text = args.get("text", "What do you see?")
                    if angle == "camera":
                        img_b, mime_t = await loop.run_in_executor(None, _capture_camera)
                        self.ui.start_camera_stream()
                        self._vision_cam_active = True
                        print(f"[Vision] �� 📷 Camera: {len(img_b):,} bytes")
                        _stall = "camera"
                    else:
                        img_b, mime_t = await loop.run_in_executor(None, _capture_screen)
                        print(f"[Vision] �� 🖥��️  Screen: {len(img_b):,} bytes")
                        _stall = "screen"
                    self._pending_vision = (img_b, mime_t, user_text, angle)
                    result = (
                        f"[VISION_ACTIVE] {_stall.capitalize()} captured. "
                        f"Immediately say ONE short natural sentence in the user's own language, "
                        f"telling them you are looking at their {_stall} right now. "
                        f"Do NOT describe or guess content — the actual image arrives in the NEXT message."
                    )
            elif name == "close_camera":
                self.ui.stop_camera_stream()
                result = "Camera closed."
            elif name == "computer_settings":
                r = await loop.run_in_executor(None, lambda: computer_settings(parameters=args, response=None, player=self.ui))
                result = r or "Done."
            elif name == "desktop_control":
                r = await loop.run_in_executor(None, lambda: desktop_control(parameters=args, player=self.ui))
                result = r or "Done."
            elif name == "code_helper":
                r = await loop.run_in_executor(None, lambda: code_helper(parameters=args, player=self.ui, speak=self.speak))
                result = r or "Done."
            elif name == "dev_agent":
                r = await loop.run_in_executor(None, lambda: dev_agent(parameters=args, player=self.ui, speak=self.speak))
                result = r or "Done."
            elif name == "web_search":
                r = await loop.run_in_executor(None, lambda: web_search(parameters=args, response=None, player=self.ui))
                result = r or "Done."
                # Mirror results to the on-screen content panel
                _mode = args.get("mode", "search")
                if r and not r.startswith("No results") and not r.startswith("Search failed"):
                    _query = args.get("query") or ", ".join(args.get("items", []))
                    _label = f"{_mode.upper()} — {_query[:38]}" if _query else _mode.upper()
                    self.ui.show_content(_label, r)
            elif name == "file_processor":
                if not args.get("file_path") and self.ui.current_file:
                    args["file_path"] = self.ui.current_file
                r = await loop.run_in_executor(
                    None,
                    lambda: file_processor(parameters=args, player=self.ui, speak=self.speak)
                )
                result = r or "Done."
            elif name == "computer_control":
                r = await loop.run_in_executor(None, lambda: computer_control(parameters=args, player=self.ui))
                result = r or "Done."
            elif name == "game_updater":
                r = await loop.run_in_executor(None, lambda: game_updater(parameters=args, player=self.ui, speak=self.speak))
                result = r or "Done."
            elif name == "flight_finder":
                r = await loop.run_in_executor(None, lambda: flight_finder(parameters=args, player=self.ui))
                result = r or "Done."
            elif name == "system_status":
                r = await loop.run_in_executor(None, get_system_status)
                result = str(r)
            elif name == "shutdown_nisha":
                self.ui.write_log("SYS: Shutdown requested.")
                self.speak("Goodbye, sir.")
                def _shutdown():
                    import time, os
                    time.sleep(1)
                    os._exit(0)
                threading.Thread(target=_shutdown, daemon=True).start()
            elif name == "set_model":
                model_name = args.get("model", "").strip()
                if not model_name:
                    result = "Please specify a model name."
                else:
                    try:
                        # Update the config file
                        config = _load_full_config()
                        config["nvidia_model"] = model_name
                        with open(API_CONFIG_PATH, "w", encoding="utf-8") as f:
                            json.dump(config, f, indent=2)
                        result = f"Model set to: {model_name}. Changes will take effect on next reconnect."
                        self.ui.write_log(f"MODEL: Changed to {model_name}")
                    except Exception as e:
                        result = f"Failed to set model: {e}"
                        self.ui.write_log(f"MODEL ERROR: {e}")
            else:
                result = f"Unknown tool: {name}"

        except Exception as e:
            result = f"Tool '{name}' failed: {e}"
            traceback.print_exc()
            self.speak_error(name, e)

        if not self.ui.muted:
            self.ui.set_state("LISTENING")

        print(f"[NISHA] �� 📤 {name} → {str(result)[:80]}")
        return types.FunctionResponse(
            id=fc.id, name=name,
            response={"result": result}
        )

    async def _send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send_realtime_input(media=msg)

    async def _listen_audio(self):
        print("[NISHA] [Mic] Mic started")
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            with self._speaking_lock:
                nisha_speaking = self._is_speaking
            if not nisha_speaking and not self.ui.muted and not self._phone_active:
                data = indata.tobytes()
                loop.call_soon_threadsafe(
                    self.out_queue.put_nowait,
                    {"data": data, "mime_type": "audio/pcm"}
                )

        try:
            with sd.InputStream(
                samplerate=SEND_SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
                blocksize=CHUNK_SIZE,
                callback=callback,
            ):
                print("[NISHA] [Mic] Mic stream open")
                while True:
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[NISHA] [Mic] Error: {e}")
            raise

    async def _receive_audio(self):
        print("[NISHA] [Recv] Recv started")
        out_buf, in_buf = [], []

        try:
            while True:
                async for response in self.session.receive():

                    if response.data:
                        if self._interrupted:
                            pass  # discard: interrupted
                        else:
                            if self._turn_done_event and self._turn_done_event.is_set():
                                self._turn_done_event.clear()
                            # Split into ~50 ms chunks so interrupt() stops audio within 50 ms
                            # (24000 Hz × 2 bytes/sample × 0.05 s = 2400 bytes per slice)
                            _audio_data = response.data
                            _SLICE = 2400
                            for _i in range(0, len(_audio_data), _SLICE):
                                self.audio_in_queue.put_nowait(_audio_data[_i : _i + _SLICE])

                    if response.server_content:
                        sc = response.server_content

                        if sc.output_transcription and sc.output_transcription.text:
                            txt = _clean_transcript(sc.output_transcription.text)
                            if txt and txt != (out_buf[-1] if out_buf else ""):
                                out_buf.append(txt)

                        if sc.input_transcription and sc.input_transcription.text:
                            txt = _clean_transcript(sc.input_transcription.text)
                            if txt:
                                in_buf.append(txt)
                                self._last_user_speech = time.monotonic()

                        if sc.turn_complete:
                            if self._turn_done_event:
                                self._turn_done_event.set()

                            # If this turn_complete ends an interrupted response, clear the
                            # flag and skip all further processing for that turn.
                            if self._interrupted:
                                self._interrupted = False
                                in_buf  = []
                                out_buf = []
                                continue

                            full_in = " ".join(in_buf).strip()
                            if full_in:
                                self.ui.write_log(f"You: {full_in}")
                                if self._dashboard:
                                    asyncio.create_task(self._dashboard.broadcast({
                                        "type": "log", "speaker": "user",
                                        "text": full_in,
                                        "ts": datetime.now().isoformat(),
                                    }))
                                in_buf = []

                            full_out = " ".join(out_buf).strip()
                            if full_out:
                                self.ui.write_log(f"{self._asst_name}: {full_out}")
                                if self._dashboard:
                                    asyncio.create_task(self._dashboard.broadcast({
                                        "type": "log", "speaker": "nisha",
                                        "text": full_out,
                                        "ts": datetime.datetime.now().isoformat(),
                                    }))
                                out_buf = []

                            # Vision injection: model finished tool-response turn → now send the image
                            if self._pending_vision and self.session:
                                import base64 as _b64
                                img_b, mime_t, question, angle = self._pending_vision
                                self._pending_vision = None
                                b64 = _b64.b64encode(img_b).decode("ascii")
                                print(f"[Vision] �� 📤 {len(img_b):,} bytes (angle={angle}) → main session")
                                await self.session.send_client_content(
                                    turns={"parts": [
                                        {"inline_data": {"mime_type": mime_t, "data": b64}},
                                        {"text": question},
                                    ]},
                                    turn_complete=True,
                                )
                                # SORIE next turn_complete behaviour depending on angle
                                if self._vision_cam_active:
                                    # Camera: keep busy until NISHA finishes speaking the answer
                                    self._vision_cam_active    = False
                                    self._vision_close_pending = True
                                else:
                                    # Screen-only: no camera to close; release busy flag now
                                    self._vision_busy = False
                            elif self._vision_close_pending:
                                # This turn_complete IS the vision answer — close camera + release busy flag
                                self._vision_close_pending = False
                                self._vision_busy = False
                                async def _cam_close():
                                    await asyncio.sleep(2.0)
                                    self.ui.stop_camera_stream()
                                asyncio.create_task(_cam_close())

                    if response.tool_call:
                        fn_responses = []
                        for fc in response.tool_call.function_calls:
                            print(f"[NISHA] �� 📞 {fc.name}")
                            fr = await self._execute_tool(fc)
                            fn_responses.append(fr)
                        await self.session.send_tool_response(
                            function_responses=fn_responses
                        )
        except Exception as e:
            print(f"[NISHA] [Recv] Error: {e}")
            traceback.print_exc()
            raise

    async def _play_audio(self):
        print("[NISHA] [Play] Play started")

        stream = sd.RawOutputStream(
            samplerate=RECEIVE_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
        )
        stream.start()

        try:
            while True:
                try:
                    chunk = await asyncio.wait_for(
                        self.audio_in_queue.get(),
                        timeout=0.1
                    )
                except asyncio.TimeoutError:
                    if (
                        self._turn_done_event
                        and self._turn_done_event.is_set()
                        and self.audio_in_queue.empty()
                    ):
                        self.set_speaking(False)
                        self._turn_done_event.clear()
                    continue
                self.set_speaking(True)
                try:
                    await asyncio.to_thread(stream.write, chunk)
                except (RuntimeError, asyncio.CancelledError):
                    break   # executor shutting down — exit cleanly
        except Exception as e:
            print(f"[NISHA] �� ❌ Play: {e}")
            raise
        finally:
            self.set_speaking(False)
            stream.stop()
            stream.close()

    # ── Morning briefing ─────────────────────────────────────────────────────

    async def _send_startup_briefing(self) -> None:
        """
        Two-phase briefing optimized for speed:
          Phase 1 — instant greeting (no tools) → speech starts in <1s
          Phase 2 — news pre-fetched in a background thread while Phase 1 plays,
                    delivered as ready text (no Gemini tool-call round-trip) and
                    shown on the UI content panel. Waits for turn_complete event
                    instead of a fixed sleep so there is no unnecessary gap.
        """
        from datetime import datetime
        memory   = load_memory()
        identity = memory.get("identity", {})

        def _val(k: str) -> str:
            e = identity.get(k, {})
            return (e.get("value", "") if isinstance(e, dict) else str(e)).strip()

        lang = _val("language")
        name = _val("name")
        time_str = datetime.now().strftime("%H:%M")

        # Start fetching news immediately — runs in parallel while phase 1 plays
        loop = asyncio.get_event_loop()
        news_future = loop.run_in_executor(None, _fetch_news_sync, "top world news today")

        await asyncio.sleep(0.3)
        if not self.session:
            return

        # ── Phase 1: instant greeting ─────────────────────────────────────
        lang_clause = f" Respond in {lang}." if lang else ""
        name_clause = f" Address the user as {name}." if name else ""
        p1 = (
            f"Greet the user, mention it is {time_str}, and say you are fetching today's news now. "
            f"One short sentence only. Do not call any tools.{lang_clause}{name_clause}"
        )

        # Clear the turn-done event so we can wait for Phase 1 to finish
        if self._turn_done_event:
            self._turn_done_event.clear()

        await self.session.send_client_content(
            turns={"parts": [{"text": p1}]},
            turn_complete=True,
        )
        self.ui.write_log("SYS: Briefing phase 1 (greeting) sent.")

        # ── Phase 2: fire as soon as Phase 1 audio is done ───────────────────
        async def _deliver_news():
            try:
                lang_str = f" Respond in {lang}." if lang else ""

                # Wait for news fetch (already running) and Phase 1 turn-complete
                # in parallel — whichever takes longer determines the wait time
                news_done   = asyncio.wrap_future(news_future)
                turn_waited = False
                if self._turn_done_event:
                    try:
                        await asyncio.wait_for(self._turn_done_event.wait(), timeout=6.0)
                        turn_waited = True
                    except asyncio.TimeoutError:
                        pass

                # If turn_complete didn't fire (timeout), give a small buffer
                if not turn_waited:
                    await asyncio.sleep(1.0)

                try:
                    news_text = await asyncio.wait_for(news_done, timeout=4.0)
                except Exception:
                    news_text = ""

                if not self.session:
                    return

                if news_text and len(news_text) > 60:
                    # Show on UI content panel immediately
                    self.ui.show_content("NEWS — top world news today", news_text)

                    p2 = (
                        f"[BRIEFING] Here are today's top news headlines:\n{news_text}\n\n"
                        "Pick ONE headline, summarise it in one sentence, then say the full list "
                        f"is displayed on screen. Do not call any tools.{lang_str}"
                    )
                else:
                    p2 = (
                        "News headlines could not be fetched right now. "
                        f"Let the user know briefly.{lang_str}"
                    )

                await self.session.send_client_content(
                    turns={"parts": [{"text": p2}]},
                    turn_complete=True,
                )
                self.ui.write_log("SYS: Briefing phase 2 (news) sent.")
            except Exception as e:
                print(f"[Briefing] Phase 2 error: {e}")
                self.ui.write_log(f"SYS: Briefing phase 2 failed: {e}")

        asyncio.create_task(_deliver_news())

    # ── Proactive mode ─────────────────────────────────────────────────────

    async def _run_proactive_mode(self) -> None:
        """
        Background task: periodically checks if the user has been silent long enough,
        then hands time + memory context to Gemini so it can decide what (if anything)
        to say proactively. No hardcoded rules — Gemini makes the call.
        """
        while True:
            await asyncio.sleep(60)   # evaluate once per minute

            if not self.session:
                continue

            with self._speaking_lock:
                speaking = self._is_speaking
            if speaking:
                continue

            if not self._proactive.should_trigger(self._last_user_speech):
                continue

            self._proactive.mark_triggered()

            try:
                memory = await asyncio.to_thread(load_memory)
                prompt = self._proactive.build_prompt(memory)
                await self.session.send_client_content(
                    turns={"parts": [{"text": prompt}]},
                    turn_complete=True,
                )
                self.ui.write_log("SYS: Proactive check-in.")
            except Exception as e:
                print(f"[Proactive] �� ⚠��️ {e}")

    # ── Phone audio relay ────────────────────────────────────────

    async def _relay_phone_audio(self) -> None:
        """Forward phone mic PCM chunks from dashboard queue into the Gemini Live session."""
        q = self._dashboard._phone_audio_queue
        while True:
            try:
                chunk = await asyncio.wait_for(q.get(), timeout=1.0)
            except asyncio.TimeoutError:
                # No audio for 1 s → phone mic inactive, give PC mic back
                self._phone_active = False
                continue
            self._phone_active = True   # phone is streaming — silence PC mic
            with self._speaking_lock:
                speaking = self._is_speaking
            if not speaking and not self.ui.muted:
                try:
                    self.out_queue.put_nowait(chunk)
                except asyncio.QueueFull:
                    pass

    def _on_phone_connected(self) -> None:
        self.ui.write_log("SYS: Phone connected via Remote Dashboard.")
        self.ui.notify_phone_connected()

    # ── dashboard command relay ────────────────────────────────

    async def _process_dashboard_commands(self) -> None:
        while True:
            try:
                text = await asyncio.wait_for(
                    self._dashboard._command_queue.get(), timeout=0.5
                )
                if not text:
                    continue
                # Wait up to 8s for session to become ready after a wake
                for _ in range(80):
                    if self.session:
                        break
                    await asyncio.sleep(0.1)
                if self.session:
                    await self.session.send_client_content(
                        turns={"parts": [{"text": text}]},
                        turn_complete=True,
                    )
                    self.ui.write_log(f"[Web]: {text}")
                else:
                    print(f"[Dashboard] Dropped command (no session): {text}")
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                print(f"[Dashboard] Command error: {e}")
                await asyncio.sleep(0.5)

    # ── main loop ────────────────────────────────────────────────────────

    async def run(self):
        # Get or create event loop for compatibility with Python 3.14+
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create a new one
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        # Start dashboard (optional — needs: pip install fastapi "uvicorn[standard]" cryptography)
        try:
            from dashboard.server import DashboardServer
            self._dashboard = DashboardServer()
            self._dashboard.set_connect_callback(self._on_phone_connected)
            asyncio.create_task(self._dashboard.serve())
            # Runs for the whole lifetime, not just inside an active session
            asyncio.create_task(self._process_dashboard_commands())
        except Exception as e:
            print(f"[Dashboard] Disabled: {e}")
            self._dashboard = None

        while True:
            try:
                print("[NISHA] Connecting...")
                self.ui.set_state("THINKING")

                # Get dynamic LLM configuration based on connectivity and prefs
                llm_config = self._get_llm_config()

                config = self._build_config()

                # Fresh client on every reconnect — avoids stale HTTP session state
                # Use the dynamic base URL and API key from our LLM config
                # Only set GOOGLE_API_ENDPOINT for Gemini backend to avoid confusing the client
                if llm_config["backend"] == "gemini":
                    os.environ["GOOGLE_API_ENDPOINT"] = llm_config["base_url"]
                    print(f"[DEBUG] Set GOOGLE_API_ENDPOINT to: {llm_config['base_url']}")
                else:
                    # Unset the variable for non-Gemini backends to avoid interference
                    if "GOOGLE_API_ENDPOINT" in os.environ:
                        del os.environ["GOOGLE_API_ENDPOINT"]
                        print(f"[DEBUG] Unset GOOGLE_API_ENDPOINT")

                # Try to connect with the preferred backend, fall back to secondary on failure
                primary_backend = llm_config["backend"]
                secondary_backend = "nvidia" if primary_backend == "gemini" else "gemini"

                last_error = None
                for backend_name in (primary_backend, secondary_backend):
                    try:
                        # Get config for this backend attempt
                        backend_config = self._get_llm_config_for_backend(backend_name)
                        print(f"[DEBUG] Attempting connection with backend: {backend_name}")

                        if backend_config["backend"] == "gemini":
                            # Use Google Gemini client for Live API
                            print(f"[DEBUG] Creating Gemini client with API key: {backend_config['api_key'][:10]}...")
                            client = genai.Client(
                                api_key=backend_config["api_key"],
                                http_options={"api_version": "v1beta"}
                            )
                            # The model to use - note: for the live API, we need the full model name
                            # including the "models/" prefix if not already present
                            model_name = backend_config["model"]
                            if not model_name.startswith("models/"):
                                model_name = f"models/{model_name}"

                            print(f"[DEBUG] Connecting to Gemini Live API with model: {model_name}")

                            async with (
                                client.aio.live.connect(model=model_name, config=config) as session,
                                asyncio.TaskGroup() as tg,
                            ):
                                await self._run_session(session, tg)
                                # If we get here, the connection was successful
                                print("[DEBUG] Gemini connection successful!")
                                break  # Exit the retry loop
                        else:
                            # For NVIDIA backend, we don't have Live API support yet
                            # For now, we'll raise NotImplementedError to fall back to Gemini
                            # In a full implementation, this would use NVIDIA's real-time API
                            print(f"[DEBUG] NVIDIA backend selected but not implemented, falling back to Gemini")
                            raise NotImplementedError(
                                f"NVIDIA backend ({backend_name}) is selected but real-time API integration "
                                f"is not yet complete. Falling back to Gemini."
                            )

                    except NotImplementedError as e:
                        # If this is the secondary backend and it's not implemented,
                        # we should raise the error to be handled below
                        if backend_name == secondary_backend:
                            print(f"[DEBUG] Secondary backend also not implemented: {e}")
                            raise
                        # If this is the primary backend and it's not implemented,
                        # continue to try the secondary
                        print(f"[DEBUG] Primary backend not implemented, trying secondary: {e}")
                        last_error = None  # Clear the error since we're intentionally trying fallback
                        continue
                    except Exception as e:
                        last_error = e
                        print(f"[DEBUG] Connection attempt failed with {backend_name}: {e}")
                        # If this was our last attempt, re-raise the exception
                        if backend_name == secondary_backend:
                            raise
                        # Otherwise, continue to try the secondary backend
                        print(f"[DEBUG] Trying secondary backend...")
                        continue
                else:
                    # This point is only reached if we didn't break out of the loop (i.e., both attempts failed)
                    if last_error:
                        raise last_error
                    else:
                        raise RuntimeError("Failed to establish connection with any LLM backend")

            except KeyboardInterrupt:
                raise
            except SystemExit:
                raise
            except BaseException as e:
                # Catches both Exception and BaseExceptionGroup (Python 3.11+
                # TaskGroup raises BaseExceptionGroup when tasks are cancelled
                # externally, which `except Exception` would miss, letting the
                # exception escape the while-loop and causing asyncio.run() to
                # start shutdown — resulting in "executor after shutdown" errors).
                err_str = str(e)
                print(f"[NISHA] Error ({type(e).__name__}): {e}")
                traceback.print_exc()

                # Invalid API key — stop hammering the API, prompt re-configuration
                if "API key not valid" in err_str or "1007" in err_str:
                    self.ui.write_log("ERR: API key invalid — please re-enter your key.")
                    self.ui.set_state("SLEEPING")
                    self.ui.prompt_reconfig()
                    while not self.ui._win._ready:
                        await asyncio.sleep(1)
                    print("[NISHA] New API key saved — reconnecting...")
                    _conn_backoff = 3
                    continue

                # Network / timeout errors — log clearly and back off
                is_net_err = any(k in err_str for k in (
                    "TimeoutError", "timed out", "getaddrinfo", "CancelledError",
                    "ConnectionRefusedError", "OSError", "Cannot connect",
                ))
                if is_net_err:
                    self.ui.write_log(f"NET: Connection issue — retrying in 3s")
                    await asyncio.sleep(3)
                    continue

                # For other errors, show a brief message and continue
                self.ui.write_log(f"ERR: {type(e).__name__} — {str(e)[:100]}")
                await asyncio.sleep(3)

    def _get_llm_config_for_backend(self, backend: str) -> dict:
        """Get LLM configuration for a specific backend."""
        config = _load_full_config()

        if backend == "nvidia":
            return {
                "backend": "nvidia",
                "base_url": config.get("nvidia_base_url", "https://integrate.api.nvidia.com/v1"),
                "api_key": config.get("nvidia_api_key", ""),
                "model": config.get("nvidia_model", "nemotron-3-22b-instruct-v1")
            }
        else:  # gemini
            return {
                "backend": "gemini",
                "base_url": "https://generativelanguage.googleapis.com/v1beta/models/",
                "api_key": config.get("gemini_api_key", ""),
                "model": config.get("gemini_model", "gemini-2.5-flash-native-audio-preview-12-2025")
            }

    async def _run_session(self, session, tg):
        """Run the actual session with the established connection."""
        self.session          = session
        self.audio_in_queue   = asyncio.Queue()
        self.out_queue        = asyncio.Queue(maxsize=200)
        self._turn_done_event = asyncio.Event()

        # Reset transient state that must not carry over from a previous session
        self._pending_vision       = None
        self._vision_cam_active    = False
        self._vision_close_pending = False
        self._vision_busy          = False
        self._vision_last_time     = 0.0
        self._interrupted          = False

        print("[NISHA] Connected.")
        self.ui.set_state("LISTENING")
        self.ui.write_log("SYS: NISHA online.")

        if self._dashboard:
            await self._dashboard.broadcast({"type": "status", "state": "active"})

        tg.create_task(self._send_realtime())
        tg.create_task(self._listen_audio())
        tg.create_task(self._receive_audio())
        tg.create_task(self._play_audio())
        # tg.create_task(self._run_system_monitor())
        tg.create_task(self._run_proactive_mode())
        if self._dashboard:
            tg.create_task(self._relay_phone_audio())

        # Morning briefing — fires once per process launch (if enabled)
        if not self._briefing_sent and get_brief_enabled():
            self._briefing_sent = True
            tg.create_task(self._send_startup_briefing())


# Helper function for fetching news (used in morning briefing)
def _fetch_news_sync(query: str) -> str:
    """Synchronous function to fetch news for briefing."""
    try:
        from actions.web_search import web_search
        result = web_search({"query": query, "mode": "news"}, None)
        return result if result and not result.startswith("No results") and not result.startswith("Search failed") else ""
    except Exception:
        return ""

if __name__ == "__main__":
    from ui import NishaUI
    import sys
    from PyQt6.QtWidgets import QApplication
    import threading
    import asyncio

    app = QApplication(sys.argv)
    face_path = str(BASE_DIR / "config" / "nisha.ico")
    ui = NishaUI(face_path)
    nisha = NishaLive(ui)
    ui.show()

    def run_nisha():
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(nisha.run())
        except Exception as e:
            print(f"Error in NishaLive run loop: {e}")
        finally:
            loop.close()

    thread = threading.Thread(target=run_nisha, daemon=True)
    thread.start()

    sys.exit(app.exec())