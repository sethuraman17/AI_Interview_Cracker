from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent

from chat import ChatWindow

class FloatingBubble(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(60, 60)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.chat_history = []

        self.label = QLabel("AI", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: white;
                border-radius: 30px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.label.setFixedSize(60, 60)

        self._drag_pos = None
        self.chat_window: ChatWindow | None = None

    # =====================
    # DRAGGING
    # =====================
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    # =====================
    # OPEN CHAT
    # =====================
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.chat_window is None:
            self.open_chat()

    def open_chat(self):
        self.hide()

        self.chat_window = ChatWindow(
            on_minimize=self.restore_bubble,
            chat_history=self.chat_history,
            on_update_history=self.update_history
        )
        self.chat_window.move(self.pos())
        self.chat_window.show()

    def update_history(self, history):
        self.chat_history = history

    # =====================
    # RESTORE BUBBLE
    # =====================
    def restore_bubble(self):
        if self.chat_window:
            self.chat_window.close()
            self.chat_window = None

        self.show()
