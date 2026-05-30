##
# @file content_panel.py
# @brief Visualization and dataset management panel.
#
# Provides graphical data visualization, dataset
# management operations, logging facilities, and
# result presentation for the Aurumveil platform.
#

from datetime import datetime
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    cast,
)

import matplotlib.patheffects as patheffects
import matplotlib.transforms as transforms

from matplotlib.axes import Axes

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT,
)

from matplotlib.figure import (
    Figure,
)

from matplotlib.lines import (
    Line2D,
)

from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from domain.models import (
    WorldData,
)

from domain.repository import (
    DATA_DIRECTORY,
    RAW_DATA_DIRECTORY,
    delete_data_file,
    load_default_data,
    load_from_file,
    save_data_to_path,
    save_default_data,
    save_raw_data,
)

from interface.data_dialog import (
    DataDialog,
)

from interface.widget_effects import (
    apply_shadow,
)

# ===== TYPE CHECKING =====
if TYPE_CHECKING:

    from interface.control_panel import (
        ControlPanel,
    )


##
# @file content_panel.py
# @brief Visualization and dataset management panel.
#
# Provides graphical data visualization, dataset
# management operations, logging facilities, and
# result presentation for the Aurumveil platform.
#
class ContentPanel(QWidget):

    ##
    # @brief Creates and initializes the content panel.
    #
    # Configures visualization state, creates the
    # plotting canvas, initializes the user interface,
    # loads persisted datasets, and renders the
    # initial visualization.
    #
    def __init__(self) -> None:
        super().__init__()

        # ===== WIDGET CONFIGURATION =====
        self.setObjectName(
            "ContentPanel"
        )

        # ===== FILE STATE =====
        self.current_file_path: str | None = (
            None
        )

        # ===== LOGGER STATE =====
        self.log_index: int = 0

        # ===== GRAPH STATE =====
        self.figure = Figure(
            dpi=160
        )

        self.show_labels: bool = True

        self.highlighted_mine: str | None = (
            None
        )

        # ===== USER INTERFACE =====
        self._initialize_ui()

        self.append_system_log(
            "<b>[SYSTEM]</b> System startup "
            "completed successfully"
        )

        # ===== EXISTING DATASET =====
        existing_dataset = (
            load_default_data()
        )

        if existing_dataset:

            self.append_system_log(
                "<b>[SYSTEM]</b> Existing dataset "
                "successfully loaded"
            )

        # ===== INITIAL GRAPH =====
        self._draw_points()

    ##
    # @brief Builds the content panel user interface.
    #
    # Creates the visualization canvas, navigation
    # toolbar, logging area, and all layout containers
    # required by the content panel.
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
        content_card = QWidget()

        content_card.setObjectName(
            "ContentBlock"
        )

        apply_shadow(
            content_card
        )

        content_layout = QVBoxLayout(
            content_card
        )

        content_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        content_layout.setSpacing(
            16
        )

        # ===== TOOLBAR =====
        content_layout.addLayout(
            self._build_toolbar()
        )

        # ===== GRAPH CANVAS =====
        self.figure = Figure()

        self.canvas = FigureCanvas(
            self.figure
        )

        self.toolbar = NavigationToolbar2QT(
            self.canvas,
            self,
        )

        # ===== GRAPH CONTAINER =====
        graph_container = QWidget()

        graph_container.setObjectName(
            "ContentBlock"
        )

        graph_layout = QVBoxLayout(
            graph_container
        )

        graph_layout.setContentsMargins(
            8,
            8,
            8,
            8,
        )

        graph_layout.addWidget(
            self.toolbar
        )

        graph_layout.addWidget(
            self.canvas
        )

        # ===== LOG PANEL =====
        self.stats = QTextEdit()

        self.stats.setReadOnly(
            True
        )

        self.stats.mouseDoubleClickEvent = (
            self._open_logs_window
        )

        self.stats.setToolTip(
            "Double-click to open "
            "the expanded append_system_log view."
        )

        # ===== LOG CONTAINER =====
        log_container = QWidget()

        log_layout = QVBoxLayout(
            log_container
        )

        log_layout.setContentsMargins(
            1,
            1,
            1,
            1,
        )

        log_layout.addWidget(
            self.stats
        )

        # ===== LOG SCROLL AREA =====
        log_scroll_area = QScrollArea()

        log_scroll_area.setWidgetResizable(
            True
        )

        log_scroll_area.setWidget(
            log_container
        )

        # ===== FINAL CONTENT LAYOUT =====
        content_layout.addWidget(
            graph_container,
            8,
        )

        content_layout.addWidget(
            log_scroll_area,
            2,
        )

        main_layout.addWidget(
            content_card
        )

    ##
    # @brief Creates the content panel toolbar.
    #
    # Builds file management controls, dataset actions,
    # visualization settings, and execution mode
    # selection controls.
    #
    # @return QHBoxLayout
    # Fully configured toolbar layout.
    #
    def _build_toolbar(self) -> QHBoxLayout:

        # ===== TOOLBAR LAYOUT =====
        toolbar_layout = QHBoxLayout()

        toolbar_layout.setSpacing(
            8
        )

        # ===== BUTTON FACTORY =====
        def create_toolbar_button(
            button_text: str,
        ) -> QPushButton:

            toolbar_button = QPushButton(
                button_text
            )

            toolbar_button.setObjectName(
                "SecondaryButton"
            )

            toolbar_button.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )

            return toolbar_button

        # ===== FILE ACTIONS =====
        load_button = create_toolbar_button(
            "Open"
        )

        load_button.setObjectName(
            "PrimaryButton"
        )

        load_button.clicked.connect(
            self._load_file
        )

        toolbar_layout.addWidget(
            load_button
        )

        toolbar_layout.addStretch(
            1
        )

        # ===== SAVE ACTIONS =====
        save_button = create_toolbar_button(
            "Quick Save"
        )

        save_button.clicked.connect(
            self._save
        )

        toolbar_layout.addWidget(
            save_button
        )

        save_as_button = create_toolbar_button(
            "Save To"
        )

        save_as_button.clicked.connect(
            self._save_as
        )

        toolbar_layout.addWidget(
            save_as_button
        )

        toolbar_layout.addStretch(
            1
        )

        # ===== DATA ACTIONS =====
        edit_data_button = (
            create_toolbar_button(
                "Edit Data"
            )
        )

        edit_data_button.clicked.connect(
            self._open_data_dialog
        )

        toolbar_layout.addWidget(
            edit_data_button
        )

        clear_data_button = (
            create_toolbar_button(
                "Clear"
            )
        )

        clear_data_button.clicked.connect(
            self._clear_data
        )

        toolbar_layout.addWidget(
            clear_data_button
        )

        # ===== LABEL TOGGLE =====
        self.toggle_labels_button = (
            create_toolbar_button(
                "Disable Labels"
            )
        )

        self.toggle_labels_button.clicked.connect(
            self._toggle_data_labels
        )

        toolbar_layout.addWidget(
            self.toggle_labels_button
        )

        toolbar_layout.addStretch(
            2
        )

        # ===== EXECUTION MODE =====
        self.mode_group = QButtonGroup(
            self
        )

        self.btn_cached = QPushButton(
            "Use Cache"
        )

        self.btn_recompute = QPushButton(
            "Run Analysis"
        )

        for mode_button in (
            self.btn_cached,
            self.btn_recompute,
        ):
            mode_button.setCheckable(
                True
            )

            mode_button.setObjectName(
                "SegmentButton"
            )

        self.btn_cached.setChecked(
            True
        )

        self.mode_group.addButton(
            self.btn_cached
        )

        self.mode_group.addButton(
            self.btn_recompute
        )

        toolbar_layout.addWidget(
            self.btn_cached
        )

        toolbar_layout.addWidget(
            self.btn_recompute
        )

        toolbar_layout.addStretch()

        return toolbar_layout

    ##
    # @brief Returns the current execution mode.
    #
    # Determines whether cached results should be used
    # instead of executing a fresh algorithm run.
    #
    # @return bool
    # True when cache mode is enabled.
    #
    def is_cached_mode(self) -> bool:

        return (
            self.btn_cached.isChecked()
        )


    ##
    # @brief Refreshes the graph visualization.
    #
    # Clears the current visualization and redraws
    # all entities and analytical overlays.
    #
    def redraw_graph(self) -> None:

        self._clear_graph()

        self._draw_points()

    ##
    # @brief Highlights a selected mine.
    #
    # Updates the currently highlighted mine and
    # refreshes the visualization to reflect the
    # selection state.
    #
    # @param mine_id
    # Identifier of the mine to highlight or None
    # to clear the current highlight.
    #
    def set_highlighted_mine(self, mine_id: str | None) -> None:

        self.highlighted_mine = (
            mine_id
        )

        self._draw_points()

    ##
    # @brief Renders the complete graph visualization.
    #
    # Loads the current dataset, prepares the graph,
    # renders all entities and analytical overlays,
    # and updates the visualization canvas.
    #
    def _draw_points(self) -> None:

        # ===== INPUT DATASET =====
        dataset = load_default_data()

        # ===== DATASET VALIDATION =====
        if not dataset:
            self._clear_graph()

            return

        # ===== GRAPH PREPARATION =====
        graph_axis = self._prepare_graph()

        # ===== DATA RENDERING =====
        self._draw_miners(
            graph_axis,
            dataset,
        )

        self._draw_mines(
            graph_axis,
            dataset,
        )

        # ===== CACHED RESULT =====
        cached_result = (
            self._get_cached_result()
        )

        # ===== ANALYSIS VISUALIZATION =====
        self._draw_assignments(
            graph_axis,
            cached_result,
        )

        self._draw_convex_hull(
            graph_axis,
            cached_result,
        )

        # ===== FINAL GRAPH CONFIGURATION =====
        self._build_legend(
            graph_axis,
        )

        self._configure_graph(
            graph_axis,
        )

        self.canvas.draw()

    ##
    # @brief Clears the current graph visualization.
    #
    # Removes all rendered elements from the figure
    # and refreshes the drawing canvas.
    #
    def _clear_graph(self) -> None:

        self.figure.clear()

        self.canvas.draw()

    ##
    # @brief Creates and configures a plotting area.
    #
    # Initializes the graph axes, applies visual
    # configuration, and prepares the canvas for
    # entity rendering.
    #
    # @return Axes
    # Configured matplotlib plotting axes.
    #
    def _prepare_graph(self) -> Axes:

        self.figure.clear()

        graph_axis = (
            self.figure.add_subplot(
                111
            )
        )

        graph_axis.set_title(
            "Strategic Mining Infrastructure "
            "of the Dwarven Kingdom",

            fontweight="bold",

            pad=15,
        )

        graph_axis.grid()

        graph_axis.margins(
            x=0.08,
            y=0.12,
        )

        return graph_axis

    ##
    # @brief Renders miner locations.
    #
    # Draws all miners contained in the current
    # dataset and optionally displays their
    # identifiers.
    #
    # @param graph_axis
    # Target plotting axes.
    #
    # @param dataset
    # Dataset containing miner information.
    #
    def _draw_miners(
        self,
        graph_axis: Axes,
        dataset: WorldData,
    ) -> None:

        for miner in dataset.miners:

            x_coord = (
                miner.position.x
            )

            y_coord = (
                miner.position.y
            )

            if (
                x_coord is None
                or y_coord is None
            ):
                continue

            graph_axis.scatter(
                x_coord,
                y_coord,
                color="#52A52E",
                marker="o",
                zorder=4,
            )

            if self.show_labels:
                text_transform = (
                    graph_axis.transData
                    + transforms.ScaledTranslation(
                        0,
                        4 / 72,
                        self.figure.dpi_scale_trans,
                    )
                )

                graph_axis.text(
                    x_coord,
                    y_coord,

                    str(
                        miner.identifier
                    ),

                    transform=text_transform,

                    color="white",

                    ha="center",

                    va="bottom",

                    fontsize=9,

                    fontweight="bold",

                    clip_on=True,

                    path_effects=[
                        patheffects.withStroke(
                            linewidth=3,
                            foreground="black",
                        )
                    ],
                )

    ##
    # @brief Renders mine locations.
    #
    # Draws all mining sites contained in the current
    # dataset and optionally displays their identifiers.
    # Highlighted mines are rendered using a distinct
    # visual style.
    #
    # @param graph_axis
    # Target plotting axes.
    #
    # @param dataset
    # Dataset containing mine information.
    #
    def _draw_mines(
        self,
        graph_axis: Axes,
        dataset: WorldData,
    ) -> None:

        for mine in dataset.mines:

            x_coord = (
                mine.location.x
            )

            y_coord = (
                mine.location.y
            )

            if (
                x_coord is None
                or y_coord is None
            ):
                continue

            is_highlighted = (
                mine.identifier == self.highlighted_mine
            )

            graph_axis.scatter(
                x_coord,
                y_coord,

                color=(
                    "#E80538"
                    if is_highlighted
                    else "#E87D1E"
                ),

                marker=(
                    "*"
                    if is_highlighted
                    else "s"
                ),

                s=(
                    160
                    if is_highlighted
                    else None
                ),

                linewidths=(
                    2.5
                    if is_highlighted
                    else 1.0
                ),

                zorder=4,
            )

            if self.show_labels:
                text_transform = (
                    graph_axis.transData
                    + transforms.ScaledTranslation(
                        0,
                        5 / 72,
                        self.figure.dpi_scale_trans,
                    )
                )

                graph_axis.text(
                    x_coord,
                    y_coord,

                    str(
                        mine.identifier
                    ),

                    transform=text_transform,

                    color="white",

                    ha="center",

                    va="bottom",

                    fontsize=9,

                    fontweight="bold",

                    clip_on=True,

                    path_effects=[
                        patheffects.withStroke(
                            linewidth=3,
                            foreground="black",
                        )
                    ],
                )

    ##
    # @brief Renders resource allocation assignments.
    #
    # Visualizes assignment relationships between
    # miners and mines using connection lines derived
    # from the latest optimization result.
    #
    # @param graph_axis
    # Target plotting axes.
    #
    # @param cached_result
    # Cached algorithm output containing assignment data.
    #
    @staticmethod
    def _draw_assignments(
        graph_axis: Axes,
        cached_result: dict[str, object],
    ) -> None:

        assignment_result: dict[str, object] = cast(
            dict[str, object],

            cached_result.get(
                "assignment",
                {},
            ),
        )

        dwarf_assignments: list[
            dict[str, object]
        ] = cast(
            list[dict[str, object]],

            assignment_result.get(
                "assignments",
                [],
            ) or []
        )

        for (
            assignment_index,
            assignment,
        ) in enumerate(
            dwarf_assignments
        ):
            miner_x_coord: float = float(
                cast(
                    int | float | str,
                    assignment["miner_x"],
                )
            )

            miner_y_coord: float = float(
                cast(
                    int | float | str,
                    assignment["miner_y"],
                )
            )

            mine_x_coord: float = float(
                cast(
                    int | float | str,
                    assignment["mine_x"],
                )
            )

            mine_y_coord: float = float(
                cast(
                    int | float | str,
                    assignment["mine_y"],
                )
            )

            graph_axis.plot(
                [
                    miner_x_coord,
                    mine_x_coord,
                ],

                [
                    miner_y_coord,
                    mine_y_coord,
                ],

                color="#9B7FAF",

                linewidth=1.8,

                linestyle="--",

                label=(
                    "Dwarven Logistics Network"
                    if assignment_index == 0
                    else ""
                ),

                zorder=3,
            )

    ##
    # @brief Renders the protected kingdom boundary.
    #
    # Draws the convex hull generated by the selected
    # computational geometry algorithm and annotates
    # its boundary segments.
    #
    # @param graph_axis
    # Target plotting axes.
    #
    # @param cached_result
    # Cached algorithm output containing convex hull data.
    #
    @staticmethod
    def _draw_convex_hull(
        graph_axis: Axes,
        cached_result: dict[str, object],
    ) -> None:

        geometry_result: dict[str, object] = cast(
            dict[str, object],

            cached_result.get(
                "geometry",
                {},
            ),
        )

        convex_hull_points: list[
            dict[str, object]
        ] = cast(
            list[dict[str, object]],

            geometry_result.get(
                "convex_hull",
                [],
            ),
        )

        hull_size = len(
            convex_hull_points
        )

        for edge_index in range(hull_size):
            point_a = (
                convex_hull_points[
                    edge_index
                ]
            )

            point_b = (
                convex_hull_points[
                    (
                        edge_index + 1
                    ) % hull_size
                ]
            )

            x1: float = float(
                cast(
                    int | float | str,
                    point_a["x"],
                )
            )

            y1: float = float(
                cast(
                    int | float | str,
                    point_a["y"],
                )
            )

            x2: float = float(
                cast(
                    int | float | str,
                    point_b["x"],
                )
            )

            y2: float = float(
                cast(
                    int | float | str,
                    point_b["y"],
                )
            )

            graph_axis.plot(
                [x1, x2],
                [y1, y2],

                color="#7FA4D1",

                linewidth=2,

                zorder=2,

                antialiased=True,

                label=(
                    "Protected Kingdom Boundary"

                    if edge_index == 0

                    else ""
                ),
            )

            mid_x = (
                (x1 + x2) / 2
            )

            mid_y = (
                (y1 + y2) / 2
            )

            graph_axis.text(
                mid_x,
                mid_y,

                f"B{edge_index + 1}",

                ha="center",

                va="center",

                fontsize=10,

                fontweight="bold",

                color="#2F2F2F",

                zorder=2,

                clip_on=True,

                bbox=dict(
                    facecolor="#F8F8F8",

                    edgecolor="#6578B4",

                    linewidth=1.5,

                    boxstyle="round,pad=0.45",
                ),
            )

    ##
    # @brief Creates the graph legend.
    #
    # Builds and displays a legend describing all
    # graphical entities and analytical overlays
    # rendered within the visualization.
    #
    # @param graph_axis
    # Target plotting axes.
    #
    @staticmethod
    def _build_legend(graph_axis: Axes) -> None:

        point_handles = [

            Line2D(
                [0],
                [0],

                marker="o",

                color="w",

                markerfacecolor="#52A52E",

                markersize=9,

                label="Dwarven Settlements",
            ),

            Line2D(
                [0],
                [0],

                marker="s",

                color="w",

                markerfacecolor="#E87D1E",

                markersize=9,

                label="Mining Facilities",
            ),

            Line2D(
                [0],
                [0],

                marker="*",

                color="w",

                markerfacecolor="#E80538",

                markersize=14,

                label="Noisiest Guardian",
            ),
        ]

        line_handles = [

            Line2D(
                [0],
                [0],

                color="#7FA4D1",

                linewidth=2,

                label="Protected Kingdom Boundary",
            ),

            Line2D(
                [0],
                [0],

                color="#9B7FAF",

                linewidth=1.8,

                linestyle="--",

                label="Dwarven Logistics Network",
            ),
        ]

        legend_handles = [

            point_handles[0],
            line_handles[0],

            point_handles[1],
            Line2D([], [], linestyle="none", label=""),

            point_handles[2],
            line_handles[1],
        ]

        graph_axis.legend(
            handles=legend_handles,

            loc="upper center",

            bbox_to_anchor=(
                0.5,
                -0.09,
            ),

            ncol=3,

            frameon=True,

            columnspacing=0.9,

            handlelength=1.8,

            handletextpad=0.5,

            borderaxespad=0.3,
        )

    ##
    # @brief Applies final graph configuration.
    #
    # Configures layout parameters, coordinate
    # formatting, and interactive visualization
    # behavior after all graph elements have been
    # rendered.
    #
    # @param graph_axis
    # Target plotting axes.
    #
    def _configure_graph(self, graph_axis: Axes) -> None:

        self.figure.subplots_adjust(
            bottom=0.2
        )

        graph_axis.format_coord = (
            lambda x, y: (
                f"<b>Coordinates</b> → "
                f"<b>X:</b> {x:.2f} "
                f"<b>Y:</b> {y:.2f}"
            )
        )

    ##
    # @brief Retrieves the most recent analysis result.
    #
    # Obtains the cached algorithm output stored by
    # the control panel and returns an empty result
    # when no analysis has been executed.
    #
    # @return dict[str, object]
    # Cached algorithm result.
    #
    def _get_cached_result(self) -> dict[str, object]:

        control_panel: ControlPanel | None = getattr(
            self,
            "control_panel",
            None,
        )

        if control_panel is None:
            return {}

        return (
            control_panel.cached_result
            or {}
        )


    ##
    # @brief Imports a dataset from a file.
    #
    # Opens a file selection dialogue, loads the selected
    # dataset, updates the current application state,
    # and refreshes the visualization.
    #
    def _load_file(self) -> None:

        selected_file_path, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Import Dataset",
                str(DATA_DIRECTORY),
                "Huffman Files (*.huff)",
            )
        )

        # ===== FILE VALIDATION =====
        if not selected_file_path:
            return

        try:

            # ===== DATA LOADING =====
            dataset = load_from_file(
                selected_file_path
            )

            save_default_data(
                dataset
            )

            # ===== STATE UPDATE =====
            self.current_file_path = (
                selected_file_path
            )

            self.append_system_log(
                "<b>[SYSTEM]</b> Dataset successfully "
                f"loaded: {selected_file_path}"
            )

            # ===== GRAPH REFRESH =====
            self._draw_points()

            self.append_system_log(
                "<b>[SYSTEM]</b> Visualization "
                "refreshed successfully"
            )

        # ===== IMPORT FAILURE =====
        except Exception as import_error:

            QMessageBox.critical(
                self,
                "Import Failed",
                (
                    "An unexpected error occurred "
                    "while loading the dataset:\n\n"
                    f"{import_error}"
                ),
            )

    ##
    # @brief Saves the current dataset.
    #
    # Persists the active dataset, either to its
    # existing location or to the RAW dataset
    # repository when no file association exists.
    #
    def _save(self) -> None:

        # ===== INPUT DATASET =====
        dataset = (
            self._validate_dataset_for_save()
        )

        if dataset is None:
            return

        try:

            # ===== EXISTING FILE =====
            if self.current_file_path:

                self._save_existing_dataset(
                    dataset,
                )

            # ===== NEW RAW EXPORT =====
            else:

                self._save_new_raw_dataset(
                    dataset,
                )

        # ===== SAVE FAILURE =====
        except Exception as save_error:

            self._show_save_error(
                save_error,
            )

    ##
    # @brief Exports the current dataset to a file.
    #
    # Opens a save dialogue, allows the user to choose
    # an export location, and stores the dataset as
    # a Huffman-compressed file.
    #
    def _save_as(self) -> None:

        # ===== INPUT DATASET =====
        dataset = (
            self._validate_dataset_for_save()
        )

        if dataset is None:
            return

        # ===== DEFAULT EXPORT NAME =====
        generated_filename = (
            save_raw_data(
                dataset
            )
        )

        # ===== EXPORT DIALOG =====
        selected_file_path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Export Dataset",

                str(
                    DATA_DIRECTORY
                    / generated_filename
                ),

                "Huffman Files (*.huff)",
            )
        )

        # ===== PATH VALIDATION =====
        if not selected_file_path:
            return

        if not selected_file_path.lower().endswith(".huff"):
            selected_file_path += ".huff"

        try:

            # ===== FILE EXPORT =====
            save_data_to_path(
                dataset,
                selected_file_path,
            )

            # ===== STATE UPDATE =====
            self.current_file_path = (
                selected_file_path
            )

            self.append_system_log(
                "<b>[SYSTEM]</b> Dataset successfully "
                f"saved to: {selected_file_path}"
            )

            # ===== GRAPH REFRESH =====
            self._refresh_visualization()

        # ===== EXPORT FAILURE =====
        except Exception as export_error:

            self._show_save_error(
                export_error,
            )

    ##
    # @brief Stores a new RAW dataset snapshot.
    #
    # Creates a content-addressed dataset file within
    # the RAW dataset repository and updates the
    # current file association.
    #
    # @param dataset
    # Dataset to persist.
    #
    def _save_new_raw_dataset(self, dataset: WorldData) -> None:

        generated_filename = (
            save_raw_data(
                dataset
            )
        )

        generated_file_path = (
            RAW_DATA_DIRECTORY
            / generated_filename
        )

        self.current_file_path = str(
            generated_file_path
        )

        self.append_system_log(
            "<b>[SYSTEM]</b> Dataset successfully "
            "stored in RAW directory: "
            f"{generated_filename}"
        )

    ##
    # @brief Updates an existing dataset file.
    #
    # Saves the specified dataset to the currently
    # associated file location and performs RAW
    # repository maintenance when required.
    #
    # @param dataset
    # Dataset to persist.
    #
    def _save_existing_dataset(self, dataset: WorldData) -> None:

        # ===== PATH VALIDATION =====
        if self.current_file_path is None:
            return

        current_file_path = (
            Path(
                self.current_file_path
            ).resolve()
        )

        raw_directory_path = (
            RAW_DATA_DIRECTORY.resolve()
        )

        # ===== RAW FILE UPDATE =====
        if current_file_path.parent == raw_directory_path:

            generated_filename = (
                save_raw_data(
                    dataset
                )
            )

            updated_file_path = (
                raw_directory_path
                / generated_filename
            ).resolve()

            if (
                current_file_path.exists()
                and current_file_path
                != updated_file_path
            ):
                current_file_path.unlink()

            self.current_file_path = str(
                updated_file_path
            )

            self.append_system_log(
                "<b>[SYSTEM]</b> RAW dataset "
                f"updated: {generated_filename}"
            )

            return

        # ===== STANDARD SAVE =====
        save_data_to_path(
            dataset,
            str(current_file_path),
        )

        self.append_system_log(
            "<b>[SYSTEM]</b> Dataset successfully "
            f"saved to: {current_file_path}"
        )

    ##
    # @brief Validates dataset availability.
    #
    # Ensures that a dataset is currently loaded
    # before a save operation is performed.
    #
    # @return WorldData | None
    # Dataset ready for persistence or None when
    # no dataset is available.
    #
    def _validate_dataset_for_save(self) -> WorldData | None:

        dataset = load_default_data()

        if not dataset:
            QMessageBox.warning(
                self,
                "No Data Available",
                (
                    "There is no input dataset "
                    "available for saving."
                ),
            )

            return None

        return dataset

    ##
    # @brief Refreshes the visualization.
    #
    # Clears the current graph and rebuilds the
    # complete visualization using the latest
    # dataset and analysis results.
    #
    def _refresh_visualization(self) -> None:

        self._clear_graph()

        self._draw_points()

        self.append_system_log(
            "<b>[SYSTEM]</b> Visualization "
            "refreshed successfully"
        )

    ##
    # @brief Displays a save operation error.
    #
    # Presents a dialogue describing an unexpected
    # failure encountered during dataset persistence.
    #
    # @param save_error
    # Exception describing the failure.
    #
    def _show_save_error(self, save_error: Exception) -> None:

        QMessageBox.critical(
            self,
            "Save Operation Failed",
            (
                "An unexpected error occurred "
                "while saving data:\n\n"
                f"{save_error}"
            ),
        )


    ##
    # @brief Opens the dataset editor.
    #
    # Displays the data management dialogue, detects
    # dataset modifications, invalidates outdated
    # analysis results, and refreshes the visualization.
    #
    def _open_data_dialog(self) -> None:

        # ===== DATA SNAPSHOT =====
        previous_dataset = (
            load_default_data()
        )

        # ===== EDITOR DIALOG =====
        data_dialog = DataDialog()

        if data_dialog.exec():

            updated_dataset = (
                load_default_data()
            )

            # ===== CHANGE DETECTION =====
            if previous_dataset != updated_dataset:

                self.append_system_log(
                    "<b>[SYSTEM]</b> Input dataset updated"
                )

                # ===== RESULT INVALIDATION =====
                cached_result_path = (
                    DATA_DIRECTORY
                    / "result.huff"
                )

                if hasattr(self, "control_panel"):
                    self.control_panel.cached_result = {}

                if cached_result_path.exists():

                    cached_result_path.unlink()

                    self.append_system_log(
                        "<b>[SYSTEM]</b> Previous analysis "
                        "results cleared"
                    )

                # ===== GRAPH REFRESH =====
                self._refresh_visualization()

            else:

                self.append_system_log(
                    "<b>[SYSTEM]</b> No changes detected "
                    "in the input dataset"
                )

    ##
    # @brief Handles dataset modification events.
    #
    # Invalidates cached analysis results and updates
    # the visualization after the input dataset has
    # been modified.
    #
    def _on_data_changed(self) -> None:

        # ===== CACHED RESULT =====
        cached_result_path = (
            DATA_DIRECTORY
            / "result.huff"
        )

        # ===== CACHE INVALIDATION =====
        if cached_result_path.exists():

            cached_result_path.unlink()

            self.append_system_log(
                "<b>[SYSTEM]</b> Previous analysis "
                "results cleared"
            )

        # ===== GRAPH REFRESH =====
        self._refresh_visualization()

    ##
    # @brief Removes the current dataset.
    #
    # Requests user confirmation, deletes persisted
    # runtime data, resets the current file state,
    # and clears the visualization.
    #
    def _clear_data(self) -> None:

        # ===== CONFIRMATION DIALOG =====
        user_reply = QMessageBox.question(
            self,
            "Confirm Operation",
            (
                "This action will permanently "
                "delete all saved data.\n\n"
                "Continue?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        # ===== DATA REMOVAL =====
        if user_reply == QMessageBox.StandardButton.Yes:

            delete_data_file()

            self.current_file_path = None

            self.append_system_log(
                "<b>[SYSTEM]</b> Cached results removed "
                "— RAW mode enabled"
            )

            # ===== GRAPH RESET =====
            self._clear_graph()

    ##
    # @brief Toggles point label visibility.
    #
    # Enables or disables entity labels displayed
    # within the graph visualization and refreshes
    # the rendered view.
    #
    def _toggle_data_labels(self) -> None:

        # ===== LABEL STATE =====
        self.show_labels = (
            not self.show_labels
        )

        # ===== BUTTON UPDATE =====
        self.toggle_labels_button.setText(
            "Enable Labels"
            if not self.show_labels
            else "Disable Labels"
        )

        # ===== STATUS LOG =====
        self.append_system_log(
            f"<b>[SYSTEM]</b> Point labels "
            f"<b>{'ENABLED' if self.show_labels else 'DISABLED'}</b>"
        )

        # ===== GRAPH REFRESH =====
        self._draw_points()


    ##
    # @brief Appends an entry to the system log.
    #
    # Creates a timestamped log entry and displays
    # it within the integrated log viewer.
    #
    # @param message
    # Log message to append.
    #
    def append_system_log(
        self,
        message: str,
    ) -> None:

        # ===== LOG INDEX =====
        self.log_index += 1

        # ===== TIMESTAMP =====
        current_timestamp = (
            datetime.now().strftime(
                "%H:%M:%S"
            )
        )

        # ===== LOGGER ENTRY =====
        self.stats.append(

            f"<b>{self.log_index:03d}</b> │ "

            f"<span style='color:#808080;'>"
            f"{current_timestamp}"
            f"</span> │ "

            f"{message}"
        )

    ##
    # @brief Opens the log viewer window.
    #
    # Displays the complete system log history
    # inside a dedicated dialogue window.
    #
    # @param _event
    # Mouse event triggering the action.
    #
    def _open_logs_window(
        self,
        _event,
    ) -> None:

        # ===== DIALOG WINDOW =====
        log_dialog = QDialog(
            self
        )

        log_dialog.setWindowTitle(
            "System Logs"
        )

        log_dialog.resize(
            900,
            600,
        )

        # ===== DIALOG LAYOUT =====
        dialog_layout = QVBoxLayout(
            log_dialog
        )

        # ===== LOG VIEW =====
        log_viewer = QTextEdit()

        log_viewer.setReadOnly(
            True
        )

        log_viewer.setHtml(
            self.stats.toHtml()
        )

        dialog_layout.addWidget(
            log_viewer
        )

        # ===== DISPLAY WINDOW =====
        log_dialog.exec()