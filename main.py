import sys

from PySide6.QtWidgets import QApplication

from theme import APP_THEME
from ui.main_window import MainWindow


# ===== APP START =====
def run_app() -> int:
    application: QApplication = QApplication(sys.argv)

    application.setStyle("Fusion")
    application.setStyleSheet(APP_THEME)

    main_window: MainWindow = MainWindow()
    main_window.show()

    return application.exec()


# ===== ENTRY POINT =====
if __name__ == "__main__":
    sys.exit(run_app())