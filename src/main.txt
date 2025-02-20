from PySide6.QtWidgets import QApplication
from terminal_ui import TerminalApp
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TerminalApp()
    window.show()
    sys.exit(app.exec())