from pathlib import Path

from PySide6.QtGui import (
    QIcon,
    QResizeEvent,
)

from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from interface.content_panel import ContentPanel
from interface.control_panel import ControlPanel
from interface.widget_effects import apply_shadow


# ===== MAIN WINDOW =====
class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # ===== WINDOW TITLE =====
        self.setWindowTitle(
            "Aurumveil • Optimization & Analysis System"
        )

        # ===== WINDOW ICON =====
        icon_path = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "icons"
            / "aurumveil.ico"
        )

        self.setWindowIcon(
            QIcon(str(icon_path))
        )

        # ===== WINDOW SIZE =====
        self.setMinimumSize(1200, 700)
        self.resize(1200, 750)

        # ===== USER INTERFACE =====
        self._initialize_ui()

    # ===== USER INTERFACE =====
    def _initialize_ui(self) -> None:

        # ===== ROOT LAYOUT =====
        root_layout: QVBoxLayout = QVBoxLayout(self)

        root_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        # ===== APP CONTAINER =====
        self.background_widget: QWidget = QWidget()

        self.background_widget.setObjectName(
            "AppContainer"
        )

        apply_shadow(self.background_widget)

        # ===== CONTENT LAYOUT =====
        content_layout: QHBoxLayout = QHBoxLayout(
            self.background_widget
        )

        content_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        content_layout.setSpacing(4)

        # ===== PANELS =====
        self.content_panel: ContentPanel = ContentPanel()
        self.control_panel: ControlPanel = ControlPanel()

        self.content_panel.control_panel = (
            self.control_panel
        )

        self.control_panel.setFixedWidth(320)

        # ===== SIGNALS =====
        self.control_panel.log_signal.connect(
            self._handle_log
        )

        self.control_panel.refresh_graph_signal.connect(
            self.content_panel.redraw_graph
        )

        # ===== PANEL LAYOUT =====
        content_layout.addWidget(
            self.content_panel,
            7,
        )

        content_layout.addWidget(
            self.control_panel,
            3,
        )

        # ===== ROOT LAYOUT =====
        root_layout.addWidget(
            self.background_widget
        )

    # ===== LOGGING =====
    def _handle_log(self, log_entry: str) -> None:

        self.content_panel.append_system_log(log_entry)

    # ===== RESIZE HANDLING =====
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        # ===== BASE SIZE =====
        base_width: int = 1200
        base_height: int = 750

        # ===== SCALE =====
        scale: float = min(
            self.width() / base_width,
            self.height() / base_height,
        )

        scale: float = max(
            1.05,
            min(scale, 1.7),
        )

        # ===== METRICS =====
        vertical_padding: int = int(6 * scale)
        horizontal_padding: int = int(14 * scale)

        border_radius: int = int(14 * scale)
        font_size: int = int(12 * scale)

        segment_radius: int = int(border_radius * 0.6)

        # ===== DYNAMIC STYLESHEET =====
        responsive_stylesheet: str = f"""
        /* ===== SECONDARY BUTTON ===== */
        QPushButton#SecondaryButton {{
            border-radius: {border_radius}px;

            padding: {vertical_padding}px {horizontal_padding}px;

            font-size: {font_size}px;
        }}


        /* ===== SEGMENT BUTTON ===== */
        QPushButton#SegmentButton {{
            padding: {vertical_padding}px {int(horizontal_padding * 0.8)}px;

            font-size: {font_size}px;
        }}

        QPushButton#SegmentButton:first {{
            border-top-left-radius: {segment_radius}px;
            border-bottom-left-radius: {segment_radius}px;
        }}

        QPushButton#SegmentButton:last {{
            border-top-right-radius: {segment_radius}px;
            border-bottom-right-radius: {segment_radius}px;
        }}


        /* ===== PRIMARY BUTTON ===== */
        QPushButton#PrimaryButton {{
            border-radius: {border_radius}px;

            padding: {vertical_padding}px {horizontal_padding}px;

            font-size: {font_size}px;
        }}
        """

        self.setStyleSheet(responsive_stylesheet)