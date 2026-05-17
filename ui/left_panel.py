from pathlib import Path
from datetime import datetime

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
    QDialog,
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
        self.log_index = 0
        self.figure = Figure(dpi=160)
        self.show_labels = True

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
        self.stats.mouseDoubleClickEvent = self._open_logs_window
        self.stats.setToolTip(
            "Double-click to open expanded log view"
        )

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
            btn = QPushButton(text)
            btn.setObjectName("ActionButton")
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )
            return btn

        load_button = create_button("Open")
        load_button.setObjectName("loadButton")
        load_button.clicked.connect(self._load_file)
        layout.addWidget(load_button)

        layout.addStretch(1)

        save_button = create_button("Quick Save")
        save_button.clicked.connect(self._save)
        layout.addWidget(save_button)

        save_as_button = create_button("Save To")
        save_as_button.clicked.connect(self._save_as)
        layout.addWidget(save_as_button)

        layout.addStretch(1)

        enter_button = create_button("Edit Data")
        enter_button.clicked.connect(self._open_data_dialog)
        layout.addWidget(enter_button)

        clear_button = create_button("Clear")
        clear_button.clicked.connect(self._clear_data)
        layout.addWidget(clear_button)

        self.toogle_button = create_button("Disable Labels")
        self.toogle_button.clicked.connect(
            self._toogle_data
        )
        layout.addWidget(self.toogle_button)

        layout.addStretch(2)

        self.mode_group = QButtonGroup(self)

        self.btn_cached = QPushButton("Use Cache")
        self.btn_recompute = QPushButton("Run Analysis")

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
        axis = self.figure.add_subplot(111)

        for miner in data.miners:
            x_coord = miner.position.x
            y_coord = miner.position.y

            axis.scatter(
                x_coord,
                y_coord,
                color="#52A52E",
                marker="o",
                zorder=3,
                label="Dwarven Settlements" if miner == data.miners[0] else ""
            )

            axis.scatter(x_coord, y_coord, color="#52A52E", marker="o", zorder=3)
            if self.show_labels:
                axis.text(x_coord, y_coord, miner.identifier)

        for mine in data.mines:
            x_coord = mine.location.x
            y_coord = mine.location.y

            axis.scatter(
                x_coord,
                y_coord,
                color="#E80538",
                marker="s",
                zorder=3,
                label="Mining Facilities" if mine == data.mines[0] else ""
            )

            axis.scatter(x_coord, y_coord, color="#E80538", marker="s", zorder=3)
            if self.show_labels:
                axis.text(x_coord, y_coord, mine.identifier)

        axis.set_title("Strategic Mining Infrastructure of the Dwarven Kingdom")
        axis.grid()

        right_panel = getattr(self, "right_panel", None)

        if right_panel is not None and right_panel.last_result is not None:
            convex_hull = (
                right_panel.last_result
                .get("geometry", {})
                .get("convex_hull", [])
            )

            hull_size = len(convex_hull)

            for edge_index in range(hull_size):
                point_a = convex_hull[edge_index]
                point_b = convex_hull[(edge_index + 1) % hull_size]

                x1, y1 = point_a["x"], point_a["y"]
                x2, y2 = point_b["x"], point_b["y"]

                axis.plot(
                    [x1, x2],
                    [y1, y2],
                    color="#7FA4D1",
                    linewidth=2,
                    zorder=2,
                    antialiased=True,
                    label="Protected Kingdom Boundary"
                    if edge_index == 0 else ""
                )

                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                axis.text(
                    mid_x,
                    mid_y,
                    f"B{edge_index + 1}",
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#2F2F2F",
                    zorder=4,
                    bbox=dict(
                        facecolor="#F8F8F8",
                        edgecolor="#6578B4",
                        linewidth=1.5,
                        boxstyle="round,pad=0.45"
                    )
                )

        axis.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            ncol=3,
            frameon=True
        )
        self.figure.subplots_adjust(bottom=0.2)
        self.canvas.draw()

    def redraw_graph(self) -> None:
        self._draw_points()

    # ===== LOAD =====
    def _load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Dataset",
            str(DATA_DIRECTORY),
            "Huffman Files (*.huff)",
        )

        if not path:
            return

        try:
            data = load_from_file(path)
            save_default_data(data)

            self.current_file_path = path
            self.log(f"[SYSTEM] Dataset successfully loaded: {path}")

            self._draw_points()

            self.log(
                "[SYSTEM] Visualization refreshed successfully"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"An unexpected error occurred while loading the dataset:\n\n{e}"
            )

    # ===== SAVE =====
    def _save(self) -> None:
        data = load_default_data()

        if not data:
            QMessageBox.warning(self, "No Data Available", "There is no input dataset available for saving.")
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
                    self.log(f"[SYSTEM] RAW dataset updated: {new_filename}")
                    self._draw_points()
                    return

                save_data_to_path(data, str(current_path))
                self.log(f"[SYSTEM] Dataset successfully saved to: {current_path}")
                self._draw_points()
                return

            except Exception as e:
                QMessageBox.critical(self, "Save Operation Failed", f"An unexpected error occurred while saving data:\n\n{e}")
                return

        filename = save_raw_data(data)
        new_path = RAW_DATA_DIRECTORY / filename

        self.current_file_path = str(new_path)
        self.log(f"[SYSTEM] Dataset successfully stored in RAW directory: {filename}")

        self._draw_points()

        self.log(
            "[SYSTEM] Visualization refreshed successfully"
        )

    # ===== SAVE AS =====
    def _save_as(self) -> None:
        data = load_default_data()

        if not data:
            QMessageBox.warning(self, "No Data Available", "There is no input dataset available for export.")
            return

        filename = save_raw_data(data)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Dataset",
            str(DATA_DIRECTORY / filename),
            "Huffman Files (*.huff)",
        )

        if not path:
            return

        if not path.lower().endswith(".huff"):
            path += ".huff"

        try:
            save_data_to_path(data, path)

            self.current_file_path = path
            self.log(f"[SYSTEM] Dataset successfully saved to: {path}")

            self._draw_points()
            self.log("[SYSTEM] Visualization refreshed successfully")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Operation Failed",
                f"An unexpected error occurred:\n\n{e}"
            )

    # ===== OTHER =====
    def _open_data_dialog(self) -> None:
        old_data = load_default_data()

        dialog = DataDialog()

        if dialog.exec():
            new_data = load_default_data()

            if old_data != new_data:
                self.log("[SYSTEM] Input dataset updated")

                result_path = DATA_DIRECTORY / "result.huff"
                if result_path.exists():
                    result_path.unlink()
                    self.log("[SYSTEM] Previous analysis results cleared")

                self._draw_points()
            else:
                self.log("[SYSTEM] No changes detected in the input dataset")

    def _on_data_changed(self) -> None:
        result_path = DATA_DIRECTORY / "result.huff"

        if result_path.exists():
            result_path.unlink()
            self.log("[SYSTEM] Previous analysis results cleared")

        self._draw_points()

    def _clear_data(self) -> None:
        reply = QMessageBox.question(
            self,
            "Confirm Operation",
            "This action will permanently delete all saved data.\n\nContinue?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            delete_data_file()
            self.current_file_path = None

            self.log("[SYSTEM] Cached results removed — RAW mode enabled")

            self.figure.clear()
            self.canvas.draw()

    def _toogle_data(self) -> None:
        self.show_labels = not self.show_labels

        self.toogle_button.setText(
            "Enable Labels "
            if not self.show_labels
            else "Disable Labels"
        )

        self.log(
            f"[SYSTEM] Point labels "
            f"<b>{'ENABLED' if self.show_labels else 'DISABLED'}</b>"
        )

        self._draw_points()

    def log(self, message: str) -> None:
        self.log_index += 1

        timestamp = datetime.now().strftime("%H:%M:%S")

        self.stats.append(
            f"<b>{self.log_index:03d}</b> │ "
            f"<span style='color:#808080;'>"
            f"{timestamp}"
            f"</span> │ "
            f"{message}"
        )

    def _open_logs_window(self, _event) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("System Logs")
        dialog.resize(900, 600)

        layout = QVBoxLayout(dialog)

        logs_view = QTextEdit()
        logs_view.setReadOnly(True)

        logs_view.setHtml(self.stats.toHtml())

        layout.addWidget(logs_view)

        dialog.exec()