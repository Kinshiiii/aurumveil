from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QScrollArea,
    QButtonGroup,
    QMessageBox,
    QFileDialog,
    QSizePolicy,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models.storage import (
    DATA_DIRECTORY,
    RAW_DATA_DIRECTORY,
    delete_data_file,
    load_default_data,
    load_from_file,
    save_data_to_path,
    save_default_data,
    save_raw_data,
)

from ui.data_dialog import DataDialog
from ui.utils import add_shadow


class LeftPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("LeftPanel")
        self.current_file_path: str | None = None

        self._build_ui()
        self._draw_points()

    # ===== UI =====
    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        card = QWidget()
        card.setObjectName("InnerBlock")
        add_shadow(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(16)

        card_layout.addLayout(self._build_toolbar())

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        editor_container = QWidget()
        editor_container.setObjectName("InnerBlock")

        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        editor_layout.addWidget(self.canvas)

        self.stats = QTextEdit()
        self.stats.setReadOnly(True)

        stats_wrapper = QWidget()
        stats_layout = QVBoxLayout(stats_wrapper)
        stats_layout.setContentsMargins(1, 1, 1, 1)
        stats_layout.addWidget(self.stats)

        stats_scroll = QScrollArea()
        stats_scroll.setWidgetResizable(True)
        stats_scroll.setWidget(stats_wrapper)

        card_layout.addWidget(editor_container, 8)
        card_layout.addWidget(stats_scroll, 2)

        main_layout.addWidget(card)

    # ===== TOOLBAR =====
    def _build_toolbar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(8)

        def create_button(text: str) -> QPushButton:
            btn = QPushButton(text)  # ✔ fix shadow warning
            btn.setObjectName("ActionButton")
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )
            return btn

        load_button = create_button("LOAD")
        load_button.clicked.connect(self._load_file)
        layout.addWidget(load_button)

        layout.addStretch(1)

        save_button = create_button("SAVE")
        save_button.clicked.connect(self._save)
        layout.addWidget(save_button)

        save_as_button = create_button("SAVE AS")
        save_as_button.clicked.connect(self._save_as)
        layout.addWidget(save_as_button)

        layout.addStretch(1)

        enter_button = create_button("ENTER DATA")
        enter_button.clicked.connect(self._open_data_dialog)
        layout.addWidget(enter_button)

        clear_button = create_button("CLEAR")
        clear_button.clicked.connect(self._clear_data)
        layout.addWidget(clear_button)

        layout.addStretch(2)

        self.mode_group = QButtonGroup(self)

        self.btn_cached = QPushButton("Cached")
        self.btn_recompute = QPushButton("Recompute")

        for mode_btn in (self.btn_cached, self.btn_recompute):
            mode_btn.setCheckable(True)
            mode_btn.setObjectName("SegmentButton")

        self.btn_cached.setChecked(True)

        self.mode_group.addButton(self.btn_cached)
        self.mode_group.addButton(self.btn_recompute)

        layout.addWidget(self.btn_cached)
        layout.addWidget(self.btn_recompute)

        layout.addStretch()

        return layout

    def is_cached_mode(self) -> bool:
        return self.btn_cached.isChecked()

    # ===== GRAPH =====
    def _draw_points(self) -> None:
        data = load_default_data()

        if not data:
            self.figure.clear()
            self.canvas.draw()
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        for miner in data.miners:
            x, y = miner.position.x, miner.position.y
            ax.scatter(x, y, color="green", marker="o")
            ax.text(x, y, miner.identifier)

        for mine in data.mines:
            x, y = mine.location.x, mine.location.y
            ax.scatter(x, y, color="red", marker="s")
            ax.text(x, y, mine.identifier)

        ax.set_title("Points visualization")
        ax.grid()

        self.canvas.draw()

    # ===== LOAD =====
    def _load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load JSON",
            str(DATA_DIRECTORY),
            "JSON Files (*.json)",
        )

        if not path:
            return

        try:
            data = load_from_file(path)
            save_default_data(data)

            self.current_file_path = path
            self.stats.append(f"✔ Loaded: {path}")

            self._draw_points()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ===== SAVE =====
    def _save(self) -> None:
        data = load_default_data()

        if not data:
            QMessageBox.warning(self, "Warning", "No data in temporary buffer")
            return

        if self.current_file_path:
            try:
                current_path = Path(self.current_file_path).resolve()
                raw_dir = RAW_DATA_DIRECTORY.resolve()

                if current_path.parent == raw_dir:
                    new_filename = save_raw_data(data)
                    new_path = (raw_dir / new_filename).resolve()

                    if current_path.exists() and current_path != new_path:
                        current_path.unlink()

                    self.current_file_path = str(new_path)
                    self.stats.append(f"✔ RAW updated → {new_filename}")
                    self._draw_points()
                    return

                save_data_to_path(data, str(current_path))
                self.stats.append(f"✔ Saved to: {current_path}")
                self._draw_points()
                return

            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return

        filename = save_raw_data(data)
        new_path = RAW_DATA_DIRECTORY / filename

        self.current_file_path = str(new_path)
        self.stats.append(f"✔ Saved to RAW: {filename}")

        self._draw_points()

    # ===== SAVE AS =====
    def _save_as(self) -> None:
        data = load_default_data()

        if not data:
            QMessageBox.warning(self, "Warning", "No data in temporary buffer")
            return

        filename = save_raw_data(data)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            str(DATA_DIRECTORY / filename),
            "JSON Files (*.json)",
        )

        if not path:
            return

        if not path.lower().endswith(".json"):
            path += ".json"

        try:
            save_data_to_path(data, path)

            self.current_file_path = path
            self.stats.append(f"✔ Saved as: {path}")

            self._draw_points()
            self.stats.append("✔ Points updated")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ===== OTHER =====
    def _open_data_dialog(self) -> None:
        dialog = DataDialog()

        if dialog.exec():
            if self.current_file_path:
                self.stats.append(
                    f"✔ Data updated (linked: {self.current_file_path})"
                )
            else:
                self.stats.append("✔ Data saved (temp mode)")

            self._draw_points()

    def _clear_data(self) -> None:
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Delete all saved data?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            delete_data_file()
            self.current_file_path = None

            self.stats.append("🗑 Cleared → RAW mode")

            self.figure.clear()
            self.canvas.draw()