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
    QComboBox, QSizePolicy, QGridLayout, QGraphicsDropShadowEffect,
    QSplitter,
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QPoint, pyqtProperty, QObject,
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPainter, QPen, QBrush,
    QLinearGradient, QFontDatabase, QPixmap, QIcon,
    QPainterPath, QPolygonF,
)

# ─────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────
C = {
    "bg":          "#000000",   # pure black background
    "cell":        "#0f0f0f",   # agent cell background
    "cell_border": "#1e1e1e",   # subtle cell border
    "cell_hover":  "#161616",   # cell hover state
    "panel_bg":    "#080f09",   # Maya right panel (dark green-black)
    "panel_border":"#0d2010",   # Maya panel border
    "accent":      "#3B6FFF",   # electric blue — ZOEY accent
    "accent_dim":  "#1a3a8f",   # dimmed blue
    "text_white":  "#FFFFFF",
    "text_dim":    "#888888",
    "text_muted":  "#444444",
    "green":       "#22c55e",   # active / healthy
    "amber":       "#f59e0b",   # warning
    "red":         "#ef4444",   # error / deviation
    "mono":        "#a3e635",   # console monospace text
    "bar_bg":      "#0a0a0a",   # command bar
    "bar_border":  "#222222",
    "dashed_line": "#1e3a5f",   # connection line between cells
}

FONT_MONO  = "Courier New"
FONT_SANS  = "Arial"

# Agent definitions
AGENTS = {
    "nisha":    {"label": "NISHA",    "icon": "✦", "role": "Chief of Staff",         "voice": "Sulafat",     "color": C["accent"]},
    "scout":    {"label": "SCOUT",    "icon": "◎", "role": "Research & Validation",  "voice": "Erinome",     "color": "#06b6d4"},
    "asha":     {"label": "ASHA",     "icon": "⬡", "role": "Coding & GitHub",        "voice": "Pulcherrima", "color": "#a78bfa"},
    "mira":     {"label": "MIRA",     "icon": "◈", "role": "Career & Admin",         "voice": "Despina",     "color": "#34d399"},
    "operator": {"label": "OPERATOR", "icon": "⊕", "role": "Computer & Workflows",   "voice": "Schedar",     "color": "#fb923c"},
}

STATUS_COLORS = {
    "idle":     C["text_muted"],
    "thinking": C["amber"],
    "running":  C["green"],
    "error":    C["red"],
    "waiting":  C["accent"],
}

MODEL_OPTIONS = {
    "nisha":    ["gemini-3.8-flash", "thinkingmachines/inkling:free", "qwen2.5:32b (local)"],
    "scout":    ["thinkingmachines/inkling:free", "nvidia/nemotron-3-ultra-550b:free", "llama3.2 (local)"],
    "asha":     ["poolside/laguna-s-2.1:free", "moonshotai/kimi-k3", "qwen2.5:32b (local)"],
    "mira":     ["nvidia/nemotron-3-ultra-550b:free", "gemini-3.6-flash", "mistral:7b (local)"],
    "operator": ["nvidia/nemotron-3-nano-omni:free", "gemini-3.8-flash", "phi3:medium (local)"],
}


