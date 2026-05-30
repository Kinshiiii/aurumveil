##
# @file control_panel.py
# @brief Analysis and execution control panel.
#
# Provides algorithm configuration, execution,
# benchmarking, caching, and result management
# functionality for the Aurumveil platform.
#

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


##
# @brief Analysis control panel.
#
# Serves as the primary interface for configuring
# optimization, geometry, and range query algorithms.
#
# The panel manages algorithm execution, result
# caching, benchmarking, and communication with
# the visualization subsystem.
#
class ControlPanel(QWidget):

    ##
    # @brief Emitted when a new log entry is generated.
    #
    log_signal = Signal(str)

    ##
    # @brief Emitted when the visualization requires refreshing.
    #
    refresh_graph_signal = Signal()

    ##
    # @brief Creates and initializes the control panel.
    #
    # Configures execution state, cache management,
    # signal infrastructure, and user interface
    # components used to control algorithm execution.
    #
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

    ##
    # @brief Builds the control panel user interface.
    #
    # Creates algorithm selection controls, execution
    # parameter inputs, status indicators, and action
    # buttons used to configure and execute analyses.
    #
    # The interface provides configuration options for:
    # - maximum flow algorithms,
    # - minimum-cost pathfinding algorithms,
    # - convex hull algorithms,
    # - range query algorithms,
    # - benchmarking parameters.
    #
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

    ##
    # @brief Starts algorithm execution.
    #
    # Validates the current configuration, executes
    # the selected algorithms, collects benchmarking
    # metrics, and updates the user interface with
    # execution results.
    #
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

    ##
    # @brief Executes the selected analysis pipeline.
    #
    # Performs cache validation, executes optimization
    # and geometry algorithms when necessary, handles
    # execution errors, and stores successful results.
    #
    # @param flow_algorithm
    # Selected maximum flow algorithm.
    #
    # @param cost_algorithm
    # Selected minimum-cost pathfinding algorithm.
    #
    # @param geometry_algorithm
    # Selected convex hull algorithm.
    #
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

    ##
    # @brief Locates the loudest dwarf within a range.
    #
    # Executes the selected range query algorithm,
    # identifies the loudest dwarf contained within
    # the specified search interval, and highlights
    # the corresponding mine on the visualization.
    #
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

    ##
    # @brief Exports the current analysis result.
    #
    # Builds an export payload containing the selected
    # algorithm configuration, input dataset, and
    # analysis results, then stores it as a compressed
    # output file.
    #
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


    ##
    # @brief Returns the selected button label.
    #
    # Retrieves the text associated with the currently
    # selected button in the specified button group.
    #
    # @param group
    # Button group to inspect.
    #
    # @return str | None
    # Selected button label or None when no button
    # is selected.
    #
    @staticmethod
    def _get_selected(group: QButtonGroup) -> str | None:

        selected_button: QAbstractButton | None = (
            group.checkedButton()
        )

        if selected_button is None:
            return None

        return selected_button.text()

    ##
    # @brief Retrieves the selected algorithms.
    #
    # Obtains the currently selected flow, pathfinding,
    # and geometry algorithms and validates that all
    # required selections have been made.
    #
    # @return tuple[str, str, str] | None
    # Selected algorithm names or None when the
    # configuration is incomplete.
    #
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

    ##
    # @brief Parses a range query expression.
    #
    # Converts a textual range expression into a
    # numerical interval used by range query algorithms.
    #
    # @return tuple[int, int] | None
    # Parsed range boundaries or None when the
    # expression is invalid.
    #
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

    ##
    # @brief Validates dwarf search prerequisites.
    #
    # Ensures that a valid analysis result exists
    # before executing a range query operation.
    #
    # @return bool
    # True when the search can proceed.
    #
    def _validate_dwarf_search(self) -> bool:

        # ===== RESULT VALIDATION =====
        if not self.cached_result:
            self._set_status(
                "run analysis first"
            )

            return False

        return True

    ##
    # @brief Loads and validates the active dataset.
    #
    # Retrieves the current dataset and applies
    # failure handling when no data is available.
    #
    # @param error_message
    # Log message emitted when validation fails.
    #
    # @return WorldData | None
    # Valid dataset or None when unavailable.
    #
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


    ##
    # @brief Attempts to load a cached memory result.
    #
    # Reuses an already available execution result
    # when the current execution signature matches
    # the previously executed configuration.
    #
    # @param execution_signature
    # Unique execution signature.
    #
    # @return bool
    # True when a cached result was loaded.
    #
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

    ##
    # @brief Attempts to load a cached file result.
    #
    # Restores a previously exported analysis result
    # from persistent storage when cache mode is enabled.
    #
    # @param result_file_path
    # Cached result file location.
    #
    # @param execution_signature
    # Unique execution signature.
    #
    # @param output_filename
    # Cached output filename.
    #
    # @return bool
    # True when a cached result was loaded.
    #
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

    ##
    # @brief Executes the selected native algorithms.
    #
    # Invokes the configured optimization and geometry
    # executables and collects their results into a
    # unified response structure.
    #
    # @param dataset
    # Input dataset supplied to the algorithms.
    #
    # @param flow_algorithm
    # Selected maximum flow algorithm.
    #
    # @param cost_algorithm
    # Selected minimum-cost pathfinding algorithm.
    #
    # @param geometry_algorithm
    # Selected convex hull algorithm.
    #
    # @return dict[str, dict[str, object]]
    # Aggregated algorithm results.
    #
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

    ##
    # @brief Extracts execution errors from results.
    #
    # Scans algorithm outputs and collects formatted
    # error messages reported by failed executions.
    #
    # @param execution_result
    # Aggregated algorithm results.
    #
    # @return list[str]
    # Collection of execution error messages.
    #
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


    ##
    # @brief Updates execution status information.
    #
    # Updates the status and execution time labels
    # displayed within the control panel.
    #
    # @param result_text
    # Status message to display.
    #
    # @param time_text
    # Optional execution time value.
    #
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

    ##
    # @brief Updates action button availability.
    #
    # Enables or disables controls according to the
    # current algorithm selection and result state.
    #
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

    ##
    # @brief Resets execution state flags.
    #
    # Clears temporary execution indicators and
    # prepares the control panel for a new analysis.
    #
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

    ##
    # @brief Initializes execution status indicators.
    #
    # Updates the user interface to reflect that an
    # analysis is currently running.
    #
    def _initialize_execution_status(self) -> None:

        self._set_status(
            "running...",
            "...",
        )

    ##
    # @brief Finalizes a successful execution.
    #
    # Updates status information, logs result summaries,
    # and triggers visualization refresh operations.
    #
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


    ##
    # @brief Processes successful execution results.
    #
    # Stores execution results, updates cache metadata,
    # and enables functionality dependent on analysis
    # output.
    #
    # @param execution_result
    # Aggregated algorithm results.
    #
    # @param execution_signature
    # Unique execution signature.
    #
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

    ##
    # @brief Processes algorithm execution errors.
    #
    # Logs reported execution failures and updates
    # the control panel status accordingly.
    #
    # @param execution_errors
    # Collection of execution error messages.
    #
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

    ##
    # @brief Handles unexpected execution exceptions.
    #
    # Reports an unhandled execution failure and
    # transitions the control panel into an error state.
    #
    # @param error
    # Exception raised during execution.
    #
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

    ##
    # @brief Processes benchmark execution results.
    #
    # Updates performance statistics and dispatches
    # benchmark summaries according to the number of
    # executed iterations.
    #
    # @param execution_count
    # Number of completed executions.
    #
    # @param benchmark_metrics
    # Collected benchmark statistics.
    #
    # @param total_execution_time_ms
    # Total benchmark duration.
    #
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


    ##
    # @brief Creates benchmark metric accumulators.
    #
    # Initializes containers used to aggregate
    # performance measurements across benchmark runs.
    #
    # @return dict[str, float]
    # Initialized benchmark metrics.
    #
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

    ##
    # @brief Updates aggregated benchmark statistics.
    #
    # Extracts timing information from the current
    # execution result and accumulates benchmark metrics.
    #
    # @param benchmark_metrics
    # Metric accumulators updated in place.
    #
    # @param cached_result
    # Result containing timing information.
    #
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

    ##
    # @brief Calculates total execution duration.
    #
    # Computes the elapsed execution time in
    # milliseconds from the provided start timestamp.
    #
    # @param execution_start_time
    # Execution start timestamp.
    #
    # @return float
    # Total execution time in milliseconds.
    #
    @staticmethod
    def _calculate_total_execution_time(execution_start_time: float) -> float:

        return (
            time.perf_counter()
            - execution_start_time
        ) * 1000


    ##
    # @brief Retrieves convex hull points.
    #
    # Extracts the convex hull generated by the geometry
    # algorithm from the cached execution result.
    #
    # @return list[dict[str, object]] | None
    # Convex hull points or None when unavailable.
    #
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

    ##
    # @brief Builds a range query payload from a convex hull.
    #
    # Converts convex hull points into an ordered payload
    # containing mine locations and associated warden
    # loudness values.
    #
    # @param hull
    # Convex hull points.
    #
    # @param data
    # Input dataset.
    #
    # @return dict[str, object]
    # Ordered range query payload.
    #
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

    ##
    # @brief Executes a range query search.
    #
    # Invokes the selected range query algorithm using
    # the specified search interval and payload.
    #
    # @param selected_range_algorithm
    # Selected range query algorithm.
    #
    # @param ordered_payload
    # Ordered convex hull payload.
    #
    # @param range_start
    # Lower search boundary.
    #
    # @param range_end
    # Upper search boundary.
    #
    # @return dict[str, object]
    # Range query result.
    #
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

    ##
    # @brief Highlights the loudest dwarf location.
    #
    # Updates the graph visualization to emphasize
    # the mine associated with the detected loudest dwarf.
    #
    # @param loudest_dwarf
    # Loudest dwarf search result.
    #
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


    ##
    # @brief Resolves the associated content panel.
    #
    # Traverses the widget hierarchy and returns the
    # content panel connected to the control panel.
    #
    # @return ContentPanel | None
    # Associated content panel instance.
    #
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

    ##
    # @brief Determines the effective execution count.
    #
    # Returns the number of benchmark iterations that
    # should be executed, taking cache mode into account.
    #
    # @param execution_iterations
    # User-requested iteration count.
    #
    # @return int
    # Effective execution count.
    #
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

    ##
    # @brief Executes benchmark iterations.
    #
    # Repeatedly runs the selected algorithms and
    # accumulates benchmark performance metrics.
    #
    # @param execution_count
    # Number of executions to perform.
    #
    # @param flow_algorithm
    # Selected maximum flow algorithm.
    #
    # @param cost_algorithm
    # Selected minimum-cost pathfinding algorithm.
    #
    # @param geometry_algorithm
    # Selected geometry algorithm.
    #
    # @return dict[str, float]
    # Aggregated benchmark metrics.
    #
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

    ##
    # @brief Logs execution completion information.
    #
    # Records benchmark and execution completion
    # information in the system log.
    #
    # @param execution_iterations
    # Requested iteration count.
    #
    # @param execution_count
    # Actual execution count.
    #
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

    ##
    # @brief Processes single-run benchmark results.
    #
    # Updates execution statistics after a single
    # algorithm execution.
    #
    # @param total_execution_time_ms
    # Total execution duration.
    #
    def _handle_single_execution_results(
        self,
        total_execution_time_ms: float,
    ) -> None:

        self.time_label.setText(
            f"<b>Time:</b> "
            f"{total_execution_time_ms:.2f} ms"
        )

    ##
    # @brief Processes multi-run benchmark results.
    #
    # Computes average execution metrics and stores
    # benchmark statistics within the cached result.
    #
    # @param execution_count
    # Number of benchmark runs.
    #
    # @param benchmark_metrics
    # Aggregated benchmark metrics.
    #
    # @param total_execution_time_ms
    # Total benchmark duration.
    #
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

    ##
    # @brief Handles range query execution errors.
    #
    # Reports search failures, updates execution state,
    # and disables functionality dependent on valid
    # range query results.
    #
    # @param dwarf_search_result
    # Failed range query result.
    #
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


    ##
    # @brief Generates a unique execution signature.
    #
    # Creates deterministic identifiers based on the
    # selected algorithms and canonical dataset content.
    # The generated signature is used for cache lookup
    # and result file naming.
    #
    # @param dataset
    # Input dataset.
    #
    # @param flow_algorithm
    # Selected maximum flow algorithm.
    #
    # @param cost_algorithm
    # Selected minimum-cost pathfinding algorithm.
    #
    # @param geometry_algorithm
    # Selected geometry algorithm.
    #
    # @return tuple[str, str]
    # Execution signature and output filename.
    #
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

    ##
    # @brief Resolves the output artifact path.
    #
    # Creates the artifacts directory when necessary
    # and returns the destination path for a generated
    # result file.
    #
    # @param output_filename
    # Result filename.
    #
    # @return Path
    # Full artifact file path.
    #
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


    ##
    # @brief Builds an exportable result payload.
    #
    # Combines algorithm configuration, canonical input
    # data, and execution results into a single structure
    # suitable for persistence.
    #
    # @param flow_algorithm
    # Selected maximum flow algorithm.
    #
    # @param cost_algorithm
    # Selected minimum-cost pathfinding algorithm.
    #
    # @param geometry_algorithm
    # Selected geometry algorithm.
    #
    # @param canonical_dataset
    # Canonical dataset representation.
    #
    # @param cached_result
    # Cached execution result.
    #
    # @return dict[str, object]
    # Export payload.
    #
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

    ##
    # @brief Exports a compressed result artifact.
    #
    # Serializes the provided payload, compresses it
    # using Huffman coding, and writes the resulting
    # artifact to disk.
    #
    # @param output_file_path
    # Destination file path.
    #
    # @param export_payload
    # Payload to export.
    #
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


    ##
    # @brief Logs flow optimization results.
    #
    # Generates a formatted summary containing
    # optimization statistics, algorithm selections,
    # objective values, and execution timings.
    #
    # @param assignment_result
    # Flow optimization result.
    #
    # @param benchmark_result
    # Benchmark statistics.
    #
    # @param use_average_metrics
    # Determines whether benchmark averages or
    # single-execution timings should be reported.
    #
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

    ##
    # @brief Logs resource allocation assignments.
    #
    # Generates a formatted summary of all miner-to-mine
    # assignments produced by the flow optimization stage.
    #
    # @param assignment_entries
    # Collection of assignment records.
    #
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

    ##
    # @brief Logs geometry analysis results.
    #
    # Reports convex hull statistics and execution
    # timing information for the selected geometry
    # algorithm.
    #
    # @param geometry_result
    # Geometry analysis result.
    #
    # @param benchmark_result
    # Benchmark statistics.
    #
    # @param use_average_metrics
    # Determines whether average benchmark metrics
    # should be reported.
    #
    # @return list[dict[str, object]]
    # Convex hull points.
    #
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

    ##
    # @brief Logs convex hull boundary points.
    #
    # Outputs all points belonging to the protected
    # kingdom boundary in traversal order.
    #
    # @param convex_hull_points
    # Convex hull vertices.
    #
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

    ##
    # @brief Logs boundary route segments.
    #
    # Generates a sequential representation of the
    # inspection route formed by convex hull edges.
    #
    # @param convex_hull_points
    # Convex hull vertices.
    #
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

    ##
    # @brief Generates a complete execution report.
    #
    # Aggregates optimization, assignment, geometry,
    # and boundary information into a structured
    # execution summary written to the system log.
    #
    # @param result
    # Combined execution result.
    #
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


    ##
    # @brief Extracts dwarf information from a result entry.
    #
    # Converts a serialized dwarf record into strongly
    # typed values used by the reporting subsystem.
    #
    # @param dwarf
    # Dwarf result entry.
    #
    # @return tuple[str, int, float, float]
    # Identifier, loudness, and coordinates.
    #
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

    ##
    # @brief Logs range query search results.
    #
    # Reports the loudest detected dwarf together with
    # search statistics and execution timing.
    #
    # @param result
    # Range query result.
    #
    # @param selected_algorithm
    # Executed range query algorithm.
    #
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


    ##
    # @brief Generates a tree-structure prefix.
    #
    # Produces a textual tree connector used when
    # formatting hierarchical log entries.
    #
    # @param index
    # Current element index.
    #
    # @param size
    # Total number of elements.
    #
    # @return str
    # Tree connector prefix.
    #
    @staticmethod
    def _tree_prefix(index: int, size: int) -> str:

        return (
            "└─"
            if index == size - 1
            else "├─"
        )

    ##
    # @brief Formats an intermediate tree row.
    #
    # Creates a formatted log row representing
    # a non-terminal branch entry.
    #
    # @param label
    # Entry label.
    #
    # @param value
    # Entry value.
    #
    # @return str
    # Formatted log row.
    #
    @staticmethod
    def _branch_row(label: str, value: str) -> str:

        return (
            f"├─ {label} "
            f"{value}"
        )

    ##
    # @brief Formats an intermediate tree row.
    #
    # Creates a formatted log row representing
    # a non-terminal branch entry.
    #
    # @param label
    # Entry label.
    #
    # @param value
    # Entry value.
    #
    # @return str
    # Formatted log row.
    #
    @staticmethod
    def _terminal_row(label: str, value: str) -> str:

        return (
            f"└─ {label} "
            f"{value}"
        )