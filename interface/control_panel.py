import hashlib
import json
import time

from pathlib import Path
from typing import cast

from PySide6.QtCore import (
    Qt,
    Signal,
)

from PySide6.QtWidgets import (
    QApplication,
    QAbstractButton,
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

from engine.orchestration.execution_engine import (
    run_cpp_algorithm,
)

from engine.compression.huffman_codec import (
    compress_text,
    decompress_text,
)

from domain.models import (
    Mine,
    WorldData,
)

from domain.repository import (
    DATA_DIRECTORY,
    load_default_data,
    to_canonical_dict,
)

from interface.content_panel import (
    ContentPanel,
)

from interface.widget_effects import (
    apply_shadow,
)

# ===== ALGORITHM NAMES =====
MAXFLOW_NAMES: dict[str, str] = {

    "Ford–Fulkerson Method": (
        "Ford-Fulkerson"
    ),

    "Edmonds-Karp Method": (
        "Edmonds-Karp"
    ),
}

MINCOST_NAMES: dict[str, str] = {

    "Bellman–Ford Method": (
        "Bellman-Ford"
    ),

    "d'Esopo–Pape Method": (
        "D'Esopo-Pape"
    ),
}


# ===== CONTROL PANEL =====
class ControlPanel(QWidget):

    # ===== SIGNALS =====
    log_signal = Signal(str)
    refresh_graph_signal = Signal()

    def __init__(self) -> None:
        super().__init__()

        # ===== WIDGET SETUP =====
        self.setObjectName(
            "ControlPanel"
        )

        # ===== CACHE STATE =====
        self.cached_result: dict[str, object] | None = (
            None
        )

        self.cache_hit: bool = (
            False
        )

        self.execution_signature: str | None = (
            None
        )

        # ===== EXECUTION STATE =====
        self.execution_failed: bool = (
            False
        )

        # ===== USER INTERFACE =====
        self._initialize_ui()

    # ===== UI INITIALIZATION =====
    def _initialize_ui(self) -> None:

        # ===== MAIN LAYOUT =====
        main_layout = QVBoxLayout(
            self
        )

        main_layout.setSpacing(
            12
        )

        main_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        # ===== MAIN CONTAINER =====
        configuration_card = QWidget()

        configuration_card.setObjectName(
            "ContentBlock"
        )

        apply_shadow(
            configuration_card
        )

        configuration_layout = QVBoxLayout(
            configuration_card
        )

        # ===== PANEL TITLE =====
        title_label = QLabel(
            "Algorithm Configuration"
        )

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title_label.setObjectName(
            "TitleLabel"
        )

        title_font = (
            title_label.font()
        )

        title_font.setBold(
            True
        )

        title_label.setFont(
            title_font
        )

        configuration_layout.addWidget(
            title_label
        )

        # ===== FLOW OPTIMIZATION =====
        self.maxflow_group = QButtonGroup(
            self
        )

        flow_optimization_box = QGroupBox(
            "Flow Optimization"
        )

        flow_box_font = (
            flow_optimization_box.font()
        )

        flow_box_font.setBold(
            True
        )

        flow_optimization_box.setFont(
            flow_box_font
        )

        flow_optimization_layout = (
            QVBoxLayout()
        )

        for flow_algorithm_name in (
            MAXFLOW_NAMES.keys()
        ):

            algorithm_button = (
                QRadioButton(
                    flow_algorithm_name
                )
            )

            if flow_algorithm_name == "Edmonds-Karp Method":
                algorithm_button.setChecked(
                    True
                )

            self.maxflow_group.addButton(
                algorithm_button
            )

            flow_optimization_layout.addWidget(
                algorithm_button
            )

        for button in self.maxflow_group.buttons():
            button.toggled.connect(
                self._update_buttons_state
            )

        flow_optimization_box.setLayout(
            flow_optimization_layout
        )

        configuration_layout.addWidget(
            flow_optimization_box
        )

        # ===== COST OPTIMIZATION =====
        self.mincost_group = QButtonGroup(
            self
        )

        cost_optimization_box = QGroupBox(
            "Path Optimization"
        )

        cost_box_font = (
            cost_optimization_box.font()
        )

        cost_box_font.setBold(
            True
        )

        cost_optimization_box.setFont(
            cost_box_font
        )

        cost_optimization_layout = (
            QVBoxLayout()
        )

        for cost_algorithm_name in (
                MINCOST_NAMES.keys()
        ):

            algorithm_button = (
                QRadioButton(
                    cost_algorithm_name
                )
            )

            if cost_algorithm_name == "d'Esopo–Pape Method":
                algorithm_button.setChecked(
                    True
                )

            self.mincost_group.addButton(
                algorithm_button
            )

            cost_optimization_layout.addWidget(
                algorithm_button
            )

        for button in self.mincost_group.buttons():
            button.toggled.connect(
                self._update_buttons_state
            )

        cost_optimization_box.setLayout(
            cost_optimization_layout
        )

        configuration_layout.addWidget(
            cost_optimization_box
        )

        # ===== GEOMETRIC ANALYSIS =====
        self.geo_group = QButtonGroup(
            self
        )

        geometry_analysis_box = QGroupBox(
            "Geometric Algorithms"
        )

        geometry_box_font = (
            geometry_analysis_box.font()
        )

        geometry_box_font.setBold(
            True
        )

        geometry_analysis_box.setFont(
            geometry_box_font
        )

        geometry_analysis_layout = (
            QVBoxLayout()
        )

        for geometry_algorithm_name in [
            "Jarvis March Method",
            "Monotone Chain Method",
            "Graham Scan Method",
        ]:
            algorithm_button = (
                QRadioButton(
                    geometry_algorithm_name
                )
            )

            if geometry_algorithm_name == "Graham Scan Method":
                algorithm_button.setChecked(
                    True
                )

            self.geo_group.addButton(
                algorithm_button
            )

            geometry_analysis_layout.addWidget(
                algorithm_button
            )

        for button in self.geo_group.buttons():
            button.toggled.connect(
                self._update_buttons_state
            )

        geometry_analysis_box.setLayout(
            geometry_analysis_layout
        )

        configuration_layout.addWidget(
            geometry_analysis_box
        )

        # ===== RANGE QUERY =====
        self.seg_group = QButtonGroup(
            self
        )

        self.seg_box = QGroupBox(
            "Range Query Algorithms"
        )

        self.seg_box.setObjectName(
            "SegmentBox"
        )

        range_query_box = (
            self.seg_box
        )

        range_query_font = (
            range_query_box.font()
        )

        range_query_font.setBold(
            True
        )

        range_query_box.setFont(
            range_query_font
        )

        range_query_layout = (
            QVBoxLayout()
        )

        brute_force_button = (
            QRadioButton(
                "Brute Force Method"
            )
        )

        segment_tree_button = (
            QRadioButton(
                "Segment Tree Method"
            )
        )

        segment_tree_button.setChecked(
            True
        )

        self.seg_group.addButton(
            brute_force_button
        )

        self.seg_group.addButton(
            segment_tree_button
        )

        range_query_layout.addWidget(
            brute_force_button
        )

        range_query_layout.addWidget(
            segment_tree_button
        )

        for button in self.seg_group.buttons():
            button.toggled.connect(
                self._update_buttons_state
            )

        range_query_box.setLayout(
            range_query_layout
        )

        configuration_layout.addWidget(
            range_query_box
        )

        # ===== EXECUTION PARAMETERS =====
        execution_parameters_box = QGroupBox(
            "Execution Parameters"
        )

        parameters_box_font = (
            execution_parameters_box.font()
        )

        parameters_box_font.setBold(
            True
        )

        execution_parameters_box.setFont(
            parameters_box_font
        )

        execution_parameters_layout = (
            QHBoxLayout()
        )

        self.range_input = QLineEdit()

        self.range_input.setPlaceholderText(
            "e.g. 1-100"
        )

        self.range_input.setFixedWidth(
            100
        )

        self.iterations_input = QSpinBox()

        self.iterations_input.setRange(
            1,
            1_000_000,
        )

        self.iterations_input.setValue(
            1
        )

        self.iterations_input.setFixedWidth(
            70
        )

        execution_parameters_layout.addWidget(
            QLabel("<b>Range:</b>")
        )

        execution_parameters_layout.addWidget(
            self.range_input
        )

        execution_parameters_layout.addWidget(
            QLabel("<b>Runs:</b>")
        )

        execution_parameters_layout.addWidget(
            self.iterations_input
        )

        execution_parameters_box.setLayout(
            execution_parameters_layout
        )

        configuration_layout.addWidget(
            execution_parameters_box
        )

        # ===== RESULT SECTION =====
        result_section_layout = (
            QVBoxLayout()
        )

        status_layout = (
            QHBoxLayout()
        )

        self.time_label = QLabel(
            "<b>Time:</b> ---"
        )

        self.time_label.setObjectName(
            "StatusLabel"
        )

        self.result_label = QLabel(
            "<b>Status:</b> ---"
        )

        self.result_label.setObjectName(
            "StatusLabel"
        )

        self.result_label.setWordWrap(
            True
        )

        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.result_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        status_label_font = (
            self.time_label.font()
        )

        status_label_font.setBold(
            True
        )

        self.time_label.setFont(
            status_label_font
        )

        status_layout.addWidget(
            self.time_label,
            1,
        )

        status_layout.addWidget(
            self.result_label,
            2,
        )

        # ===== ACTION BUTTONS =====
        action_buttons_layout = (
            QHBoxLayout()
        )

        self.start_btn = QPushButton(
            "Analyze"
        )

        self.start_btn.setObjectName(
            "AnalyzeButton"
        )

        self.start_btn.setFixedWidth(
            80
        )

        self.start_btn.clicked.connect(
            self.on_start
        )

        self.dwarf_btn = QPushButton(
            "Locate"
        )

        self.dwarf_btn.setObjectName(
            "LocateButton"
        )

        self.dwarf_btn.setEnabled(
            False
        )

        self.dwarf_btn.setFixedWidth(
            80
        )

        self.dwarf_btn.clicked.connect(
            self.on_find_loudest_dwarf
        )

        self.save_btn = QPushButton(
            "Export"
        )

        self.save_btn.setObjectName(
            "ExportButton"
        )

        self.save_btn.setFixedWidth(
            80
        )

        self.save_btn.clicked.connect(
            self.save_result
        )

        action_buttons_layout.addWidget(
            self.start_btn
        )

        action_buttons_layout.addStretch()

        action_buttons_layout.addWidget(
            self.dwarf_btn
        )

        action_buttons_layout.addStretch()

        action_buttons_layout.addWidget(
            self.save_btn
        )

        # ===== FINAL LAYOUT =====
        result_section_layout.addLayout(
            status_layout
        )

        result_section_layout.addLayout(
            action_buttons_layout
        )

        configuration_layout.addLayout(
            result_section_layout
        )

        main_layout.addWidget(
            configuration_card
        )

        # ===== INITIAL STATE =====
        self._update_buttons_state()

    # ===== ANALYSIS START =====
    def on_start(self) -> None:

        # ===== EXECUTION RESET =====
        self._reset_execution_state()

        # ===== SELECTED ALGORITHMS =====
        selected_algorithms: tuple[str, str, str] | None = (
            self._get_selected_algorithms()
        )

        if selected_algorithms is None:
            return

        (
            flow_algorithm,
            cost_algorithm,
            geometry_algorithm,
        ) = selected_algorithms

        # ===== EXECUTION SETTINGS =====
        execution_iterations: int = (
            self.iterations_input.value()
        )

        # ===== STATUS INITIALIZATION =====
        self._initialize_execution_status()

        # ===== EXECUTION TIMER =====
        execution_start_time: float = (
            time.perf_counter()
        )

        # ===== EXECUTION COUNT =====
        execution_count: int = (
            self._get_execution_count(
                execution_iterations
            )
        )

        # ===== BENCHMARK EXECUTION =====
        benchmark_metrics: dict[str, float] = (
            self._run_benchmark_iterations(
                execution_count,
                flow_algorithm,
                cost_algorithm,
                geometry_algorithm,
            )
        )

        # ===== RESULT VALIDATION =====
        if not self.cached_result:
            return

        # ===== EXECUTION LOGGING =====
        self._log_execution_completion(
            execution_iterations,
            execution_count,
        )

        # ===== TOTAL EXECUTION TIME =====
        total_execution_time_ms: float = (
            self._calculate_total_execution_time(
                execution_start_time
            )
        )

        # ===== BENCHMARK RESULTS =====
        self._handle_benchmark_results(
            execution_count,
            benchmark_metrics,
            total_execution_time_ms,
        )

        # ===== EXECUTION FINALIZATION =====
        self._finalize_execution()

    # ===== ALGORITHM EXECUTION =====
    def run_algorithm(
        self,
        flow_algorithm: str,
        cost_algorithm: str,
        geometry_algorithm: str,
    ) -> None:

        # ===== INPUT DATASET =====
        dataset: WorldData | None = (
            self._get_validated_dataset(
                "<b>[SYSTEM]</b> Input dataset not loaded"
            )
        )

        if dataset is None:
            return

        # ===== EXECUTION SIGNATURE =====
        execution_signature: str
        output_filename: str

        (
            execution_signature,
            output_filename,
        ) = self._build_execution_signature(
            dataset,
            flow_algorithm,
            cost_algorithm,
            geometry_algorithm,
        )

        # ===== RESULT FILE =====
        result_file_path: Path = (
            self._get_result_file_path(
                output_filename
            )
        )

        # ===== MEMORY CACHE =====
        if self._load_memory_cache(
            execution_signature
        ):
            return

        # ===== FILE CACHE =====
        if self._load_file_cache(
            result_file_path,
            execution_signature,
            output_filename,
        ):
            return

        try:

            # ===== EXECUTION =====
            execution_result: dict[str, dict[str, object]] = (
                self._execute_algorithms(
                    dataset,
                    flow_algorithm,
                    cost_algorithm,
                    geometry_algorithm,
                )
            )

            # ===== ERROR COLLECTION =====
            execution_errors: list[str] = (
                self._collect_execution_errors(
                    execution_result
                )
            )

            # ===== ERROR HANDLING =====
            if execution_errors:
                self._handle_execution_errors(
                    execution_errors
                )

                return

            # ===== SUCCESS =====
            self._handle_execution_success(
                execution_result,
                execution_signature,
            )

        # ===== EXECUTION FAILURE =====
        except Exception as error:

            self._handle_execution_exception(
                error
            )

    # ===== DWARF SEARCH =====
    def on_find_loudest_dwarf(self) -> None:

        self.execution_failed = (
            False
        )

        # ===== INPUT DATA =====
        dataset: WorldData | None = (
            self._get_validated_dataset(
                "<b>[SYSTEM]</b> No dataset available "
                "for analysis"
            )
        )

        if dataset is None:
            return

        # ===== VALIDATION =====
        if not self._validate_dwarf_search():
            return

        # ===== SELECTED RANGE ALGORITHM =====
        selected_range_algorithm: str | None = (
            self._get_selected(
                self.seg_group
            )
        )

        if selected_range_algorithm is None:
            self._set_status(
                "select range algorithm"
            )

            return

        # ===== RANGE PARSING =====
        parsed_range: tuple[int, int] | None = (
            self._parse_range_expression()
        )

        if parsed_range is None:
            return

        range_start: int
        range_end: int

        (
            range_start,
            range_end,
        ) = parsed_range

        # ===== STATUS UPDATE =====
        self._set_status(
            "searching...",
            "...",
        )

        # ===== EXECUTION TIMER =====
        search_start_time: float = (
            time.perf_counter()
        )

        try:

            # ===== CONVEX HULL =====
            convex_hull_points: list[
                dict[str, object]
            ] | None = (
                self._get_convex_hull_points()
            )

            if convex_hull_points is None:
                return

            # ===== PAYLOAD GENERATION =====
            ordered_payload: dict[str, object] = (
                self._build_ordered_payload_from_hull(
                    convex_hull_points,
                    dataset,
                )
            )

            # ===== RANGE QUERY EXECUTION =====
            dwarf_search_result: dict[str, object] = (
                self._execute_dwarf_search(
                    selected_range_algorithm,
                    ordered_payload,
                    range_start,
                    range_end,
                )
            )

            # ===== EXECUTION TIME =====
            total_search_time_ms: float = (
                time.perf_counter()
                - search_start_time
            ) * 1000

            self.time_label.setText(
                f"<b>Time:</b> "
                f"{total_search_time_ms:.2f} ms"
            )

            # ===== ERROR HANDLING =====
            if dwarf_search_result.get("error"):
                self._handle_dwarf_search_error(
                    dwarf_search_result
                )

                return

            # ===== SEARCH SUCCESS =====
            self._set_status(
                "search completed"
            )

            self.log_signal.emit(
                "<b>[DWARF RESULT]</b>"
            )

            self._log_dwarf_result(
                dwarf_search_result,
                selected_range_algorithm,
            )

            # ===== DWARF RESULTS =====
            detected_dwarves: list[
                dict[str, object]
            ] = cast(
                list[dict[str, object]],

                dwarf_search_result.get(
                    "loudest_mine",
                    [],
                ),
            )

            loudest_dwarf: (
                dict[str, object] | None
            ) = max(

                detected_dwarves,

                key=lambda dwarf: float(
                    cast(
                        int | float | str,
                        dwarf["loudness"],
                    )
                ),

                default=None,
            )

            # ===== GRAPH HIGHLIGHT =====
            self._highlight_loudest_dwarf(
                loudest_dwarf
            )

        # ===== EXECUTION FAILURE =====
        except Exception as execution_error:

            self.execution_failed = (
                True
            )

            self.log_signal.emit(
                "[DWARF EXCEPTION] "
                f"{execution_error}"
            )

            self._set_status(
                "crash"
            )

    # ===== RESULT EXPORT =====
    def save_result(self) -> None:

        # ===== INPUT DATASET =====
        dataset: WorldData | None = (
            self._get_validated_dataset(
                "<b>[SYSTEM]</b> No input dataset "
                "available for export"
            )
        )

        if dataset is None:
            return

        # ===== RESULT VALIDATION =====
        if not self.cached_result:
            self.log_signal.emit(
                "<b>[SYSTEM]</b> No analysis result "
                "available for export"
            )

            return

        try:

            # ===== SELECTED ALGORITHMS =====
            selected_algorithms: tuple[str, str, str] | None = (
                self._get_selected_algorithms()
            )

            if selected_algorithms is None:
                return

            (
                selected_flow_algorithm,
                selected_cost_algorithm,
                selected_geometry_algorithm,
            ) = selected_algorithms

            # ===== EXECUTION SIGNATURE =====
            output_filename: str

            (
                _,
                output_filename,
            ) = self._build_execution_signature(
                dataset,
                selected_flow_algorithm,
                selected_cost_algorithm,
                selected_geometry_algorithm,
            )

            # ===== OUTPUT FILE =====
            output_file_path: Path = (
                self._get_result_file_path(
                    output_filename
                )
            )

            # ===== CANONICAL DATA =====
            canonical_dataset: dict[str, object] = (
                to_canonical_dict(
                    dataset
                )
            )

            # ===== EXPORT PAYLOAD =====
            export_payload: dict[str, object] = (
                self._build_export_payload(
                    selected_flow_algorithm,
                    selected_cost_algorithm,
                    selected_geometry_algorithm,
                    canonical_dataset,
                    self.cached_result,
                )
            )

            # ===== FILE EXPORT =====
            self._export_compressed_payload(
                output_file_path,
                export_payload,
            )

            # ===== SUCCESS LOG =====
            self.log_signal.emit(
                "<b>[SYSTEM]</b> Results successfully "
                f"exported to: {output_file_path}"
            )

        # ===== EXPORT FAILURE =====
        except Exception as error:

            self.log_signal.emit(
                "<b>[SYSTEM]</b> Failed to export "
                f"results: {error}"
            )


    # ===== SELECTION HELPERS =====
    @staticmethod
    def _get_selected(group: QButtonGroup) -> str | None:

        selected_button: QAbstractButton | None = (
            group.checkedButton()
        )

        if selected_button is None:
            return None

        return selected_button.text()

    # ===== SELECTED ALGORITHMS =====
    def _get_selected_algorithms(self) -> tuple[str, str, str] | None:

        # ===== FLOW ALGORITHM =====
        flow_algorithm: str | None = (
            self._get_selected(
                self.maxflow_group
            )
        )

        # ===== COST ALGORITHM =====
        cost_algorithm: str | None = (
            self._get_selected(
                self.mincost_group
            )
        )

        # ===== GEOMETRY ALGORITHM =====
        geometry_algorithm: str | None = (
            self._get_selected(
                self.geo_group
            )
        )

        # ===== VALIDATION =====
        if not (
            flow_algorithm
            and cost_algorithm
            and geometry_algorithm
        ):
            self._set_status(
                "select required algorithms"
            )

            return None

        return (
            flow_algorithm,
            cost_algorithm,
            geometry_algorithm,
        )

    # ===== RANGE PARSING =====
    def _parse_range_expression(self) -> tuple[int, int] | None:

        # ===== RANGE INPUT =====
        range_expression: str = (
            self.range_input.text().strip()
        )

        if "-" not in range_expression:
            self._set_status(
                "invalid range (e.g. 1-10)"
            )

            return None

        # ===== RANGE PARSING =====
        try:

            range_start: int
            range_end: int

            range_start, range_end = map(
                int,
                range_expression.split("-"),
            )

            return (
                range_start,
                range_end,
            )

        except ValueError:

            self._set_status(
                "invalid range"
            )

            return None

    # ===== RANGE VALIDATION =====
    def _validate_dwarf_search(self) -> bool:

        # ===== RESULT VALIDATION =====
        if not self.cached_result:
            self._set_status(
                "run analysis first"
            )

            return False

        return True

    # ===== VALIDATED DATASET =====
    def _get_validated_dataset(self, error_message: str) -> WorldData | None:

        dataset: WorldData | None = (
            load_default_data()
        )

        if dataset is not None:
            return dataset

        self.execution_failed = (
            True
        )

        self.dwarf_btn.setEnabled(
            False
        )

        self.log_signal.emit(
            error_message
        )

        self._set_status(
            "no data"
        )

        return None


    # ===== MEMORY CACHE =====
    def _load_memory_cache(self, execution_signature: str) -> bool:

        content_panel: ContentPanel | None = (
            self._get_content_panel()
        )

        if not (
            content_panel is not None
            and content_panel.is_cached_mode()
            and self.execution_signature
            == execution_signature
            and self.cached_result
            is not None
        ):
            return False

        self.cache_hit = (
            True
        )

        self._set_status(
            "cached",
            "instant",
        )

        self.log_signal.emit(
            "<b>[SYSTEM]</b> Successfully loaded "
            "result from memory cache"
        )

        self._update_buttons_state()

        return True

    # ===== FILE CACHE =====
    def _load_file_cache(
        self,
        result_file_path: Path,
        execution_signature: str,
        output_filename: str,
    ) -> bool:

        content_panel: ContentPanel | None = (
            self._get_content_panel()
        )

        if not (
            content_panel is not None
            and content_panel.is_cached_mode()
            and result_file_path.exists()
        ):
            return False

        with open(
            result_file_path,
            "rb",
        ) as cached_file:

            compressed_cache_data: bytes = (
                cached_file.read()
            )

        decoded_cache_payload: str = (
            decompress_text(
                compressed_cache_data
            )
        )

        cached_payload: dict[str, object] = (
            json.loads(
                decoded_cache_payload
            )
        )

        cached_execution_result: dict[str, object] = cast(
            dict[str, object],

            cached_payload.get(
                "result",
                {},
            ),
        )

        self.cached_result = (
            cached_execution_result
        )

        self.execution_signature = (
            execution_signature
        )

        self._set_status(
            "cached",
            "cached",
        )

        if not self.cache_hit:
            self.log_signal.emit(
                "<b>[SYSTEM]</b> Successfully loaded "
                f"cached result: {output_filename}"
            )

        self.cache_hit = (
            True
        )

        self._update_buttons_state()

        return True

    # ===== ALGORITHM EXECUTION =====
    @staticmethod
    def _execute_algorithms(
        dataset: WorldData,
        flow_algorithm: str,
        cost_algorithm: str,
        geometry_algorithm: str,
    ) -> dict[str, dict[str, object]]:

        execution_payload: dict[str, object] = (
            dataset.to_dict()
        )

        execution_payload["config"] = {

            "flow_algorithm": (

                MAXFLOW_NAMES[
                    flow_algorithm
                ]
            ),

            "cost_algorithm": (

                MINCOST_NAMES[
                    cost_algorithm
                ]
            ),
        }

        return {

            "assignment": (

                run_cpp_algorithm(
                    "Min-Cost Max-Flow Method",
                    execution_payload,
                )
            ),

            "geometry": (

                run_cpp_algorithm(
                    geometry_algorithm,
                    execution_payload,
                )
            ),
        }

    # ===== EXECUTION ERRORS =====
    @staticmethod
    def _collect_execution_errors(execution_result: dict[str, dict[str, object]]) -> list[str]:

        execution_errors: list[str] = []

        for result_key, result_value in execution_result.items():

            if not isinstance(
                result_value,
                dict,
            ):
                continue

            typed_result_value: dict[str, object] = (
                result_value
            )

            if typed_result_value.get("error"):
                stderr_output: str = cast(
                    str,

                    typed_result_value.get(
                        "stderr",
                        "",
                    ),
                )

                stdout_output: str = cast(
                    str,

                    typed_result_value.get(
                        "stdout",
                        "",
                    ),
                )

                formatted_error_message: str = (
                    f"[{result_key}] ERROR: "
                    f"{stderr_output} "
                    f"{stdout_output}"
                ).strip()

                execution_errors.append(
                    formatted_error_message
                )

        return execution_errors


    # ===== STATUS UPDATE =====
    def _set_status(
        self,
        result_text: str,
        time_text: str | None = None,
    ) -> None:

        self.result_label.setText(
            f"<b>Status:</b> {result_text}"
        )

        if time_text is not None:
            self.time_label.setText(
                f"<b>Time:</b> {time_text}"
            )

    # ===== BUTTON STATE MANAGEMENT =====
    def _update_buttons_state(self) -> None:

        # ===== SELECTED FLOW ALGORITHM =====
        selected_flow_algorithm: str | None = (
            self._get_selected(
                self.maxflow_group
            )
        )

        # ===== SELECTED COST ALGORITHM =====
        selected_cost_algorithm: str | None = (
            self._get_selected(
                self.mincost_group
            )
        )

        # ===== SELECTED GEOMETRY ALGORITHM =====
        selected_geometry_algorithm: str | None = (
            self._get_selected(
                self.geo_group
            )
        )

        # ===== SELECTED RANGE ALGORITHM =====
        selected_range_algorithm: str | None = (
            self._get_selected(
                self.seg_group
            )
        )

        # ===== RESULT AVAILABILITY =====
        has_cached_result: bool = (
                self.cached_result is not None
        )

        # ===== RANGE BUTTON STATE =====
        for button in self.seg_group.buttons():
            button.setEnabled(
                has_cached_result
            )

        # ===== RANGE PANEL STATE =====
        self.seg_box.setProperty(
            "active",
            has_cached_result,
        )

        self.seg_box.style().unpolish(
            self.seg_box
        )

        self.seg_box.style().polish(
            self.seg_box
        )

        # ===== RANGE BUTTON REFRESH =====
        for button in self.seg_group.buttons():
            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )

            button.update()

        # ===== PANEL REFRESH =====
        self.seg_box.update()

        # ===== MAIN ACTION BUTTONS =====
        self.start_btn.setEnabled(

            bool(
                selected_flow_algorithm
                and selected_cost_algorithm
                and selected_geometry_algorithm
            )
        )

        self.dwarf_btn.setEnabled(

            has_cached_result
            and selected_range_algorithm is not None
        )

    # ===== EXECUTION STATE =====
    def _reset_execution_state(self) -> None:

        self.execution_failed = (
            False
        )

        self.cache_hit = (
            False
        )

        self.dwarf_btn.setEnabled(
            False
        )

    # ===== EXECUTION STATUS =====
    def _initialize_execution_status(self) -> None:

        self._set_status(
            "running...",
            "...",
        )

    # ===== EXECUTION FINALIZATION =====
    def _finalize_execution(self) -> None:

        if self.execution_failed:
            return

        self._set_status(
            "completed"
        )

        if self.cached_result is None:
            return

        self._log_result_summary(
            self.cached_result
        )

        self.refresh_graph_signal.emit()


    # ===== EXECUTION SUCCESS =====
    def _handle_execution_success(
        self,
        execution_result: dict[
            str,
            dict[str, object],
        ],
        execution_signature: str,
    ) -> None:

        self._set_status(
            "completed"
        )

        self.dwarf_btn.setEnabled(
            True
        )

        self.cached_result = (
            execution_result
        )

        self.execution_signature = (
            execution_signature
        )

        self._update_buttons_state()

    # ===== EXECUTION FAILURE =====
    def _handle_execution_errors(
        self,
        execution_errors: list[str],
    ) -> None:

        self.dwarf_btn.setEnabled(
            False
        )

        self.log_signal.emit(
            "\n".join(
                execution_errors
            )
        )

        self.execution_failed = (
            True
        )

        self._set_status(
            "error"
        )

    # ===== EXECUTION EXCEPTION =====
    def _handle_execution_exception(
        self,
        error: Exception,
    ) -> None:

        self.execution_failed = (
            True
        )

        self.dwarf_btn.setEnabled(
            False
        )

        self.log_signal.emit(
            "<b>[SYSTEM]</b> Execution failed "
            f"due to an exception: {error}"
        )

        self._set_status(
            "crash"
        )

    # ===== BENCHMARK RESULTS =====
    def _handle_benchmark_results(
        self,
        execution_count: int,
        benchmark_metrics: dict[str, float],
        total_execution_time_ms: float,
    ) -> None:

        # ===== CACHE SHORTCUT =====
        if self.cache_hit:
            self.refresh_graph_signal.emit()

            return

        # ===== MULTI EXECUTION =====
        if execution_count > 1:

            self._handle_multi_execution_results(
                execution_count,
                benchmark_metrics,
                total_execution_time_ms,
            )

        # ===== SINGLE EXECUTION =====
        else:

            self._handle_single_execution_results(
                total_execution_time_ms
            )


    # ===== BENCHMARK METRICS =====
    @staticmethod
    def _initialize_benchmark_metrics() -> dict[str, float]:

        return {

            "flow": (
                0.0
            ),

            "pathfinding": (
                0.0
            ),

            "augmentation": (
                0.0
            ),

            "geometry": (
                0.0
            ),
        }

    # ===== BENCHMARK UPDATE =====
    @staticmethod
    def _update_benchmark_metrics(
        benchmark_metrics: dict[str, float],
        cached_result: dict[str, object],
    ) -> None:

        # ===== ASSIGNMENT RESULT =====
        assignment_result: dict[str, object] = cast(
            dict[str, object],

            cached_result.get(
                "assignment",
                {},
            ),
        )

        # ===== GEOMETRY RESULT =====
        geometry_result: dict[str, object] = cast(
            dict[str, object],

            cached_result.get(
                "geometry",
                {},
            ),
        )

        # ===== FLOW METRICS =====
        total_flow_time_ms: float = float(
            cast(
                int | float | str,

                assignment_result.get(
                    "total_algorithm_time_ms",
                    0,
                ),
            )
        )

        pathfinding_time_ms: float = float(
            cast(
                int | float | str,

                assignment_result.get(
                    "pathfinding_time_ms",
                    0,
                ),
            )
        )

        augmentation_time_ms: float = float(
            cast(
                int | float | str,

                assignment_result.get(
                    "augmentation_time_ms",
                    0,
                ),
            )
        )

        # ===== GEOMETRY METRICS =====
        geometry_execution_time_ms: float = float(
            cast(
                int | float | str,

                geometry_result.get(
                    "execution_time_ms",
                    0,
                ),
            )
        )

        benchmark_metrics["flow"] += (
            total_flow_time_ms
        )

        benchmark_metrics["pathfinding"] += (
            pathfinding_time_ms
        )

        benchmark_metrics["augmentation"] += (
            augmentation_time_ms
        )

        benchmark_metrics["geometry"] += (
            geometry_execution_time_ms
        )

    # ===== EXECUTION TIME =====
    @staticmethod
    def _calculate_total_execution_time(execution_start_time: float) -> float:

        return (
            time.perf_counter()
            - execution_start_time
        ) * 1000


    # ===== CONVEX HULL =====
    def _get_convex_hull_points(self) -> list[dict[str, object]] | None:

        if self.cached_result is None:
            return None

        # ===== GEOMETRY RESULT =====
        geometry_result: dict[str, object] = cast(
            dict[str, object],

            self.cached_result.get(
                "geometry",
                {},
            ),
        )

        # ===== CONVEX HULL =====
        convex_hull_points: list[
            dict[str, object]
        ] = cast(
            list[dict[str, object]],

            geometry_result.get(
                "convex_hull",
                [],
            ),
        )

        # ===== HULL VALIDATION =====
        if not convex_hull_points:
            self._set_status(
                "no convex hull"
            )

            return None

        return convex_hull_points

    # ===== ORDERED PAYLOAD =====
    @staticmethod
    def _build_ordered_payload_from_hull(
        hull: list[dict[str, object]],
        data: WorldData,
    ) -> dict[str, object]:

        # ===== MINE LOOKUP TABLE =====
        mine_lookup: dict[str, Mine] = {

            mine.identifier: mine
            for mine in data.mines
        }

        # ===== ORDERED POINTS =====
        ordered_boundary_points: list[
            dict[str, object]
        ] = []

        for point in hull:

            point_identifier: str = cast(
                str,
                point["id"],
            )

            mine: Mine | None = (
                mine_lookup.get(
                    point_identifier
                )
            )

            if mine is None:
                raise ValueError(
                    "Mining facility with ID "
                    f"{point_identifier} "
                    "was not found"
                )

            ordered_boundary_points.append(
                {

                    "id": (
                        mine.identifier
                    ),

                    "x": (
                        mine.location.x
                    ),

                    "y": (
                        mine.location.y
                    ),

                    "loudness": (
                        mine.assigned_warden.loudness
                        if mine.assigned_warden
                        else 0
                    ),
                }
            )

        # ===== PAYLOAD EXPORT =====
        return {
            "points": (
                ordered_boundary_points
            ),
        }

    # ===== RANGE QUERY EXECUTION =====
    @staticmethod
    def _execute_dwarf_search(
        selected_range_algorithm: str,
        ordered_payload: dict[str, object],
        range_start: int,
        range_end: int,
    ) -> dict[str, object]:

        return run_cpp_algorithm(
            selected_range_algorithm,
            ordered_payload,
            (
                range_start,
                range_end,
            ),
        )

    # ===== GRAPH HIGHLIGHT =====
    def _highlight_loudest_dwarf(self, loudest_dwarf: dict[str, object] | None) -> None:

        if loudest_dwarf is None:
            return

        content_panel: ContentPanel | None = (
            self._get_content_panel()
        )

        if content_panel is None:
            return

        highlighted_mining_facility_id: str = cast(
            str,
            loudest_dwarf["id"],
        )

        content_panel.set_highlighted_mine(
            highlighted_mining_facility_id
        )


    # ===== PANEL RESOLUTION =====
    def _get_content_panel(self) -> ContentPanel | None:

        parent_widget: QWidget | None = (
            self.parent()
        )

        while (
            isinstance(
                parent_widget,
                QWidget,
            )
            and not hasattr(
                parent_widget,
                "content_panel",
            )
        ):
            parent_widget = (
                parent_widget.parent()
            )

        return getattr(
            parent_widget,
            "content_panel",
            None,
        )

    # ===== EXECUTION COUNT =====
    def _get_execution_count(self, execution_iterations: int) -> int:

        content_panel: ContentPanel | None = (
            self._get_content_panel()
        )

        return (
            1
            if (
                content_panel is not None
                and content_panel.is_cached_mode()
            )
            else execution_iterations
        )

    # ===== BENCHMARK EXECUTION =====
    def _run_benchmark_iterations(
        self,
        execution_count: int,
        flow_algorithm: str,
        cost_algorithm: str,
        geometry_algorithm: str,
    ) -> dict[str, float]:

        benchmark_metrics: dict[str, float] = (
            self._initialize_benchmark_metrics()
        )

        for _ in range(execution_count):

            QApplication.processEvents()

            self.run_algorithm(
                flow_algorithm,
                cost_algorithm,
                geometry_algorithm,
            )

            if self.cached_result is None:
                continue

            self._update_benchmark_metrics(
                benchmark_metrics,
                self.cached_result,
            )

        return benchmark_metrics

    # ===== EXECUTION LOGGING =====
    def _log_execution_completion(
        self,
        execution_iterations: int,
        execution_count: int,
    ) -> None:

        if execution_count > 1:

            self.log_signal.emit(
                "<b>[SYSTEM]</b> Total iterations "
                f"executed: {execution_iterations}"
            )

        if not self.cache_hit:

            self.log_signal.emit(
                "<b>[SYSTEM]</b> Algorithm execution "
                "finished successfully"
            )

    # ===== SINGLE EXECUTION RESULTS =====
    def _handle_single_execution_results(
        self,
        total_execution_time_ms: float,
    ) -> None:

        self.time_label.setText(
            f"<b>Time:</b> "
            f"{total_execution_time_ms:.2f} ms"
        )

    # ===== MULTI EXECUTION RESULTS =====
    def _handle_multi_execution_results(
        self,
        execution_count: int,
        benchmark_metrics: dict[str, float],
        total_execution_time_ms: float,
    ) -> None:

        average_execution_time_ms: float = (
            total_execution_time_ms
            / execution_count
        )

        self.time_label.setText(
            f"<b>Time (AVG)</b>: "
            f"{average_execution_time_ms:.2f} ms"
        )

        if self.cached_result is None:
            return

        self.cached_result["benchmark"] = {

            "avg_flow_time_ms": (
                benchmark_metrics["flow"]
                / execution_count
            ),

            "avg_pathfinding_time_ms": (
                benchmark_metrics["pathfinding"]
                / execution_count
            ),

            "avg_augmentation_time_ms": (
                benchmark_metrics["augmentation"]
                / execution_count
            ),

            "avg_geometry_time_ms": (
                benchmark_metrics["geometry"]
                / execution_count
            ),
        }

    # ===== DWARF SEARCH ERROR =====
    def _handle_dwarf_search_error(self, dwarf_search_result: dict[str, object]) -> None:

        self.execution_failed = (
            True
        )

        self._set_status(
            "error"
        )

        self.dwarf_btn.setEnabled(
            False
        )

        execution_error_message: str = cast(
            str,

            dwarf_search_result.get(
                "stderr",
                "Unknown error",
            ),
        )

        self.log_signal.emit(
            "[DWARF ERROR] "
            f"{execution_error_message}"
        )


    # ===== EXECUTION SIGNATURE =====
    @staticmethod
    def _build_execution_signature(
        dataset: WorldData,
        flow_algorithm: str,
        cost_algorithm: str,
        geometry_algorithm: str,
    ) -> tuple[str, str]:

        # ===== ALGORITHM SIGNATURE =====
        algorithm_signature: str = (

            f"{flow_algorithm}_"
            f"{cost_algorithm}_"
            f"{geometry_algorithm}"
        )

        algorithm_hash: str = (
            hashlib.sha256(
                algorithm_signature.encode()
            )
            .hexdigest()[:8]
        )

        # ===== DATA HASH =====
        canonical_dataset: dict[str, object] = (
            to_canonical_dict(
                dataset
            )
        )

        canonical_dataset_json: str = (
            json.dumps(
                canonical_dataset,

                sort_keys=True,

                separators=(
                    ",",
                    ":",
                ),
            )
        )

        data_hash: str = (
            hashlib.sha256(
                canonical_dataset_json.encode()
            )
            .hexdigest()[:8]
        )

        # ===== EXECUTION IDENTIFIERS =====
        execution_signature: str = (

            f"{algorithm_hash}_"
            f"{data_hash}"
        )

        output_filename: str = (

            f"solution_"
            f"{algorithm_hash}_"
            f"{data_hash}.huff"
        )

        return (
            execution_signature,
            output_filename,
        )

    # ===== RESULT FILE PATH =====
    @staticmethod
    def _get_result_file_path(output_filename: str) -> Path:

        results_directory: Path = (
            DATA_DIRECTORY
            / "artifacts"
        )

        results_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return (
            results_directory
            / output_filename
        )


    # ===== EXPORT PAYLOAD =====
    @staticmethod
    def _build_export_payload(
        flow_algorithm: str,
        cost_algorithm: str,
        geometry_algorithm: str,
        canonical_dataset: dict[str, object],
        cached_result: dict[str, object],
    ) -> dict[str, object]:

        return {

            "algorithms": {

                "flow": (
                    flow_algorithm
                ),

                "cost": (
                    cost_algorithm
                ),

                "geometry": (
                    geometry_algorithm
                ),
            },

            "input": (
                canonical_dataset
            ),

            "result": (
                cached_result
            ),
        }

    # ===== COMPRESSED EXPORT =====
    @staticmethod
    def _export_compressed_payload(
        output_file_path: Path,
        export_payload: dict[str, object],
    ) -> None:

        serialized_export_payload: str = (
            json.dumps(
                export_payload,
                indent=4,
            )
        )

        compressed_payload: bytes = (
            compress_text(
                serialized_export_payload
            )
        )

        with open(
            output_file_path,
            "wb",
        ) as output_file:

            output_file.write(
                compressed_payload
            )


    # ===== FLOW SUMMARY =====
    def _log_flow_summary(
        self,
        assignment_result: dict[str, object],
        benchmark_result: dict[str, object],
        use_average_metrics: bool,
    ) -> None:

        self.log_signal.emit(
            "<b>[FLOW OPTIMIZATION]</b>"
        )

        flow_algorithm_name: str = cast(
            str,

            assignment_result.get(
                "maxflow_algorithm",
                "---",
            ),
        )

        cost_algorithm_name: str = cast(
            str,

            assignment_result.get(
                "mincost_algorithm",
                "---",
            ),
        )

        maximum_flow_value: (
            str | int | float
        ) = cast(
            str | int | float,

            assignment_result.get(
                "max_flow",
                "---",
            ),
        )

        minimum_cost_value: (
            str | int | float
        ) = cast(
            str | int | float,

            assignment_result.get(
                "min_cost",
                "---",
            ),
        )

        maximum_flow: str = (
            str(maximum_flow_value)
        )

        minimum_cost: str = (
            str(minimum_cost_value)
        )

        self.log_signal.emit(
            self._branch_row(
                "Max Flow Algorithm:",
                flow_algorithm_name,
            )
        )

        self.log_signal.emit(
            self._branch_row(
                "Min Cost Algorithm:",
                cost_algorithm_name,
            )
        )

        self.log_signal.emit(
            self._branch_row(
                "Maximum Flow (Successfully Assigned Dwarves):",
                maximum_flow,
            )
        )

        self.log_signal.emit(
            self._branch_row(
                "Minimum Cost (Bowls of Porridge Needed):",
                minimum_cost,
            )
        )

        pathfinding_execution_time_ms: float = (
            float(
                cast(
                    int | float | str,

                    benchmark_result.get(
                        "avg_pathfinding_time_ms",
                        0,
                    )

                    if use_average_metrics

                    else assignment_result.get(
                        "pathfinding_time_ms",
                        0,
                    )
                )
            )
        )

        augmentation_execution_time_ms: float = (
            float(
                cast(
                    int | float | str,

                    benchmark_result.get(
                        "avg_augmentation_time_ms",
                        0,
                    )

                    if use_average_metrics

                    else assignment_result.get(
                        "augmentation_time_ms",
                        0,
                    )
                )
            )
        )

        total_flow_execution_time_ms: float = (
            float(
                cast(
                    int | float | str,

                    benchmark_result.get(
                        "avg_flow_time_ms",
                        0,
                    )

                    if use_average_metrics

                    else assignment_result.get(
                        "total_algorithm_time_ms",
                        0,
                    )
                )
            )
        )

        self.log_signal.emit(
            self._branch_row(
                "Pathfinding:",
                (
                    f"{pathfinding_execution_time_ms:.4f} "
                    "ms"
                ),
            )
        )

        self.log_signal.emit(
            self._branch_row(
                "Augmentation:",
                (
                    f"{augmentation_execution_time_ms:.4f} "
                    "ms"
                ),
            )
        )

        self.log_signal.emit(
            self._terminal_row(
                "Total:",
                (
                    f"{total_flow_execution_time_ms:.4f} "
                    "ms"
                ),
            )
        )

    # ===== ASSIGNMENT SUMMARY =====
    def _log_assignment_summary(
        self,
        assignment_entries: list[
            dict[str, object]
        ],
    ) -> None:

        if not assignment_entries:
            return

        self.log_signal.emit(
            ""
        )

        self.log_signal.emit(
            "<b>[DWARF ASSIGNMENTS]</b>"
        )

        for (
            assignment_index,
            assignment_entry,
        ) in enumerate(assignment_entries):
            row_prefix: str = (
                self._tree_prefix(
                    assignment_index,
                    len(assignment_entries),
                )
            )

            miner_identifier: str = cast(
                str,
                assignment_entry["miner"],
            )

            mine_identifier: str = cast(
                str,
                assignment_entry["mine"],
            )

            mine_position_x: float = float(
                cast(
                    int | float | str,
                    assignment_entry["mine_x"],
                )
            )

            mine_position_y: float = float(
                cast(
                    int | float | str,
                    assignment_entry["mine_y"],
                )
            )

            self.log_signal.emit(

                f"{row_prefix} "
                f"{miner_identifier} "
                f"→ "
                f"{mine_identifier} "
                f"........ "
                f"({mine_position_x}, "
                f"{mine_position_y})"
            )

    # ===== GEOMETRY SUMMARY =====
    def _log_geometry_summary(
        self,
        geometry_result: dict[str, object],
        benchmark_result: dict[str, object],
        use_average_metrics: bool,
    ) -> list[dict[str, object]]:

        convex_hull_points: list[
            dict[str, object]
        ] = cast(
            list[dict[str, object]],

            geometry_result.get(
                "convex_hull",
                [],
            ),
        )

        geometry_execution_time_ms: float = (
            float(
                cast(
                    int | float | str,

                    benchmark_result.get(
                        "avg_geometry_time_ms",
                        0,
                    )

                    if use_average_metrics

                    else geometry_result.get(
                        "execution_time_ms",
                        0,
                    )
                )
            )
        )

        self.log_signal.emit(
            ""
        )

        self.log_signal.emit(
            "<b>[GEOMETRIC ANALYSIS]</b>"
        )

        self.log_signal.emit(
            self._branch_row(
                "Convex Hull Points",
                str(
                    len(
                        convex_hull_points
                    )
                ),
            )
        )

        self.log_signal.emit(
            self._terminal_row(
                "Execution Time",
                (
                    f"{geometry_execution_time_ms:.4f} "
                    "ms"
                ),
            )
        )

        return convex_hull_points

    # ===== BOUNDARY POINTS =====
    def _log_boundary_points(
        self,
        convex_hull_points: list[dict[str, object]],
    ) -> None:

        if not convex_hull_points:
            return

        self.log_signal.emit(
            ""
        )

        self.log_signal.emit(
            "<b>[BOUNDARY POINTS]</b>"
        )

        for (
            point_index,
            boundary_point,
        ) in enumerate(convex_hull_points):

            row_prefix: str = (
                self._tree_prefix(
                    point_index,
                    len(convex_hull_points),
                )
            )

            point_identifier: str = cast(
                str,
                boundary_point["id"],
            )

            point_x: float = float(
                cast(
                    int | float | str,
                    boundary_point["x"],
                )
            )

            point_y: float = float(
                cast(
                    int | float | str,
                    boundary_point["y"],
                )
            )

            self.log_signal.emit(

                f"{row_prefix} "
                f"{point_identifier} "
                f"({point_x}, "
                f"{point_y})"
            )

    # ===== BOUNDARY SEGMENTS =====
    def _log_boundary_segments(
        self,
        convex_hull_points: list[dict[str, object]],
    ) -> None:

        if not convex_hull_points:
            return

        self.log_signal.emit(
            ""
        )

        self.log_signal.emit(
            "<b>[PRINCE'S INSPECTION ROUTE]</b>"
        )

        for segment_index in range(
            len(convex_hull_points)
        ):
            current_boundary_point: dict[
                str,
                object,
            ] = (
                convex_hull_points[
                    segment_index
                ]
            )

            next_boundary_point: dict[
                str,
                object,
            ] = (
                convex_hull_points[
                    (
                        segment_index + 1
                    )
                    % len(convex_hull_points)
                ]
            )

            row_prefix: str = (
                self._tree_prefix(
                    segment_index,
                    len(convex_hull_points),
                )
            )

            current_point_id: str = cast(
                str,
                current_boundary_point["id"],
            )

            next_point_id: str = cast(
                str,
                next_boundary_point["id"],
            )

            self.log_signal.emit(

                f"{row_prefix} "
                f"B{segment_index + 1} "
                f"........ "
                f"{current_point_id} "
                f"→ "
                f"{next_point_id}"
            )

    # ===== RESULT LOGGER =====
    def _log_result_summary(self, result: dict[str, object]) -> None:

        # ===== ASSIGNMENT RESULT =====
        assignment_result: dict[
            str,
            object,
        ] = cast(
            dict[str, object],

            result.get(
                "assignment",
                {},
            ),
        )

        # ===== ASSIGNMENT LIST =====
        assignment_entries: list[
            dict[str, object]
        ] = cast(
            list[dict[str, object]],

            assignment_result.get(
                "assignments",
                [],
            ),
        )

        # ===== GEOMETRY RESULT =====
        geometry_result: dict[
            str,
            object,
        ] = cast(
            dict[str, object],

            result.get(
                "geometry",
                {},
            ),
        )

        # ===== BENCHMARK RESULT =====
        benchmark_result: dict[
            str,
            object,
        ] = cast(
            dict[str, object],

            result.get(
                "benchmark",
                {},
            ),
        )

        use_average_metrics: bool = bool(
            benchmark_result
        )

        # ===== FLOW SUMMARY =====
        self._log_flow_summary(
            assignment_result,
            benchmark_result,
            use_average_metrics,
        )

        # ===== ASSIGNMENT SUMMARY =====
        self._log_assignment_summary(
            assignment_entries,
        )

        # ===== GEOMETRY SUMMARY =====
        convex_hull_points: list[
            dict[str, object]
        ] = self._log_geometry_summary(
            geometry_result,
            benchmark_result,
            use_average_metrics,
        )

        # ===== BOUNDARY POINTS =====
        self._log_boundary_points(
            convex_hull_points,
        )

        # ===== BOUNDARY SEGMENTS =====
        self._log_boundary_segments(
            convex_hull_points,
        )

        # ===== LOG SPACING =====
        self.log_signal.emit(
            "\n"
        )


    # ===== DWARF DATA =====
    @staticmethod
    def _extract_dwarf_data(
        dwarf: dict[str, object],
    ) -> tuple[str, int, float, float]:

        dwarf_id: str = cast(
            str,
            dwarf["id"],
        )

        dwarf_loudness: int = int(
            cast(
                int | float | str,
                dwarf["loudness"],
            )
        )

        dwarf_x: float = float(
            cast(
                int | float | str,
                dwarf["x"],
            )
        )

        dwarf_y: float = float(
            cast(
                int | float | str,
                dwarf["y"],
            )
        )

        return (
            dwarf_id,
            dwarf_loudness,
            dwarf_x,
            dwarf_y,
        )

    # ===== DWARF LOGGER =====
    def _log_dwarf_result(
        self,
        result: dict[str, object],
        selected_algorithm: str,
    ) -> None:

        # ===== DETECTED DWARVES =====
        detected_dwarves: list[
            dict[str, object]
        ] = cast(
            list[dict[str, object]],

            result.get(
                "loudest_mine",
                [],
            ),
        )

        # ===== LOUDEST DWARF =====
        loudest_dwarf: (
            dict[str, object] | None
        ) = max(

            detected_dwarves,

            key=lambda dwarf: float(
                cast(
                    int | float | str,
                    dwarf["loudness"],
                )
            ),

            default=None,
        )

        # ===== LOGGER HEADER =====
        self.log_signal.emit(
            "<b>[DWARF SEARCH]</b>"
        )

        self.log_signal.emit(
            self._branch_row(
                "Algorithm:",
                selected_algorithm,
            )
        )

        # ===== LOUDEST DWARF =====
        if loudest_dwarf is not None:

            (
                loudest_dwarf_id,
                loudest_dwarf_loudness,
                loudest_dwarf_x,
                loudest_dwarf_y,
            ) = self._extract_dwarf_data(
                loudest_dwarf
            )

            self.log_signal.emit(
                self._branch_row(
                    "Loudest Dwarf:",
                    loudest_dwarf_id,
                )
            )

            self.log_signal.emit(
                self._branch_row(
                    "Loudness:",
                    str(
                        loudest_dwarf_loudness
                    ),
                )
            )

            self.log_signal.emit(
                self._branch_row(
                    "Position:",
                    (
                        f"({loudest_dwarf_x}, "
                        f"{loudest_dwarf_y})"
                    ),
                )
            )

        execution_time_ms: float = float(
            cast(
                int | float | str,

                result.get(
                    "execution_time_ms",
                    0,
                ),
            )
        )

        # ===== EXECUTION TIME =====
        self.log_signal.emit(
            self._terminal_row(
                "Execution:",
                f"{execution_time_ms:.4f} ms",
            )
        )

        # ===== LOG SPACING =====
        self.log_signal.emit(
            "\n"
        )


    # ===== TREE PREFIX =====
    @staticmethod
    def _tree_prefix(index: int, size: int) -> str:

        return (
            "└─"
            if index == size - 1
            else "├─"
        )

    # ===== BRANCH ROW =====
    @staticmethod
    def _branch_row(label: str, value: str) -> str:

        return (
            f"├─ {label} "
            f"{value}"
        )

    # ===== TERMINAL ROW =====
    @staticmethod
    def _terminal_row(label: str, value: str) -> str:

        return (
            f"└─ {label} "
            f"{value}"
        )