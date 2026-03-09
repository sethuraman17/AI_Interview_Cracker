from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QMouseEvent

from api import ask_backend


class Worker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, question: str):
        super().__init__()
        self.question = question

    def run(self):
        try:
            answer = ask_backend(self.question)
            self.finished.emit(answer)
        except Exception as e:
            self.error.emit(str(e))


class ChatWindow(QWidget):
    def __init__(self, on_minimize, chat_history, on_update_history):
        super().__init__()
        self.on_minimize = on_minimize
        self.chat_history = chat_history
        self.on_update_history = on_update_history

        self.setFixedSize(360, 480)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
                border-radius: 16px;
            }
        """)

        self._drag_pos = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # ===== TITLE BAR =====
        title_bar = QWidget()
        title_bar.setFixedHeight(36)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
        """)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("AI Assistant")
        title_label.setStyleSheet("font-weight: bold;")

        minimize_btn = QPushButton("–")
        minimize_btn.setFixedSize(28, 28)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        minimize_btn.clicked.connect(self.on_minimize)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(minimize_btn)

        title_bar.mousePressEvent = self._mouse_press
        title_bar.mouseMoveEvent = self._mouse_move
        title_bar.mouseReleaseEvent = self._mouse_release

        # ===== CHAT AREA =====
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 8px;
            }
        """)

        # ===== INPUT AREA =====
        input_layout = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask something...")
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 8px;
            }
        """)

        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border-radius: 10px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input)
        input_layout.addWidget(self.send_btn)

        # ===== ADD TO MAIN LAYOUT =====
        main_layout.addWidget(title_bar)
        main_layout.addWidget(self.chat_area)
        main_layout.addLayout(input_layout)

        for sender, text in self.chat_history:
            self.append_message(sender, text)


    # =====================
    # MESSAGE HANDLING
    # =====================
    def send_message(self):
        text = self.input.text().strip()
        if not text:
            return

        self.chat_history.append(("human", text))
        self.on_update_history(self.chat_history)
        self.append_message("human", text)

        self.input.clear()
        self.set_input_enabled(False)

        self.chat_history.append(("ai", "Thinking..."))
        self.on_update_history(self.chat_history)
        self.append_message("ai", "Thinking...")

        self.worker = Worker(text)
        self.worker.finished.connect(self.on_response)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_response(self, answer: str):
        self.chat_history[-1] = ("ai", answer)
        self.on_update_history(self.chat_history)
        self.replace_last_message("ai", answer)
        self.set_input_enabled(True)

    def on_error(self, error: str):
        self.chat_history[-1] = ("ai", f"Error: {error}")
        self.on_update_history(self.chat_history)
        self.replace_last_message("ai", f"Error: {error}")
        self.set_input_enabled(True)

    # =====================
    # CHAT HELPERS
    # =====================
    def append_message(self, sender: str, text: str):
        label = "You" if sender == "human" else "AI"

        html = f"""
        <div style="margin-bottom:12px;">
            <div style="font-weight:bold; margin-bottom:4px;">
                {label}:
            </div>
            <div style="margin-left:8px;">
                {text}
            </div>
        </div>
        """

        self.chat_area.append(html)

    def replace_last_message(self, sender: str, text: str):
        content = self.chat_area.toHtml()
        blocks = content.split("</div>")
        blocks = blocks[:-2]  # remove last message block

        label = "You" if sender == "human" else "AI"

        new_block = f"""
        <div style="margin-bottom:12px;">
            <div style="font-weight:bold; margin-bottom:4px;">
                {label}:
            </div>
            <div style="margin-left:8px;">
                {text}
            </div>
        </div>
        """

        self.chat_area.setHtml("</div>".join(blocks) + new_block)

    def set_input_enabled(self, enabled: bool):
        self.input.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)

    # =====================
    # DRAGGING
    # =====================
    def _mouse_press(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def _mouse_move(self, event: QMouseEvent):
        if self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def _mouse_release(self, event: QMouseEvent):
        self._drag_pos = None
