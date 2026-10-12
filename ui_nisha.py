"""
NISHA UI — Advanced ZOEY-style Interface — October 2026
Pure black background. Dark agent cells. Maya-style right console. Floating command bar.
No hologram. No decorative effects. Data IS the design.
PyQt6
"""

import sys
import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QTextEdit, QLineEdit,
    QComboBox, QSizePolicy, QGridLayout, QSplitter,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

# ─────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────
C = {
    "bg":          "#000000",
    "cell":        "#0f0f0f",
    "cell_border": "#1e1e1e",
    "cell_hover":  "#161616",
    "panel_bg":    "#080f09",
    "panel_border":"#0d2010",
    "accent":      "#3B6FFF",
    "accent_dim":  "#1a3a8f",
    "text_white":  "#FFFFFF",
    "text_dim":    "#888888",
    "text_muted":  "#444444",
    "green":       "#22c55e",
    "amber":       "#f59e0b",
    "red":         "#ef4444",
    "mono":        "#a3e635",
    "bar_bg":      "#0a0a0a",
    "bar_border":  "#222222",
}

FONT_MONO = "Courier New"
FONT_SANS = "Arial"

AGENTS = {
    "nisha":    {"label": "NISHA",    "icon": "✦", "role": "Chief of Staff",        "voice": "Sulafat",      "color": "#3B6FFF"},
    "scout":    {"label": "SCOUT",    "icon": "◎", "role": "Research & Validation", "voice": "Erinome",      "color": "#06b6d4"},
    "asha":     {"label": "ASHA",     "icon": "⬡", "role": "Coding & GitHub",       "voice": "Pulcherrima",  "color": "#a78bfa"},
    "mira":     {"label": "MIRA",     "icon": "◈", "role": "Career & Admin",        "voice": "Despina",      "color": "#34d399"},
    "operator": {"label": "OPERATOR", "icon": "⊕", "role": "Computer & Workflows",  "voice": "Schedar",      "color": "#fb923c"},
}

STATUS_COLORS = {
    "idle":     "#444444",
    "thinking": "#f59e0b",
    "running":  "#22c55e",
    "error":    "#ef4444",
    "waiting":  "#3B6FFF",
}

MODEL_OPTIONS = {
    "nisha":    ["gemini-3.8-flash", "thinkingmachines/inkling:free", "qwen2.5:32b (local)"],
    "scout":    ["thinkingmachines/inkling:free", "nvidia/nemotron-3-ultra-550b:free", "llama3.2 (local)"],
    "asha":     ["poolside/laguna-s-2.1:free", "moonshotai/kimi-k3", "qwen2.5:32b (local)"],
    "mira":     ["nvidia/nemotron-3-ultra-550b:free", "gemini-3.6-flash", "mistral:7b (local)"],
    "operator": ["nvidia/nemotron-3-nano-omni:free", "gemini-3.8-flash", "phi3:medium (local)"],
}


