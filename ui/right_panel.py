import hashlib
import json
import time
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.compression.huffman import (
    compress_text,
    decompress_text,
)

from core.algorithm_runner import (
    problem_data_to_dict,
    run_cpp_algorithm,
)

from models.domain import Mine
from models.storage import (
    DATA_DIRECTORY,
    load_default_data,
)

from ui.left_panel import LeftPanel
from ui.utils import add_shadow

MAXFLOW_NAMES = {
    "Ford–Fulkerson Method": "Ford-Fulkerson",
    "Edmonds–Karp Method": "Edmonds-Karp",
    "Dinic Method": "Dinic",
}

MINCOST_NAMES = {
    "Bellman–Ford Method": "Bellman-Ford",
    "d'Esopo–Pape Method": "DESO",
}


class RightPanel(QWidget):
    log_signal = Signal(str)
    refresh_graph_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("RightPanel")
        self.last_result = None
        self.was_cached = False
        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        card = QWidget()
        card.setObjectName("InnerBlock")
        add_shadow(card)

        card_layout = QVBoxLayout(card)

        title = QLabel("Algorithm Configuration")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("TitleLabel")

        font = title.font()
        font.setBold(True)
        title.setFont(font)

        card_layout.addWidget(title)

        # ===== MAX FLOW =====
        self.maxflow_group = QButtonGroup(self)
        maxflow_box = QGroupBox("Flow Optimization")

        font = maxflow_box.font()
        font.setBold(True)
        maxflow_box.setFont(font)

        maxflow_layout = QVBoxLayout()

        for name in [
            "Ford–Fulkerson Method",
            "Edmonds–Karp Method",
            "Dinic Method",
        ]:
            btn = QRadioButton(name)
            self.maxflow_group.addButton(btn)
            maxflow_layout.addWidget(btn)

        for btn in self.maxflow_group.buttons():
            btn.toggled.connect(self._update_buttons_state)

        maxflow_box.setLayout(maxflow_layout)
        card_layout.addWidget(maxflow_box)

        # ===== MIN COST =====
        self.mincost_group = QButtonGroup(self)
        mincost_box = QGroupBox("Path Optimization")

        font = mincost_box.font()
        font.setBold(True)
        mincost_box.setFont(font)

        mincost_layout = QVBoxLayout()

        for name in [
            "Bellman–Ford Method",
            "d'Esopo–Pape Method",
        ]:
            btn = QRadioButton(name)
            self.mincost_group.addButton(btn)
            mincost_layout.addWidget(btn)

        for btn in self.mincost_group.buttons():
            btn.toggled.connect(self._update_buttons_state)

        mincost_box.setLayout(mincost_layout)
        card_layout.addWidget(mincost_box)

        # ===== GEOMETRY =====
        self.geo_group = QButtonGroup(self)
        geo_box = QGroupBox("Geometric Algorithms")

        font = geo_box.font()
        font.setBold(True)
        geo_box.setFont(font)

        geo_layout = QVBoxLayout()

        for name in [
            "Graham Scan Method",
            "Jarvis March Method",
            "Monotone Chain Method",
        ]:
            btn = QRadioButton(name)
            self.geo_group.addButton(btn)
            geo_layout.addWidget(btn)

        for btn in self.geo_group.buttons():
            btn.toggled.connect(self._update_buttons_state)

        geo_box.setLayout(geo_layout)
        card_layout.addWidget(geo_box)

        # ===== SEGMENT =====
        self.seg_group = QButtonGroup(self)
        self.seg_box = QGroupBox("Range Query Algorithms")
        self.seg_box.setObjectName("SegmentBox")
        seg_box = self.seg_box

        font = seg_box.font()
        font.setBold(True)
        seg_box.setFont(font)

        seg_layout = QVBoxLayout()

        btn1 = QRadioButton("Brute Force Method")
        btn2 = QRadioButton("Segment Tree Method")

        self.seg_group.addButton(btn1)
        self.seg_group.addButton(btn2)

        seg_layout.addWidget(btn1)
        seg_layout.addWidget(btn2)

        for btn in self.seg_group.buttons():
            btn.toggled.connect(self._update_buttons_state)

        seg_box.setLayout(seg_layout)
        card_layout.addWidget(seg_box)

        # ===== PARAMETERS =====
        param_box = QGroupBox("Execution Parameters")

        font = param_box.font()
        font.setBold(True)
        param_box.setFont(font)

        param_layout = QHBoxLayout()

        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g. 1-100")
        self.range_input.setFixedWidth(100)

        self.iterations_input = QSpinBox()
        self.iterations_input.setRange(1, 1_000_000)
        self.iterations_input.setValue(1)
        self.iterations_input.setFixedWidth(70)

        param_layout.addWidget(QLabel("<b>Range:</b>"))
        param_layout.addWidget(self.range_input)
        param_layout.addWidget(QLabel("<b>Runs:</b>"))
        param_layout.addWidget(self.iterations_input)

        param_box.setLayout(param_layout)
        card_layout.addWidget(param_box)

        # ===== RESULT =====
        bottom_layout = QVBoxLayout()

        info_layout = QHBoxLayout()

        self.time_label = QLabel("<b>Time:</b> ---")
        self.time_label.setObjectName("statusLabel")

        self.result_label = QLabel("<b>Status:</b> ---")
        self.result_label.setObjectName("statusLabel")
        self.result_label.setWordWrap(True)

        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.result_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        font = self.time_label.font()
        font.setBold(True)
        self.time_label.setFont(font)

        info_layout.addWidget(self.time_label, 1)
        info_layout.addWidget(self.result_label, 2)

        buttons_layout = QHBoxLayout()

        self.start_btn = QPushButton("Analyze")
        self.start_btn.setObjectName("ActionButton")
        self.start_btn.setFixedWidth(80)
        self.start_btn.clicked.connect(self.on_start)

        self.dwarf_btn = QPushButton("Locate")
        self.dwarf_btn.setObjectName("ActionButton")
        self.dwarf_btn.setEnabled(False)
        self.dwarf_btn.setFixedWidth(80)
        self.dwarf_btn.clicked.connect(self.on_find_dwarf)

        self.save_btn = QPushButton("Export")
        self.save_btn.setObjectName("ActionButton")
        self.save_btn.setFixedWidth(80)
        self.save_btn.clicked.connect(self.save_result)

        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.dwarf_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)

        bottom_layout.addLayout(info_layout)
        bottom_layout.addLayout(buttons_layout)

        card_layout.addLayout(bottom_layout)
        main_layout.addWidget(card)

        self._update_buttons_state()

    def on_start(self):
        self.dwarf_btn.setEnabled(False)
        self.was_cached = False

        maxflow = self._get_selected(self.maxflow_group)
        mincost = self._get_selected(self.mincost_group)
        geo = self._get_selected(self.geo_group)
        seg = self._get_selected(self.seg_group)

        if not (maxflow and mincost and geo):
            self.result_label.setText("<b>Status:</b> select first 3 sections")
            return

        iterations = self.iterations_input.value()

        self.result_label.setText("<b>Status:</b> running...")
        self.time_label.setText("<b>Time:</b> ...")

        start_time = time.perf_counter()

        for _ in range(iterations):
            QApplication.processEvents()
            self.run_algorithm(maxflow, mincost, geo, seg)

        if not self.last_result:
            return

        if iterations > 1:
            self.log_signal.emit(f"[SYSTEM] Total iterations executed: {iterations}")

        if not self.was_cached:
            self.log_signal.emit("[SYSTEM] Algorithm execution finished successfully")
            formatted_result = json.dumps(self.last_result, indent=4)
            self.log_signal.emit(formatted_result)

        self.result_label.setText("<b>Status:</b> success")

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        if self.was_cached:
            self.refresh_graph_signal.emit()
            return

        if iterations > 1:
            avg_time = elapsed_ms / iterations
            self.time_label.setText(f"<b>Time (AVG)</b>: {avg_time:.2f} ms")
        else:
            self.time_label.setText(f"<b>Time:</b> {elapsed_ms:.2f} ms")

        if "error" not in self.result_label.text().lower():
            self.result_label.setText("<b>Status:</b> done")
            self.refresh_graph_signal.emit()

    @staticmethod
    def _get_selected(group) -> str | None:
        button = group.checkedButton()
        return button.text() if button else None

    def _update_buttons_state(self):
        maxflow = self._get_selected(self.maxflow_group)
        mincost = self._get_selected(self.mincost_group)
        geo = self._get_selected(self.geo_group)
        seg = self._get_selected(self.seg_group)

        has_result = self.last_result is not None

        self.seg_box.setEnabled(has_result)

        for btn in self.seg_group.buttons():
            btn.setEnabled(has_result)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

        self.seg_box.style().unpolish(self.seg_box)
        self.seg_box.style().polish(self.seg_box)
        self.seg_box.update()

        self.start_btn.setEnabled(bool(maxflow and mincost and geo))
        self.dwarf_btn.setEnabled(
            has_result and seg is not None
        )

    def run_algorithm(self, maxflow, mincost, geo, seg):
        data = load_default_data()

        if not data:
            self.dwarf_btn.setEnabled(False)
            self.log_signal.emit("[SYSTEM] Input dataset not loaded")
            self.result_label.setText("<b>Status:</b> no data")
            return

        algo_string = f"{maxflow}_{mincost}_{geo}_{seg}"
        algo_hash = hashlib.sha256(algo_string.encode()).hexdigest()[:8]

        data_dict = problem_data_to_dict(data)
        raw = json.dumps(data_dict, sort_keys=True)
        data_hash = hashlib.sha256(raw.encode()).hexdigest()[:8]

        results_dir = DATA_DIRECTORY / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        filename = f"result_{algo_hash}_{data_hash}.huff"
        path = results_dir / filename

        parent: Optional[QWidget] = self.parent()

        while isinstance(parent, QWidget) and not hasattr(parent, "left_panel"):
            parent = parent.parent()

        left_panel = getattr(parent, "left_panel", None)

        if (
                isinstance(left_panel, LeftPanel)
                and left_panel.is_cached_mode()
                and path.exists()
        ):
            with open(path, "rb") as f:
                compressed = f.read()

            decoded = decompress_text(compressed)

            cached = json.loads(decoded)

            self.last_result = cached.get("result")
            self.result_label.setText("<b>Status:</b> cached")
            self.time_label.setText("<b>Time:</b> cached")

            self.log_signal.emit(f"[SYSTEM] Successfully loaded cached result: {filename}")
            self.was_cached = True

            pretty = json.dumps(cached.get("result"), indent=4)
            self.log_signal.emit(pretty)
            return

        try:
            payload = problem_data_to_dict(data)
            payload["config"] = {
                "maxflow": MAXFLOW_NAMES[maxflow],
                "mincost": MINCOST_NAMES[mincost],
            }

            result = {
                "assignment": run_cpp_algorithm("Min-Cost Max-Flow", payload),
                "geometry": run_cpp_algorithm(geo, data),
            }

            errors: list[str] = []

            for key, value in result.items():
                if isinstance(value, dict) and value.get("error"):
                    errors.append(
                        f"[{key}] ERROR: "
                        f"{value.get('stderr', '')} "
                        f"{value.get('stdout', '')}".strip()
                    )

            if errors:
                self.dwarf_btn.setEnabled(False)
                self.log_signal.emit("\n".join(errors))
                self.result_label.setText("<b>Status:</b> error")
                return

            self.result_label.setText("<b>Status:</b> during...")
            self.dwarf_btn.setEnabled(True)

            result_payload = {
                "algorithms": algo_string,
                "input": data_dict,
                "result": result,
            }

            serialized = json.dumps(
                result_payload,
                indent=4,
            )

            compressed = compress_text(serialized)

            with open(path, "wb") as f:
                f.write(compressed)

            self.last_result = result
            self._update_buttons_state()

        except Exception as e:
            self.dwarf_btn.setEnabled(False)
            self.log_signal.emit(f"[SYSTEM] Execution failed due to an exception: {e}")
            self.result_label.setText("<b>Status:</b> crash")

    @staticmethod
    def build_ordered_payload_from_hull(hull: list[dict], data) -> dict:
        mine_map = {mine.identifier: mine for mine in data.mines}

        ordered_points = []

        from typing import cast

        for point in hull:
            point_id = point["id"]

            mine = cast(Mine, mine_map.get(point_id))

            if mine is None:
                raise ValueError(f"Mining facility with ID '{point_id}' was not found")

            ordered_points.append({
                "id": mine.identifier,
                "x": mine.location.x,
                "y": mine.location.y,
                "loudness": mine.assigned_guard.loudness,
            })

        return {"points": ordered_points}

    def on_find_dwarf(self):
        data = load_default_data()

        if not self.last_result:
            self.result_label.setText("<b>Status:</b> run Start first")
            return

        if not data:
            self.dwarf_btn.setEnabled(False)
            self.log_signal.emit("[SYSTEM] No data available for analysis")
            self.result_label.setText("<b>Status:</b> no data")
            return

        seg = self._get_selected(self.seg_group)

        if seg is None:
            self.result_label.setText("<b>Status:</b> select segment algorithm")
            return

        text = self.range_input.text().strip()

        if "-" not in text:
            self.result_label.setText("<b>Status:</b> invalid range (e.g. 1-10)")
            return

        try:
            start_r, end_r = map(int, text.split("-"))
        except ValueError:
            self.result_label.setText("<b>Status:</b> invalid range")
            return

        self.result_label.setText("<b>Status:</b> searching dwarf...")
        self.time_label.setText("<b>Time:</b> ...")

        start_time = time.perf_counter()

        try:
            hull = self.last_result.get("geometry", {}).get("convex_hull", [])

            if not hull:
                self.result_label.setText("<b>Status:</b> no convex hull")
                return

            payload = self.build_ordered_payload_from_hull(hull, data)

            result = run_cpp_algorithm(seg, payload, (start_r, end_r))

            elapsed = (time.perf_counter() - start_time) * 1000
            self.time_label.setText(f"<b>Time:</b> {elapsed:.2f} ms")

            if isinstance(result, dict) and result.get("error"):
                self.result_label.setText("<b>Status:</b> error")
                self.dwarf_btn.setEnabled(False)
                self.log_signal.emit(f"[DWARF ERROR] {result.get('stderr')}")
                return

            self.result_label.setText("<b>Status:</b> dwarf found")
            self.log_signal.emit("[DWARF RESULT]")
            self.log_signal.emit(json.dumps(result, indent=4))

        except Exception as e:
            self.log_signal.emit(f"[DWARF EXCEPTION] {e}")
            self.result_label.setText("<b>Status:</b> crash")

    def save_result(self):
        data = load_default_data()

        if not self.last_result:
            self.log_signal.emit(
                "[SYSTEM] No analysis result available for export"
            )
            return

        if not data:
            self.dwarf_btn.setEnabled(False)
            self.log_signal.emit(
                "[SYSTEM] No input dataset available for export"
            )
            return

        try:
            maxflow = self._get_selected(self.maxflow_group)
            mincost = self._get_selected(self.mincost_group)
            geo = self._get_selected(self.geo_group)
            seg = self._get_selected(self.seg_group)

            algo_string = f"{maxflow}_{mincost}_{geo}_{seg}"
            algo_hash = hashlib.sha256(algo_string.encode()).hexdigest()[:8]

            data_dict = problem_data_to_dict(data)
            raw = json.dumps(data_dict, sort_keys=True)
            data_hash = hashlib.sha256(raw.encode()).hexdigest()[:8]

            results_dir = DATA_DIRECTORY / "results"
            results_dir.mkdir(parents=True, exist_ok=True)

            filename = f"result_{algo_hash}_{data_hash}.huff"
            path = results_dir / filename

            result_payload = {
                "algorithms": algo_string,
                "input": data_dict,
                "result": self.last_result,
            }

            serialized = json.dumps(
                result_payload,
                indent=4,
            )

            compressed = compress_text(serialized)

            with open(path, "wb") as f:
                f.write(compressed)

            self.log_signal.emit(f"[SYSTEM] Results successfully exported to: {filename}")

        except Exception as e:
            self.log_signal.emit(
                f"[SYSTEM] An error occurred while saving results: {e}"
            )
