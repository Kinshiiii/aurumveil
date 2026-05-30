import sys
import logging

from PySide6.QtWidgets import QApplication

from engine.orchestration.runtime_initializer import build_application
from stylesheet import APP_STYLESHEET
from interface.main_window import MainWindow


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


# ===== TERMINAL =====
def pause_terminal() -> None:

    try:
        input("\nPress Enter to exit...")

    except KeyboardInterrupt:
        pass


# ===== APPLICATION START =====
def launch_application() -> int:

    # ===== BUILD =====
    try:
        build_application()

    except Exception as error:
        logging.error(error)

        pause_terminal()

        raise

    # ===== APPLICATION =====
    application: QApplication = QApplication(
        sys.argv
    )

    application.setStyle("Fusion")
    application.setStyleSheet(APP_STYLESHEET)

    # ===== WINDOW =====
    main_window: MainWindow = MainWindow()

    main_window.show()

    return application.exec()


# ===== ENTRY =====
if __name__ == "__main__":
    sys.exit(launch_application())