# ─────────────────────────────────────────────
# AGENT CELL  (ZOEY-style dark card)
# ─────────────────────────────────────────────
class AgentCell(QFrame):
    model_changed = pyqtSignal(str, str)   # agent_name, new_model

    def __init__(self, agent_name: str, parent=None):
        super().__init__(parent)
        self.agent_name   = agent_name
        self.agent_info   = AGENTS[agent_name]
        self._status      = "idle"
        self._last_task   = "—"
        self._pulse_alpha = 0
        self._setup_ui()
        self._setup_pulse()

    def _setup_ui(self):
        self.setMinimumWidth(260)
        self.setMinimumHeight(170)
        self.setStyleSheet(f"""
            AgentCell {{
                background: {C['cell']};
                border: 1px solid {C['cell_border']};
                border-radius: 12px;
            }}
            AgentCell:hover {{
                border: 1px solid {self.agent_info['color']}55;
                background: {C['cell_hover']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(6)

        # ── Header row ───────────────────────────
        header = QHBoxLayout()
        header.setSpacing(10)

        icon_lbl = QLabel(self.agent_info["icon"])
        icon_lbl.setFont(QFont(FONT_SANS, 18))
        icon_lbl.setStyleSheet(f"color: {self.agent_info['color']}; background: transparent;")
        header.addWidget(icon_lbl)

        name_lbl = QLabel(self.agent_info["label"])
        name_lbl.setFont(QFont(FONT_SANS, 13, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {C['text_white']}; background: transparent; letter-spacing: 2px;")
        header.addWidget(name_lbl)
        header.addStretch()

        self._status_dot = QLabel("●")
        self._status_dot.setFont(QFont(FONT_SANS, 10))
        self._status_dot.setStyleSheet(f"color: {STATUS_COLORS['idle']}; background: transparent;")
        header.addWidget(self._status_dot)

        layout.addLayout(header)

        # ── Role ─────────────────────────────────
        role_lbl = QLabel(self.agent_info["role"].upper())
        role_lbl.setFont(QFont(FONT_MONO, 8))
        role_lbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent; letter-spacing: 1.5px;")
        layout.addWidget(role_lbl)

        layout.addSpacing(6)

        # ── Brain selector ────────────────────────
        brain_row = QHBoxLayout()
        brain_lbl = QLabel("BRAIN")
        brain_lbl.setFont(QFont(FONT_MONO, 7))
        brain_lbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent; letter-spacing: 1px;")
        brain_row.addWidget(brain_lbl)

        self._brain_select = QComboBox()
        self._brain_select.addItems(MODEL_OPTIONS.get(self.agent_name, ["gemini-3.8-flash"]))
        self._brain_select.setStyleSheet(f"""
            QComboBox {{
                background: #1a1a1a;
                color: {self.agent_info['color']};
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                padding: 2px 6px;
                font-family: {FONT_MONO};
                font-size: 9px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: #111;
                color: {C['text_white']};
                selection-background-color: {C['accent_dim']};
            }}
        """)
        self._brain_select.currentTextChanged.connect(
            lambda m: self.model_changed.emit(self.agent_name, m)
        )
        brain_row.addWidget(self._brain_select)
        layout.addLayout(brain_row)

        layout.addSpacing(4)

        # ── Last task ─────────────────────────────
        self._task_lbl = QLabel("—")
        self._task_lbl.setFont(QFont(FONT_MONO, 8))
        self._task_lbl.setStyleSheet(f"color: {C['text_dim']}; background: transparent;")
        self._task_lbl.setWordWrap(True)
        self._task_lbl.setMaximumHeight(36)
        layout.addWidget(self._task_lbl)

        layout.addStretch()

        # ── Voice badge ───────────────────────────
        voice_lbl = QLabel(f"♪ {self.agent_info['voice']}")
        voice_lbl.setFont(QFont(FONT_MONO, 7))
        voice_lbl.setStyleSheet(f"color: {self.agent_info['color']}55; background: transparent;")
        layout.addWidget(voice_lbl)

    def _setup_pulse(self):
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._do_pulse)

    def _do_pulse(self):
        # Animate status dot brightness when agent is active
        self._pulse_alpha = (self._pulse_alpha + 15) % 256

    def set_status(self, status: str, task: str = ""):
        self._status = status
        color = STATUS_COLORS.get(status, C["text_muted"])
        self._status_dot.setStyleSheet(f"color: {color}; background: transparent;")
        if task:
            self._last_task = task[:80] + "…" if len(task) > 80 else task
            self._task_lbl.setText(self._last_task)
        if status in ("thinking", "running"):
            self._pulse_timer.start(80)
        else:
            self._pulse_timer.stop()

    def get_current_model(self) -> str:
        return self._brain_select.currentText()


# ─────────────────────────────────────────────
# CELLS CANVAS  (draws dashed connection lines)
# ─────────────────────────────────────────────
class CellsCanvas(QWidget):
    """Transparent overlay that draws dashed lines between agent cells."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._connections: list[tuple[QPoint, QPoint]] = []

    def set_connections(self, connections: list[tuple[QPoint, QPoint]]):
        self._connections = connections
        self.update()

    def paintEvent(self, event):
        if not self._connections:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(C["dashed_line"]))
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(1)
        pen.setDashPattern([4, 6])
        painter.setPen(pen)
        for p1, p2 in self._connections:
            painter.drawLine(p1, p2)
        painter.end()


