##
# @file main.py
# @brief Application entry point for the Aurumveil platform.
#
# Responsible for runtime initialization, Qt application
# configuration, and launching the main graphical interface.
#

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


##
# @brief Pauses the terminal before application shutdown.
#
# Prevents the console window from closing immediately after
# an initialization failure, allowing the user to review
# the reported error message.
#
# @return None
#
def pause_terminal() -> None:

    try:
        input("\nPress Enter to exit...")

    except KeyboardInterrupt:
        pass


##
# @brief Builds and launches the Aurumveil application.
#
# Executes the runtime initialization process, configures
# the Qt application environment, applies the global
# stylesheet, creates the main window, and starts the
# application event loop.
#
# @return int
# Exit code returned by the Qt event loop.
#
# @throws Exception
# Re-raises any exception encountered during the build phase.
#
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


##
# @brief Application entry point.
#
# Starts the Aurumveil application and forwards the Qt
# event loop exit code to the operating system.
#
if __name__ == "__main__":
    sys.exit(launch_application())