import sys
from PySide6.QtWidgets import QApplication
from bubble import FloatingBubble

app = QApplication(sys.argv)

bubble = FloatingBubble()
bubble.show()

sys.exit(app.exec())