# ─────────────────────────────────────────────
# MAYA CONSOLE  (right panel — monospace tables)
# ─────────────────────────────────────────────
class MayaConsole(QWidget):
    """Maya-style right panel: dense monospace tables, approval cards, deviations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(340)
        self.setMaximumWidth(420)
        self.setStyleSheet(f"background: {C['panel_bg']}; border-left: 1px solid {C['panel_border']};")
        self._setup_ui()
        self._mock_tick_timer = QTimer(self)
        self._mock_tick_timer.timeout.connect(self._tick)
        self._mock_tick_timer.start(3000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Panel header ──────────────────────────
        header = QWidget()
        header.setFixedHeight(42)
        header.setStyleSheet(f"background: {C['panel_bg']}; border-bottom: 1px solid {C['panel_border']};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)
        title = QLabel("GOVERNANCE CONSOLE")
        title.setFont(QFont(FONT_MONO, 9, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C['mono']}; letter-spacing: 2px;")
        h_layout.addWidget(title)
        h_layout.addStretch()
        ts = QLabel(datetime.now().strftime("%H:%M"))
        ts.setFont(QFont(FONT_MONO, 8))
        ts.setStyleSheet(f"color: {C['text_muted']};")
        self._timestamp = ts
        h_layout.addWidget(ts)
        layout.addWidget(header)

        # ── Scrollable content ─────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar { width: 0; height: 0; }")
        content = QWidget()
        content.setStyleSheet(f"background: {C['panel_bg']};")
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(0, 8, 0, 8)
        self._content_layout.setSpacing(0)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # ── Agent status table ─────────────────────
        self._add_section("AGENT REGISTRY")
        self._agent_rows: Dict[str, QLabel] = {}
        for name, info in AGENTS.items():
            row = self._add_table_row(
                agent=info["label"],
                brain="gemini-3.8-flash" if name == "nisha" else "inkling:free",
                status="IDLE",
                status_color=C["text_muted"],
            )
            self._agent_rows[name] = row

        self._content_layout.addSpacing(8)

        # ── Deviations ─────────────────────────────
        self._add_section("DEVIATIONS / FLAGS")
        self._add_pill_row("No active deviations", C["green"])

        self._content_layout.addSpacing(8)

        # ── Approvals ──────────────────────────────
        self._add_section("PENDING APPROVALS")
        self._approval_area = QWidget()
        self._approval_area.setStyleSheet("background: transparent;")
        self._approval_layout = QVBoxLayout(self._approval_area)
        self._approval_layout.setContentsMargins(0, 0, 0, 0)
        self._approval_layout.setSpacing(4)
        no_pending = QLabel("  No pending approvals")
        no_pending.setFont(QFont(FONT_MONO, 8))
        no_pending.setStyleSheet(f"color: {C['text_muted']};")
        self._approval_layout.addWidget(no_pending)
        self._content_layout.addWidget(self._approval_area)

        self._content_layout.addSpacing(8)

        # ── Live log ───────────────────────────────
        self._add_section("SYSTEM LOG")
        self._log_box = QTextEdit()
        self._log_box.setReadOnly(True)
        self._log_box.setMaximumHeight(180)
        self._log_box.setFont(QFont(FONT_MONO, 8))
        self._log_box.setStyleSheet(f"""
            QTextEdit {{
                background: #050d06;
                color: {C['mono']};
                border: none;
                padding: 8px 12px;
            }}
        """)
        self._content_layout.addWidget(self._log_box)
        self._content_layout.addStretch()

    def _add_section(self, title: str):
        lbl = QLabel(f"  {title}")
        lbl.setFont(QFont(FONT_MONO, 7, QFont.Weight.Bold))
        lbl.setFixedHeight(28)
        lbl.setStyleSheet(f"""
            color: {C['text_muted']};
            background: #0b150c;
            border-top: 1px solid {C['panel_border']};
            border-bottom: 1px solid {C['panel_border']};
            letter-spacing: 2px;
        """)
        self._content_layout.addWidget(lbl)

    def _add_table_row(self, agent: str, brain: str, status: str, status_color: str) -> QLabel:
        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent;")
        row_widget.setFixedHeight(26)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(12, 0, 12, 0)
        row_layout.setSpacing(0)

        agent_lbl = QLabel(f"{agent:<10}")
        agent_lbl.setFont(QFont(FONT_MONO, 8))
        agent_lbl.setStyleSheet(f"color: {C['text_white']}; background: transparent;")
        row_layout.addWidget(agent_lbl)

        brain_lbl = QLabel(brain[:22])
        brain_lbl.setFont(QFont(FONT_MONO, 7))
        brain_lbl.setStyleSheet(f"color: {C['accent']}; background: transparent;")
        row_layout.addWidget(brain_lbl, stretch=1)

        status_lbl = QLabel(status)
        status_lbl.setFont(QFont(FONT_MONO, 7, QFont.Weight.Bold))
        status_lbl.setStyleSheet(f"color: {status_color}; background: transparent;")
        row_layout.addWidget(status_lbl)

        self._content_layout.addWidget(row_widget)
        return status_lbl

    def _add_pill_row(self, text: str, color: str):
        pill = QLabel(f"  ● {text}")
        pill.setFont(QFont(FONT_MONO, 8))
        pill.setFixedHeight(24)
        pill.setStyleSheet(f"color: {color}; background: transparent;")
        self._content_layout.addWidget(pill)

    # ── Public API ───────────────────────────────────────────────────────────
    def log(self, message: str, level: str = "INFO"):
        color_map = {"INFO": C["mono"], "WARN": C["amber"], "ERROR": C["red"], "OK": C["green"]}
        color = color_map.get(level, C["mono"])
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_box.append(f'<span style="color:{C["text_muted"]}">[{ts}]</span> <span style="color:{color}">{message}</span>')
        sb = self._log_box.verticalScrollBar()
        sb.setValue(sb.maximum())

    def update_agent_status(self, agent_name: str, status: str, brain: str = ""):
        row_lbl = self._agent_rows.get(agent_name)
        if row_lbl:
            color = STATUS_COLORS.get(status.lower(), C["text_muted"])
            row_lbl.setText(status.upper())
            row_lbl.setStyleSheet(f"color: {color}; background: transparent;")

    def add_approval_card(self, agent: str, action: str, detail: str):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #0d1f0f;
                border: 1px solid {C['amber']}55;
                border-radius: 6px;
                margin: 4px 10px;
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(10, 8, 10, 8)
        cl.setSpacing(4)

        top = QHBoxLayout()
        agent_lbl = QLabel(f"⚠  {agent.upper()}")
        agent_lbl.setFont(QFont(FONT_MONO, 8, QFont.Weight.Bold))
        agent_lbl.setStyleSheet(f"color: {C['amber']};")
        top.addWidget(agent_lbl)
        top.addStretch()
        action_lbl = QLabel(action)
        action_lbl.setFont(QFont(FONT_MONO, 7))
        action_lbl.setStyleSheet(f"color: {C['text_dim']};")
        top.addWidget(action_lbl)
        cl.addLayout(top)

        detail_lbl = QLabel(detail[:60])
        detail_lbl.setFont(QFont(FONT_MONO, 8))
        detail_lbl.setStyleSheet(f"color: {C['text_white']};")
        detail_lbl.setWordWrap(True)
        cl.addWidget(detail_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        approve_btn = QPushButton("APPROVE")
        approve_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['green']}22;
                color: {C['green']};
                border: 1px solid {C['green']}55;
                border-radius: 4px;
                padding: 3px 12px;
                font-family: {FONT_MONO};
                font-size: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {C['green']}44; }}
        """)
        deny_btn = QPushButton("DENY")
        deny_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['red']}22;
                color: {C['red']};
                border: 1px solid {C['red']}55;
                border-radius: 4px;
                padding: 3px 12px;
                font-family: {FONT_MONO};
                font-size: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {C['red']}44; }}
        """)
        approve_btn.clicked.connect(lambda: self._remove_card(card))
        deny_btn.clicked.connect(lambda: self._remove_card(card))
        btn_row.addWidget(approve_btn)
        btn_row.addWidget(deny_btn)
        cl.addLayout(btn_row)

        self._approval_layout.insertWidget(0, card)

    def _remove_card(self, card: QFrame):
        card.setParent(None)
        card.deleteLater()
        self.log("Approval decision recorded.", "OK")

    def _tick(self):
        self._timestamp.setText(datetime.now().strftime("%H:%M"))


# ─────────────────────────────────────────────
# COMMAND BAR  (floating bottom strip)
# ─────────────────────────────────────────────
class CommandBar(QWidget):
    submitted = pyqtSignal(str)
    voice_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._listening = False
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            background: {C['bar_bg']};
            border-top: 1px solid {C['bar_border']};
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(12)

        # Voice button
        self._voice_btn = QPushButton("🎤")
        self._voice_btn.setFixedSize(40, 40)
        self._voice_btn.setStyleSheet(f"""
            QPushButton {{
                background: #111;
                color: {C['text_dim']};
                border: 1px solid #2a2a2a;
                border-radius: 20px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                border-color: {C['accent']};
                color: {C['accent']};
            }}
            QPushButton:checked {{
                background: {C['accent']}22;
                border-color: {C['accent']};
                color: {C['accent']};
            }}
        """)
        self._voice_btn.setCheckable(True)
        self._voice_btn.toggled.connect(self._on_voice_toggle)
        layout.addWidget(self._voice_btn)

        # Text input
        self._input = QLineEdit()
        self._input.setPlaceholderText("Message NISHA…")
        self._input.setFont(QFont(FONT_SANS, 12))
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: #111111;
                color: {C['text_white']};
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 8px 16px;
            }}
            QLineEdit:focus {{
                border-color: {C['accent']}88;
            }}
        """)
        self._input.returnPressed.connect(self._on_submit)
        layout.addWidget(self._input, stretch=1)

        # Send button
        self._send_btn = QPushButton("↑")
        self._send_btn.setFixedSize(40, 40)
        self._send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['accent']};
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #5080ff; }}
            QPushButton:pressed {{ background: {C['accent_dim']}; }}
        """)
        self._send_btn.clicked.connect(self._on_submit)
        layout.addWidget(self._send_btn)

    def _on_submit(self):
        text = self._input.text().strip()
        if text:
            self.submitted.emit(text)
            self._input.clear()

    def _on_voice_toggle(self, on: bool):
        self._listening = on
        self._voice_btn.setText("🔴" if on else "🎤")
        self.voice_toggled.emit(on)


# ─────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────
class NishaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NISHA — Agentic AI")
        self.setMinimumSize(1280, 780)
        self._cells: Dict[str, AgentCell] = {}
        self._setup_window()
        self._setup_ui()
        self._start_demo_ticker()

    def _setup_window(self):
        self.setStyleSheet(f"QMainWindow {{ background: {C['bg']}; }}")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(C["bg"]))
        self.setPalette(palette)

    def _setup_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background: {C['bg']};")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ───────────────────────────────
        topbar = self._build_topbar()
        root.addWidget(topbar)

        # ── Main area (cells + console) ───────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #1a1a1a; width: 1px; }")
        splitter.setHandleWidth(1)

        # Left: agent cells
        left = self._build_cells_area()
        splitter.addWidget(left)

        # Right: Maya console
        self._console = MayaConsole()
        splitter.addWidget(self._console)
        splitter.setSizes([900, 380])

        root.addWidget(splitter, stretch=1)

        # ── Command bar ───────────────────────────
        self._cmd_bar = CommandBar()
        self._cmd_bar.submitted.connect(self._on_command)
        self._cmd_bar.voice_toggled.connect(self._on_voice)
        root.addWidget(self._cmd_bar)

        # Initial log
        self._console.log("NISHA system online.", "OK")
        self._console.log("All agents registered.", "INFO")
        self._console.log("Governance active.", "INFO")

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(50)
        bar.setStyleSheet(f"background: {C['bg']}; border-bottom: 1px solid {C['cell_border']};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)

        # NISHA wordmark
        wordmark = QLabel("NISHA")
        wordmark.setFont(QFont(FONT_SANS, 16, QFont.Weight.Bold))
        wordmark.setStyleSheet(f"color: {C['text_white']}; letter-spacing: 6px; background: transparent;")
        layout.addWidget(wordmark)

        sub = QLabel("AGENTIC AI")
        sub.setFont(QFont(FONT_MONO, 8))
        sub.setStyleSheet(f"color: {C['text_muted']}; letter-spacing: 3px; background: transparent; margin-left: 8px;")
        layout.addWidget(sub)

        layout.addStretch()

        # System time
        self._clock = QLabel(datetime.now().strftime("%A, %d %B %Y  %H:%M"))
        self._clock.setFont(QFont(FONT_MONO, 9))
        self._clock.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
        layout.addWidget(self._clock)

        # Clock timer
        timer = QTimer(self)
        timer.timeout.connect(lambda: self._clock.setText(datetime.now().strftime("%A, %d %B %Y  %H:%M")))
        timer.start(30000)

        layout.addSpacing(24)

        # Isaiah 60:22 badge
        verse = QLabel("Isaiah 60:22")
        verse.setFont(QFont(FONT_MONO, 8))
        verse.setStyleSheet(f"color: {C['accent_dim']}; background: transparent;")
        layout.addWidget(verse)

        return bar

    def _build_cells_area(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background: {C['bg']};")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 24, 16)
        layout.setSpacing(0)

        # Section label
        section_lbl = QLabel("ACTIVE AGENTS")
        section_lbl.setFont(QFont(FONT_MONO, 8, QFont.Weight.Bold))
        section_lbl.setStyleSheet(f"color: {C['text_muted']}; letter-spacing: 3px; background: transparent;")
        layout.addWidget(section_lbl)
        layout.addSpacing(16)

        # ── ZOEY-style staggered grid ─────────────
        # Row 1: NISHA (wider) + SCOUT
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        nisha_cell = AgentCell("nisha")
        nisha_cell.setMinimumWidth(300)     # NISHA gets more space
        self._cells["nisha"] = nisha_cell
        nisha_cell.model_changed.connect(self._on_model_change)
        row1.addWidget(nisha_cell, stretch=2)

        scout_cell = AgentCell("scout")
        self._cells["scout"] = scout_cell
        scout_cell.model_changed.connect(self._on_model_change)
        row1.addWidget(scout_cell, stretch=1)

        layout.addLayout(row1)
        layout.addSpacing(16)

        # ── Row 2: ASHA + MIRA + OPERATOR (staggered) ──
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        # Vertical offset for stagger effect — push ASHA down slightly
        asha_wrap = QWidget()
        asha_wrap.setStyleSheet("background: transparent;")
        aw_layout = QVBoxLayout(asha_wrap)
        aw_layout.setContentsMargins(0, 20, 0, 0)
        asha_cell = AgentCell("asha")
        self._cells["asha"] = asha_cell
        asha_cell.model_changed.connect(self._on_model_change)
        aw_layout.addWidget(asha_cell)
        row2.addWidget(asha_wrap, stretch=1)

        mira_cell = AgentCell("mira")
        self._cells["mira"] = mira_cell
        mira_cell.model_changed.connect(self._on_model_change)
        row2.addWidget(mira_cell, stretch=1)

        # Vertical offset for OPERATOR — push up slightly
        op_wrap = QWidget()
        op_wrap.setStyleSheet("background: transparent;")
        ow_layout = QVBoxLayout(op_wrap)
        ow_layout.setContentsMargins(0, 0, 0, 20)
        op_cell = AgentCell("operator")
        self._cells["operator"] = op_cell
        op_cell.model_changed.connect(self._on_model_change)
        ow_layout.addWidget(op_cell)
        row2.addWidget(op_wrap, stretch=1)

        layout.addLayout(row2)
        layout.addStretch()

        return container

    # ── Event handlers ───────────────────────────────────────────────────────
    def _on_command(self, text: str):
        self._console.log(f"→ {text}", "INFO")
        # Simulate NISHA thinking
        self._cells["nisha"].set_status("thinking", f"Processing: {text}")
        self._console.update_agent_status("nisha", "thinking")
        QTimer.singleShot(1800, lambda: self._nisha_respond(text))

    def _nisha_respond(self, text: str):
        self._cells["nisha"].set_status("idle", "Awaiting next task")
        self._console.update_agent_status("nisha", "idle")
        self._console.log("NISHA: Response ready.", "OK")

    def _on_voice(self, on: bool):
        if on:
            self._console.log("🎤 Voice input active — listening…", "INFO")
            self._cells["nisha"].set_status("thinking", "Listening…")
        else:
            self._console.log("Voice input stopped.", "INFO")
            self._cells["nisha"].set_status("idle")

    def _on_model_change(self, agent: str, model: str):
        self._console.log(f"Brain swap: {agent.upper()} → {model}", "WARN")

    def _start_demo_ticker(self):
        """Simulate live agent activity for demo purposes."""
        self._demo_timer = QTimer(self)
        self._demo_timer.timeout.connect(self._demo_tick)
        self._demo_timer.start(8000)
        self._demo_step = 0

    def _demo_tick(self):
        demos = [
            ("scout", "running", "Researching Sierra Leone education data…"),
            ("asha",  "thinking", "Reviewing WASSCE app Flutter codebase…"),
            ("mira",  "running", "Drafting scholarship application letter…"),
            ("scout", "idle", "Research complete — 12 sources found."),
            ("asha",  "idle", "Code review complete. 2 suggestions ready."),
            ("mira",  "idle", "Draft ready for Sorie's review."),
        ]
        if self._demo_step < len(demos):
            agent, status, task = demos[self._demo_step]
            self._cells[agent].set_status(status, task)
            self._console.update_agent_status(agent, status)
            if status == "running":
                self._console.log(f"{agent.upper()}: {task}", "INFO")
            else:
                self._console.log(f"{agent.upper()}: {task}", "OK")
            self._demo_step += 1


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def launch():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(C["bg"]))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(C["text_white"]))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#0a0a0a"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(C["cell"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor(C["cell"]))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor(C["text_white"]))
    palette.setColor(QPalette.ColorRole.Text,            QColor(C["text_white"]))
    palette.setColor(QPalette.ColorRole.Button,          QColor(C["cell"]))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(C["text_white"]))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(C["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(C["text_white"]))
    app.setPalette(palette)

    win = NishaWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