# ─────────────────────────────────────────────
# AGENT CELL
# ─────────────────────────────────────────────
class AgentCell(QFrame):
    model_changed = pyqtSignal(str, str)

    def __init__(self, agent_name: str, parent=None):
        super().__init__(parent)
        self.agent_name = agent_name
        self.agent_info = AGENTS[agent_name]
        self._setup_ui()

    def _setup_ui(self):
        self.setMinimumWidth(260)
        self.setMinimumHeight(175)
        self.setStyleSheet(f"""
            AgentCell {{
                background: {C['cell']};
                border: 1px solid {C['cell_border']};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(5)

        # Header
        header = QHBoxLayout()
        icon = QLabel(self.agent_info["icon"])
        icon.setFont(QFont(FONT_SANS, 18))
        icon.setStyleSheet(f"color: {self.agent_info['color']}; background: transparent;")
        header.addWidget(icon)

        name = QLabel(self.agent_info["label"])
        name.setFont(QFont(FONT_SANS, 13, QFont.Weight.Bold))
        name.setStyleSheet(f"color: {C['text_white']}; background: transparent; letter-spacing: 2px;")
        header.addWidget(name)
        header.addStretch()

        self._dot = QLabel("●")
        self._dot.setFont(QFont(FONT_SANS, 10))
        self._dot.setStyleSheet(f"color: {STATUS_COLORS['idle']}; background: transparent;")
        header.addWidget(self._dot)
        layout.addLayout(header)

        role = QLabel(self.agent_info["role"].upper())
        role.setFont(QFont(FONT_MONO, 8))
        role.setStyleSheet(f"color: {C['text_muted']}; background: transparent; letter-spacing: 1.5px;")
        layout.addWidget(role)
        layout.addSpacing(4)

        # Brain selector
        brain_row = QHBoxLayout()
        blbl = QLabel("BRAIN")
        blbl.setFont(QFont(FONT_MONO, 7))
        blbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent; letter-spacing: 1px;")
        brain_row.addWidget(blbl)

        self._brain = QComboBox()
        self._brain.addItems(MODEL_OPTIONS.get(self.agent_name, []))
        self._brain.setStyleSheet(f"""
            QComboBox {{
                background: #1a1a1a; color: {self.agent_info['color']};
                border: 1px solid #2a2a2a; border-radius: 4px;
                padding: 2px 6px; font-family: {FONT_MONO}; font-size: 9px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: #111; color: {C['text_white']};
                selection-background-color: {C['accent_dim']};
            }}
        """)
        self._brain.currentTextChanged.connect(lambda m: self.model_changed.emit(self.agent_name, m))
        brain_row.addWidget(self._brain)
        layout.addLayout(brain_row)
        layout.addSpacing(3)

        self._task = QLabel("—")
        self._task.setFont(QFont(FONT_MONO, 8))
        self._task.setStyleSheet(f"color: {C['text_dim']}; background: transparent;")
        self._task.setWordWrap(True)
        self._task.setMaximumHeight(34)
        layout.addWidget(self._task)
        layout.addStretch()

        voice = QLabel(f"♪ {self.agent_info['voice']}")
        voice.setFont(QFont(FONT_MONO, 7))
        voice.setStyleSheet(f"color: {self.agent_info['color']}55; background: transparent;")
        layout.addWidget(voice)

    def set_status(self, status: str, task: str = ""):
        color = STATUS_COLORS.get(status, C["text_muted"])
        self._dot.setStyleSheet(f"color: {color}; background: transparent;")
        if task:
            self._task.setText(task[:80] + "…" if len(task) > 80 else task)

    def get_current_model(self) -> str:
        return self._brain.currentText()


# ─────────────────────────────────────────────
# MAYA CONSOLE
# ─────────────────────────────────────────────
class MayaConsole(QWidget):
    approval_signal = pyqtSignal(str, bool)  # action_id, approved

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(340)
        self.setMaximumWidth(420)
        self.setStyleSheet(f"background: {C['panel_bg']}; border-left: 1px solid {C['panel_border']};")
        self._setup_ui()
        QTimer(self, timeout=self._tick, interval=30000).start()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setFixedHeight(42)
        hdr.setStyleSheet(f"background: {C['panel_bg']}; border-bottom: 1px solid {C['panel_border']};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(16, 0, 16, 0)
        t = QLabel("GOVERNANCE CONSOLE")
        t.setFont(QFont(FONT_MONO, 9, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {C['mono']}; letter-spacing: 2px;")
        hl.addWidget(t)
        hl.addStretch()
        self._ts = QLabel(datetime.now().strftime("%H:%M"))
        self._ts.setFont(QFont(FONT_MONO, 8))
        self._ts.setStyleSheet(f"color: {C['text_muted']};")
        hl.addWidget(self._ts)
        layout.addWidget(hdr)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}QScrollBar{width:0;height:0;}")
        content = QWidget()
        content.setStyleSheet(f"background:{C['panel_bg']};")
        self._cl = QVBoxLayout(content)
        self._cl.setContentsMargins(0, 6, 0, 6)
        self._cl.setSpacing(0)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Agent table
        self._add_section("AGENT REGISTRY")
        self._rows: Dict[str, QLabel] = {}
        for name, info in AGENTS.items():
            brain = MODEL_OPTIONS[name][0]
            self._rows[name] = self._add_row(info["label"], brain[:22], "IDLE", C["text_muted"])

        self._cl.addSpacing(6)
        self._add_section("DEVIATIONS / FLAGS")
        self._add_pill("No active deviations", C["green"])

        self._cl.addSpacing(6)
        self._add_section("PENDING APPROVALS")
        self._ap_wrap = QWidget()
        self._ap_wrap.setStyleSheet("background:transparent;")
        self._ap_layout = QVBoxLayout(self._ap_wrap)
        self._ap_layout.setContentsMargins(0, 0, 0, 0)
        self._ap_layout.setSpacing(4)
        no = QLabel("  No pending approvals")
        no.setFont(QFont(FONT_MONO, 8))
        no.setStyleSheet(f"color:{C['text_muted']};")
        self._ap_layout.addWidget(no)
        self._cl.addWidget(self._ap_wrap)

        self._cl.addSpacing(6)
        self._add_section("SYSTEM LOG")
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(180)
        self._log.setFont(QFont(FONT_MONO, 8))
        self._log.setStyleSheet(f"QTextEdit{{background:#050d06;color:{C['mono']};border:none;padding:8px 12px;}}")
        self._cl.addWidget(self._log)
        self._cl.addStretch()

    def _add_section(self, title):
        l = QLabel(f"  {title}")
        l.setFont(QFont(FONT_MONO, 7, QFont.Weight.Bold))
        l.setFixedHeight(26)
        l.setStyleSheet(f"color:{C['text_muted']};background:#0b150c;border-top:1px solid {C['panel_border']};border-bottom:1px solid {C['panel_border']};letter-spacing:2px;")
        self._cl.addWidget(l)

    def _add_row(self, agent, brain, status, sc) -> QLabel:
        row = QWidget()
        row.setFixedHeight(26)
        row.setStyleSheet("background:transparent;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 0, 12, 0)
        rl.setSpacing(0)
        al = QLabel(f"{agent:<10}")
        al.setFont(QFont(FONT_MONO, 8))
        al.setStyleSheet(f"color:{C['text_white']};background:transparent;")
        rl.addWidget(al)
        bl = QLabel(brain)
        bl.setFont(QFont(FONT_MONO, 7))
        bl.setStyleSheet(f"color:{C['accent']};background:transparent;")
        rl.addWidget(bl, stretch=1)
        sl = QLabel(status)
        sl.setFont(QFont(FONT_MONO, 7, QFont.Weight.Bold))
        sl.setStyleSheet(f"color:{sc};background:transparent;")
        rl.addWidget(sl)
        self._cl.addWidget(row)
        return sl

    def _add_pill(self, text, color):
        p = QLabel(f"  ● {text}")
        p.setFont(QFont(FONT_MONO, 8))
        p.setFixedHeight(24)
        p.setStyleSheet(f"color:{color};background:transparent;")
        self._cl.addWidget(p)

    def log(self, msg: str, level: str = "INFO"):
        colors = {"INFO": C["mono"], "WARN": C["amber"], "ERROR": C["red"], "OK": C["green"]}
        color = colors.get(level, C["mono"])
        ts = datetime.now().strftime("%H:%M:%S")
        self._log.append(f'<span style="color:{C["text_muted"]}">[{ts}]</span> <span style="color:{color}">{msg}</span>')
        sb = self._log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def update_agent_status(self, agent: str, status: str):
        row = self._rows.get(agent)
        if row:
            color = STATUS_COLORS.get(status.lower(), C["text_muted"])
            row.setText(status.upper())
            row.setStyleSheet(f"color:{color};background:transparent;")

    def add_approval_card(self, action_id: str, agent: str, action: str, detail: str):
        card = QFrame()
        card.setStyleSheet(f"QFrame{{background:#0d1f0f;border:1px solid {C['amber']}55;border-radius:6px;margin:4px 10px;}}")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(10, 8, 10, 8)
        cl.setSpacing(4)

        top = QHBoxLayout()
        al = QLabel(f"⚠  {agent.upper()}")
        al.setFont(QFont(FONT_MONO, 8, QFont.Weight.Bold))
        al.setStyleSheet(f"color:{C['amber']};")
        top.addWidget(al)
        top.addStretch()
        act_l = QLabel(action)
        act_l.setFont(QFont(FONT_MONO, 7))
        act_l.setStyleSheet(f"color:{C['text_dim']};")
        top.addWidget(act_l)
        cl.addLayout(top)

        dl = QLabel(detail[:60])
        dl.setFont(QFont(FONT_MONO, 8))
        dl.setStyleSheet(f"color:{C['text_white']};")
        dl.setWordWrap(True)
        cl.addWidget(dl)

        br = QHBoxLayout()
        br.addStretch()
        ok = QPushButton("APPROVE")
        ok.setStyleSheet(f"QPushButton{{background:{C['green']}22;color:{C['green']};border:1px solid {C['green']}55;border-radius:4px;padding:3px 12px;font-family:{FONT_MONO};font-size:8px;font-weight:bold;}}QPushButton:hover{{background:{C['green']}44;}}")
        deny = QPushButton("DENY")
        deny.setStyleSheet(f"QPushButton{{background:{C['red']}22;color:{C['red']};border:1px solid {C['red']}55;border-radius:4px;padding:3px 12px;font-family:{FONT_MONO};font-size:8px;font-weight:bold;}}QPushButton:hover{{background:{C['red']}44;}}")
        ok.clicked.connect(lambda: (self.approval_signal.emit(action_id, True), card.deleteLater()))
        deny.clicked.connect(lambda: (self.approval_signal.emit(action_id, False), card.deleteLater()))
        br.addWidget(ok)
        br.addWidget(deny)
        cl.addLayout(br)
        self._ap_layout.insertWidget(0, card)

    def _tick(self):
        self._ts.setText(datetime.now().strftime("%H:%M"))


# ─────────────────────────────────────────────
# COMMAND BAR
# ─────────────────────────────────────────────
class CommandBar(QWidget):
    submitted     = pyqtSignal(str)
    voice_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet(f"background:{C['bar_bg']};border-top:1px solid {C['bar_border']};")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(12)

        self._voice = QPushButton("🎤")
        self._voice.setFixedSize(40, 40)
        self._voice.setCheckable(True)
        self._voice.setStyleSheet(f"QPushButton{{background:#111;color:{C['text_dim']};border:1px solid #2a2a2a;border-radius:20px;font-size:16px;}}QPushButton:checked{{background:{C['accent']}22;border-color:{C['accent']};color:{C['accent']};}}")
        self._voice.toggled.connect(lambda on: (self._voice.setText("🔴" if on else "🎤"), self.voice_toggled.emit(on)))
        layout.addWidget(self._voice)

        self._inp = QLineEdit()
        self._inp.setPlaceholderText("Message NISHA…")
        self._inp.setFont(QFont(FONT_SANS, 12))
        self._inp.setStyleSheet(f"QLineEdit{{background:#111;color:{C['text_white']};border:1px solid #2a2a2a;border-radius:8px;padding:8px 16px;}}QLineEdit:focus{{border-color:{C['accent']}88;}}")
        self._inp.returnPressed.connect(self._send)
        layout.addWidget(self._inp, stretch=1)

        send = QPushButton("↑")
        send.setFixedSize(40, 40)
        send.setStyleSheet(f"QPushButton{{background:{C['accent']};color:white;border:none;border-radius:20px;font-size:18px;font-weight:bold;}}QPushButton:hover{{background:#5080ff;}}")
        send.clicked.connect(self._send)
        layout.addWidget(send)

    def _send(self):
        t = self._inp.text().strip()
        if t:
            self.submitted.emit(t)
            self._inp.clear()


# ─────────────────────────────────────────────
# MAIN WINDOW — NishaUI (matches import in main.py)
# ─────────────────────────────────────────────
class NishaUI(QMainWindow):
    """
    New ZOEY-style NishaUI.
    Replaces the old ui.py NishaUI while keeping the same class name
    so main.py's `from ui import NishaUI` still works without changes.
    Callbacks wired by main.py: on_text_command, on_interrupt.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NISHA — Agentic AI")
        self.setMinimumSize(1280, 760)
        self._cells: Dict[str, AgentCell] = {}
        # Callbacks (set by main.py)
        self.on_text_command  = None
        self.on_remote_clicked = None
        self.on_interrupt      = None
        self.muted             = False
        self.current_file      = None
        self._setup_window()
        self._setup_ui()
        self._demo_step = 0
        self._demo_timer = QTimer(self, timeout=self._demo_tick, interval=8000)
        self._demo_timer.start()

    def _setup_window(self):
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']};}}")
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(C["bg"]))
        p.setColor(QPalette.ColorRole.WindowText, QColor(C["text_white"]))
        self.setPalette(p)

    def _setup_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_topbar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle{background:#1a1a1a;width:1px;}")
        splitter.setHandleWidth(1)
        splitter.addWidget(self._build_cells_area())
        self._console = MayaConsole()
        self._console.approval_signal.connect(self._on_approval)
        splitter.addWidget(self._console)
        splitter.setSizes([900, 380])
        root.addWidget(splitter, stretch=1)

        self._cmd = CommandBar()
        self._cmd.submitted.connect(self._on_command)
        self._cmd.voice_toggled.connect(self._on_voice)
        root.addWidget(self._cmd)

        self._console.log("NISHA system online. Isaiah 60:22.", "OK")
        self._console.log("All agents registered.", "INFO")
        self._console.log("Governance layer active.", "INFO")

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(50)
        bar.setStyleSheet(f"background:{C['bg']};border-bottom:1px solid {C['cell_border']};")
        l = QHBoxLayout(bar)
        l.setContentsMargins(24, 0, 24, 0)

        wm = QLabel("NISHA")
        wm.setFont(QFont(FONT_SANS, 16, QFont.Weight.Bold))
        wm.setStyleSheet(f"color:{C['text_white']};letter-spacing:6px;background:transparent;")
        l.addWidget(wm)

        sub = QLabel("AGENTIC AI")
        sub.setFont(QFont(FONT_MONO, 8))
        sub.setStyleSheet(f"color:{C['text_muted']};letter-spacing:3px;background:transparent;margin-left:8px;")
        l.addWidget(sub)
        l.addStretch()

        self._clock = QLabel(datetime.now().strftime("%A, %d %B %Y  %H:%M"))
        self._clock.setFont(QFont(FONT_MONO, 9))
        self._clock.setStyleSheet(f"color:{C['text_muted']};background:transparent;")
        l.addWidget(self._clock)
        QTimer(self, timeout=lambda: self._clock.setText(datetime.now().strftime("%A, %d %B %Y  %H:%M")), interval=30000).start()

        l.addSpacing(24)
        verse = QLabel("Isaiah 60:22")
        verse.setFont(QFont(FONT_MONO, 8))
        verse.setStyleSheet(f"color:{C['accent_dim']};background:transparent;")
        l.addWidget(verse)
        return bar

    def _build_cells_area(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{C['bg']};")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(28, 24, 24, 16)
        layout.setSpacing(0)

        lbl = QLabel("ACTIVE AGENTS")
        lbl.setFont(QFont(FONT_MONO, 8, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color:{C['text_muted']};letter-spacing:3px;background:transparent;")
        layout.addWidget(lbl)
        layout.addSpacing(16)

        # Row 1: NISHA (wider) + SCOUT
        r1 = QHBoxLayout()
        r1.setSpacing(16)
        nc = AgentCell("nisha")
        nc.setMinimumWidth(300)
        nc.model_changed.connect(self._on_model_change)
        self._cells["nisha"] = nc
        r1.addWidget(nc, stretch=2)
        sc = AgentCell("scout")
        sc.model_changed.connect(self._on_model_change)
        self._cells["scout"] = sc
        r1.addWidget(sc, stretch=1)
        layout.addLayout(r1)
        layout.addSpacing(16)

        # Row 2: ASHA (staggered down) + MIRA + OPERATOR (staggered up)
        r2 = QHBoxLayout()
        r2.setSpacing(16)

        aw = QWidget()
        aw.setStyleSheet("background:transparent;")
        awl = QVBoxLayout(aw)
        awl.setContentsMargins(0, 20, 0, 0)
        ac = AgentCell("asha")
        ac.model_changed.connect(self._on_model_change)
        self._cells["asha"] = ac
        awl.addWidget(ac)
        r2.addWidget(aw, stretch=1)

        mc = AgentCell("mira")
        mc.model_changed.connect(self._on_model_change)
        self._cells["mira"] = mc
        r2.addWidget(mc, stretch=1)

        ow = QWidget()
        ow.setStyleSheet("background:transparent;")
        owl = QVBoxLayout(ow)
        owl.setContentsMargins(0, 0, 0, 20)
        oc = AgentCell("operator")
        oc.model_changed.connect(self._on_model_change)
        self._cells["operator"] = oc
        owl.addWidget(oc)
        r2.addWidget(ow, stretch=1)
        layout.addLayout(r2)
        layout.addStretch()
        return w

    # ── Public API (called by main.py) ───────────────────────────────────────
    def set_state(self, state: str):
        """Called by main.py: LISTENING | THINKING | SPEAKING | IDLE"""
        mapping = {
            "LISTENING": ("thinking", "Listening for voice input…"),
            "THINKING":  ("thinking", "Processing your request…"),
            "SPEAKING":  ("running",  "Generating response…"),
            "IDLE":      ("idle",     ""),
        }
        s, task = mapping.get(state, ("idle", ""))
        self._cells["nisha"].set_status(s, task)
        self._console.update_agent_status("nisha", s)

    def write_log(self, text: str):
        """Called by main.py to write to the console log."""
        level = "ERROR" if "ERR" in text else "WARN" if "WARN" in text else "OK" if "SYS:" in text else "INFO"
        self._console.log(text, level)

    def show_content(self, label: str, content: str):
        """Called by main.py to display content results."""
        self._console.log(f"📄 {label}", "INFO")
        self._console.log(content[:200] + ("…" if len(content) > 200 else ""), "INFO")

    def notify_phone_connected(self):
        self._console.log("📱 Remote phone connected.", "OK")

    def start_camera_stream(self):
        self._console.log("📷 Camera stream started.", "INFO")

    def stop_camera_stream(self):
        self._console.log("📷 Camera stream stopped.", "INFO")

    def add_approval_request(self, action_id: str, agent: str, action: str, detail: str):
        """Called by agents/governance to show approval card."""
        self._console.add_approval_card(action_id, agent, action, detail)

    def update_agent(self, agent: str, status: str, task: str = ""):
        """Called by orchestrator to update agent cell status."""
        if agent in self._cells:
            self._cells[agent].set_status(status, task)
        self._console.update_agent_status(agent, status)

    # ── Internal handlers ────────────────────────────────────────────────────
    def _on_command(self, text: str):
        self._console.log(f"→ {text}", "INFO")
        if self.on_text_command:
            self.on_text_command(text)
        else:
            self._cells["nisha"].set_status("thinking", f"Processing: {text}")
            self._console.update_agent_status("nisha", "thinking")
            QTimer.singleShot(1500, lambda: (
                self._cells["nisha"].set_status("idle"),
                self._console.update_agent_status("nisha", "idle"),
            ))

    def _on_voice(self, on: bool):
        self._console.log("🎤 Voice active — listening…" if on else "Voice stopped.", "INFO")
        if on:
            self.set_state("LISTENING")
        else:
            self.set_state("IDLE")

    def _on_model_change(self, agent: str, model: str):
        self._console.log(f"Brain swap: {agent.upper()} → {model}", "WARN")

    def _on_approval(self, action_id: str, approved: bool):
        status = "APPROVED" if approved else "DENIED"
        self._console.log(f"Approval {status}: {action_id}", "OK" if approved else "WARN")

    def _demo_tick(self):
        demos = [
            ("scout",    "running",  "Researching Sierra Leone education data…"),
            ("asha",     "thinking", "Reviewing WASSCE app Flutter codebase…"),
            ("mira",     "running",  "Drafting scholarship application letter…"),
            ("scout",    "idle",     "Research complete — 12 sources found."),
            ("asha",     "idle",     "Code review complete. 2 suggestions ready."),
            ("mira",     "idle",     "Draft ready for Sorie's review."),
            ("operator", "running",  "Automating file organisation task…"),
            ("operator", "idle",     "Workflow complete. 47 files organised."),
        ]
        if self._demo_step < len(demos):
            agent, status, task = demos[self._demo_step]
            self.update_agent(agent, status, task)
            self._console.log(f"{agent.upper()}: {task}", "OK" if status == "idle" else "INFO")
            self._demo_step += 1


# ─────────────────────────────────────────────
# Entry point (standalone launch)
# ─────────────────────────────────────────────
def launch():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor(C["bg"]))
    p.setColor(QPalette.ColorRole.WindowText, QColor(C["text_white"]))
    p.setColor(QPalette.ColorRole.Base, QColor("#0a0a0a"))
    p.setColor(QPalette.ColorRole.Text, QColor(C["text_white"]))
    p.setColor(QPalette.ColorRole.Button, QColor(C["cell"]))
    p.setColor(QPalette.ColorRole.ButtonText, QColor(C["text_white"]))
    p.setColor(QPalette.ColorRole.Highlight, QColor(C["accent"]))
    app.setPalette(p)
    win = NishaUI()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
