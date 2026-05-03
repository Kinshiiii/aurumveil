import json
import time
import hashlib
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

from ui.left_panel import LeftPanel
from core.algorithm_runner import run_cpp_algorithm, problem_data_to_dict
from models.storage import DATA_DIRECTORY, load_default_data
from ui.utils import add_shadow


class RightPanel(QWidget):
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("RightPanel")
        self._build_ui()
        self.last_result = None
        self.was_cached = False

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        card = QWidget()
        card.setObjectName("InnerBlock")
        add_shadow(card)

        card_layout = QVBoxLayout(card)

        title = QLabel("Algorithm selection")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("TitleLabel")

        font = title.font()
        font.setBold(True)
        title.setFont(font)

        card_layout.addWidget(title)

        # ===== MAX FLOW =====
        self.maxflow_group = QButtonGroup(self)
        maxflow_box = QGroupBox("MAX FLOW")

        font = maxflow_box.font()
        font.setBold(True)
        maxflow_box.setFont(font)

        maxflow_layout = QVBoxLayout()

        for name in ["Ford-Fulkerson", "Edmonds-Karp", "Dinic", "MKM"]:
            btn = QRadioButton(name)
            self.maxflow_group.addButton(btn)
            maxflow_layout.addWidget(btn)

        for btn in self.maxflow_group.buttons():
            btn.toggled.connect(self._update_buttons_state)

        maxflow_box.setLayout(maxflow_layout)
        card_layout.addWidget(maxflow_box)

        # ===== MIN COST =====
        self.mincost_group = QButtonGroup(self)
        mincost_box = QGroupBox("MIN COST")

        font = mincost_box.font()
        font.setBold(True)
        mincost_box.setFont(font)

        mincost_layout = QVBoxLayout()

        for name in ["Dijkstra", "Bellman-Ford", "SPFA"]:
            btn = QRadioButton(name)
            self.mincost_group.addButton(btn)
            mincost_layout.addWidget(btn)

        for btn in self.mincost_group.buttons():
            btn.toggled.connect(self._update_buttons_state)

        mincost_box.setLayout(mincost_layout)
        card_layout.addWidget(mincost_box)

        # ===== GEOMETRY =====
        self.geo_group = QButtonGroup(self)
        geo_box = QGroupBox("Convex hull")

        font = geo_box.font()
        font.setBold(True)
        geo_box.setFont(font)

        geo_layout = QVBoxLayout()

        for name in [
            "Graham (quick)",
            "Graham (stable)",
            "Jarvis",
            "Monotonic Chain",
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
        seg_box = QGroupBox("Loudest dwarf")

        font = seg_box.font()
        font.setBold(True)
        seg_box.setFont(font)

        seg_layout = QVBoxLayout()

        btn1 = QRadioButton("Segment Tree")
        btn2 = QRadioButton("Brute Force")

        self.seg_group.addButton(btn1)
        self.seg_group.addButton(btn2)

        seg_layout.addWidget(btn1)
        seg_layout.addWidget(btn2)

        for btn in self.seg_group.buttons():
            btn.toggled.connect(self._update_buttons_state)

        seg_box.setLayout(seg_layout)
        card_layout.addWidget(seg_box)

        # ===== PARAMETERS =====
        param_box = QGroupBox("Parameters")
        param_layout = QHBoxLayout()

        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g. 1-100")
        self.range_input.setFixedWidth(100)

        self.iterations_input = QSpinBox()
        self.iterations_input.setRange(1, 1_000_000)
        self.iterations_input.setValue(1)
        self.iterations_input.setFixedWidth(70)

        param_layout.addWidget(QLabel("Range:"))
        param_layout.addWidget(self.range_input)
        param_layout.addWidget(QLabel("Runs:"))
        param_layout.addWidget(self.iterations_input)

        param_box.setLayout(param_layout)
        card_layout.addWidget(param_box)

        # ===== RESULT =====
        bottom_layout = QVBoxLayout()

        info_layout = QHBoxLayout()

        self.time_label = QLabel("Time: ---")
        self.result_label = QLabel("Status: ---")
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

        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("ActionButton")
        self.start_btn.setFixedWidth(80)
        self.start_btn.clicked.connect(self.on_start)

        self.dwarf_btn = QPushButton("Find dwarf")
        self.dwarf_btn.setObjectName("ActionButton")
        self.dwarf_btn.setEnabled(False)
        self.dwarf_btn.setFixedWidth(110)
        self.dwarf_btn.clicked.connect(self.on_find_dwarf)

        self.save_btn = QPushButton("Save")
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
            self.result_label.setText("Status: select first 3 sections")
            return

        iterations = self.iterations_input.value()

        self.result_label.setText("Status: running...")
        self.time_label.setText("Time: ...")

        start_time = time.perf_counter()

        for _ in range(iterations):
            QApplication.processEvents()
            self.run_algorithm(maxflow, mincost, geo, seg)

        self.result_label.setText("Status: success")

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        if self.was_cached:
            return

        if iterations > 1:
            avg_time = elapsed_ms / iterations
            self.time_label.setText(f"Time (AVG): {avg_time:.2f} ms")
        else:
            self.time_label.setText(f"Time: {elapsed_ms:.2f} ms")

        if "error" not in self.result_label.text().lower():
            self.result_label.setText("Status: done")

    @staticmethod
    def _get_selected(group) -> str | None:
        button = group.checkedButton()
        return button.text() if button else None

    def _update_buttons_state(self):
        maxflow = self._get_selected(self.maxflow_group)
        mincost = self._get_selected(self.mincost_group)
        geo = self._get_selected(self.geo_group)
        seg = self._get_selected(self.seg_group)

        self.start_btn.setEnabled(bool(maxflow and mincost and geo))
        self.dwarf_btn.setEnabled(bool(seg and self.last_result))

    def run_algorithm(self, maxflow, mincost, geo, seg):
        data = load_default_data()

        if not data:
            self.dwarf_btn.setEnabled(False)
            self.log_signal.emit("[SYSTEM] No data loaded")
            self.result_label.setText("Status: no data")
            return

        algo_string = f"{maxflow}_{mincost}_{geo}_{seg}"
        algo_hash = hashlib.sha256(algo_string.encode()).hexdigest()[:8]

        data_dict = problem_data_to_dict(data)
        raw = json.dumps(data_dict, sort_keys=True)
        data_hash = hashlib.sha256(raw.encode()).hexdigest()[:8]

        results_dir = DATA_DIRECTORY / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        filename = f"result_{algo_hash}_{data_hash}.json"
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
            with open(path, "r", encoding="utf-8") as f:
                cached = json.load(f)

            self.last_result = cached
            self.dwarf_btn.setEnabled(True)
            self.result_label.setText("Status: cached")
            self.time_label.setText("Time: cached")

            self.log_signal.emit(f"[CACHE] Loaded: {filename}")
            self.was_cached = True

            pretty = json.dumps(cached.get("result"), indent=4)
            self.log_signal.emit(pretty)
            return

        try:
            payload = problem_data_to_dict(data)
            payload["config"] = {
                "maxflow": maxflow,
                "mincost": mincost,
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
                self.result_label.setText("Status: error")
                return

            self.log_signal.emit("[SYSTEM] All algorithms executed successfully")
            self.result_label.setText("Status: during...")
            self.dwarf_btn.setEnabled(True)

            output_path = DATA_DIRECTORY / "result.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4)

            self.log_signal.emit(json.dumps(result, indent=4))
            self.last_result = result

        except Exception as e:
            self.dwarf_btn.setEnabled(False)
            self.log_signal.emit(f"[SYSTEM] Exception: {e}")
            self.result_label.setText("Status: crash")

    def on_find_dwarf(self):
        data = load_default_data()

        if not self.last_result:
            self.result_label.setText("Status: run Start first")
            return

        if not data:
            self.dwarf_btn.setEnabled(False)
            self.log_signal.emit("[SYSTEM] No data loaded")
            self.result_label.setText("Status: no data")
            return

        seg = self._get_selected(self.seg_group)

        if seg is None:
            self.result_label.setText("Status: select segment algorithm")
            return

        text = self.range_input.text().strip()

        if "-" not in text:
            self.result_label.setText("Status: invalid range (e.g. 1-10)")
            return

        try:
            start_r, end_r = map(int, text.split("-"))
        except ValueError:
            self.result_label.setText("Status: invalid range")
            return

        self.result_label.setText("Status: searching dwarf...")
        self.time_label.setText("Time: ...")

        start_time = time.perf_counter()

        try:
            result = run_cpp_algorithm(seg, data, (start_r, end_r))

            elapsed = (time.perf_counter() - start_time) * 1000
            self.time_label.setText(f"Time: {elapsed:.2f} ms")

            if isinstance(result, dict) and result.get("error"):
                self.result_label.setText("Status: error")
                self.dwarf_btn.setEnabled(False)
                self.log_signal.emit(f"[DWARF ERROR] {result.get('stderr')}")
                return

            self.result_label.setText("Status: dwarf found")
            self.log_signal.emit("[DWARF RESULT]")
            self.log_signal.emit(json.dumps(result, indent=4))

        except Exception as e:
            self.log_signal.emit(f"[DWARF EXCEPTION] {e}")
            self.result_label.setText("Status: crash")

    def save_result(self):
        data = load_default_data()

        if not self.last_result:
            self.log_signal.emit("[SYSTEM] No result to save")
            return

        if not data:
            self.dwarf_btn.setEnabled(False)
            self.log_signal.emit("[SYSTEM] No data to save")
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

            filename = f"result_{algo_hash}_{data_hash}.json"
            path = results_dir / filename

            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "algorithms": algo_string,
                        "input": data_dict,
                        "result": self.last_result,
                    },
                    f,
                    indent=4,
                )

            self.log_signal.emit(f"[SYSTEM] Saved: {filename}")

        except Exception as e:
            self.log_signal.emit(f"[SYSTEM] Save error: {e}")