from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QIcon

from ui.left_panel import LeftPanel
from ui.right_panel import RightPanel
from ui.utils import add_shadow
from theme import APP_THEME


# ===== MAIN WINDOW =====
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # ===== WINDOW CONFIG =====
        self.setWindowTitle("Aurumveil - Optimization System")

        # TODO: Add application window icon (.ico / .png)
        self.setWindowIcon(QIcon())

        self.setMinimumSize(1200, 700)
        self.resize(1200, 750)

        self._build_ui()

    # ===== LOGGING =====
    def _append_log(self, message: str) -> None:
        self.left_panel.log(message)

    # ===== UI =====
    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)

        self.background_widget = QWidget()
        self.background_widget.setObjectName("Background")
        add_shadow(self.background_widget)

        content_layout = QHBoxLayout(self.background_widget)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(4)

        # ===== PANELS =====
        self.left_panel: LeftPanel = LeftPanel()
        self.right_panel: RightPanel = RightPanel()
        self.left_panel.right_panel = self.right_panel

        self.right_panel.setFixedWidth(320)

        # ===== SIGNALS =====
        self.right_panel.log_signal.connect(self._append_log)
        self.right_panel.refresh_graph_signal.connect(self.left_panel.redraw_graph)

        content_layout.addWidget(self.left_panel, 7)
        content_layout.addWidget(self.right_panel, 3)

        root_layout.addWidget(self.background_widget)

    # ===== RESIZE HANDLING =====
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        base_width = 1200
        base_height = 750

        scale = min(
            self.width() / base_width,
            self.height() / base_height,
        )
        scale = max(1.05, min(scale, 1.7))

        vertical_padding = int(6 * scale)
        horizontal_padding = int(14 * scale)
        border_radius = int(14 * scale)
        font_size = int(12 * scale)

        scaled_theme = f"""
        QPushButton#ActionButton {{
            background-color: white;
            border-radius: {border_radius}px;
            padding: {vertical_padding}px {horizontal_padding}px;
            border: 1px solid #cfcfcf;
            font-size: {font_size}px;
        }}

        QPushButton#ActionButton:hover {{
            background-color: #f2f4f7;
        }}

        QPushButton#ActionButton:pressed {{
            background-color: #e0e4ea;
        }}

        QPushButton#SegmentButton {{
            background-color: white;
            border: 1px solid #cfcfcf;
            padding: {vertical_padding}px {int(horizontal_padding * 0.8)}px;
            border-radius: 0px;
            font-size: {font_size}px;
        }}

        QPushButton#SegmentButton:first {{
            border-top-left-radius: {int(border_radius * 0.6)}px;
            border-bottom-left-radius: {int(border_radius * 0.6)}px;
        }}

        QPushButton#SegmentButton:last {{
            border-top-right-radius: {int(border_radius * 0.6)}px;
            border-bottom-right-radius: {int(border_radius * 0.6)}px;
        }}

        QPushButton#SegmentButton:checked {{
            background-color: #6578B4;
            color: white;
            border: 1px solid #7FA4D1;
        }}

        QPushButton#SegmentButton:checked:hover {{
            background-color: #7FA4D1;
            color: white;
            border: 1px solid #6578B4;
        }}
        
        QPushButton#SegmentButton:hover {{
            background-color: #cfcfcf;
            color: white;
            border: 1px solid white;
        }}
        
        QPushButton#loadButton {{
            background-color: #52A52E;
            color: white;
            border-radius: {border_radius}px;
            padding: {vertical_padding}px {horizontal_padding}px;
            border: 1px solid #cfcfcf;
            font-size: {font_size}px;
        }}
    
        QPushButton#loadButton:hover {{
            background-color: #9EC44D;
        }}
    
        QPushButton#loadButton:pressed {{
            background-color: #9EC44D;
        }}
        """

        self.setStyleSheet(APP_THEME + scaled_theme)
