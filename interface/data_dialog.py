##
# @file data_dialog.py
# @brief Data management dialogue for the Aurumveil platform.
#
# Provides functionality for viewing, editing,
# validating, and persisting miners, mines,
# and wardens stored within the application data model.
#

from pathlib import Path
from typing import cast

from PySide6.QtCore import (
    Qt,
    Signal,
)

from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
)

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from domain.models import (
    Mine,
    Miner,
    Point,
    Warden,
    WorldData,
)

from domain.repository import (
    load_default_data,
    save_default_data,
)

# ===== RESOURCES =====
RESOURCES: list[str] = [
    "Gold",
    "Coal",
    "Copper",
    "Iron",
    "Silver",
    "Diamond",
]


##
# @brief World data management dialogue.
#
# Provides an interactive interface for managing
# miners, mines, and wardens. The dialogue allows
# users to create, modify, remove, and persist
# world entities used by the optimization engine.
#
class DataDialog(QDialog):

    ##
    # @brief Emitted after world data has been modified.
    #
    data_changed = Signal()

    ##
    # @brief Creates and initializes the data dialogue.
    #
    # Configures the dialogue window, builds the user
    # interface, loads persisted world data, and
    # populates all data tables.
    #
    def __init__(self) -> None:
        super().__init__()

        # ===== WINDOW =====
        self.setWindowTitle("World Data Manager")

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

        self.resize(850, 500)

        # ===== USER INTERFACE =====
        self._initialize_ui()

        # ===== DEFAULT DATA =====
        world_data: WorldData | None = (
            load_default_data()
        )

        if world_data:
            self._load_to_tables(world_data)

    ##
    # @brief Builds the dialogue user interface.
    #
    # Creates all layouts, tables, labels, and
    # action buttons used for managing world data.
    # The method also establishes signal connections
    # and configures default widget states.
    #
    def _initialize_ui(self) -> None:

        # ===== MAIN LAYOUT =====
        main_layout: QVBoxLayout = QVBoxLayout(
            self
        )

        # ===== MINERS =====
        miners_label: QLabel = QLabel(
            "Mining Crew"
        )

        main_layout.addWidget(miners_label)

        # ===== MINER TABLE =====
        self.miners_table: QTableWidget = (
            self._build_table(
                [
                    "Identifier",
                    "Name",
                    "Resource",
                    "Position X",
                    "Position Y",
                ]
            )
        )

        main_layout.addWidget(
            self.miners_table
        )

        # ===== MIDDLE LAYOUT =====
        middle_layout: QHBoxLayout = (
            QHBoxLayout()
        )

        # ===== MINES =====
        mines_layout: QVBoxLayout = (
            QVBoxLayout()
        )

        mines_label: QLabel = QLabel(
            "Mining Sites"
        )

        mines_layout.addWidget(mines_label)

        self.mines_table: QTableWidget = (
            self._build_table(
                [
                    "Identifier",
                    "Resource",
                    "Resource Capacity",
                    "Position X",
                    "Position Y",
                ]
            )
        )

        self.mines_table.setColumnWidth(
            2,
            120,
        )

        mines_layout.addWidget(
            self.mines_table
        )

        # ===== WARDENS =====
        wardens_layout: QVBoxLayout = (
            QVBoxLayout()
        )

        wardens_label: QLabel = QLabel(
            "Defense Wardens"
        )

        wardens_layout.addWidget(
            wardens_label
        )

        # ===== WARDEN TABLE =====
        self.wardens_table: QTableWidget = (
            self._build_table(
                [
                    "Identifier",
                    "Alert Volume",
                ]
            )
        )

        wardens_layout.addWidget(
            self.wardens_table
        )

        # ===== MIDDLE CONTENT =====
        middle_layout.addLayout(
            mines_layout,
            2,
        )

        middle_layout.addLayout(
            wardens_layout,
            1,
        )

        main_layout.addLayout(
            middle_layout
        )

        # ===== BUTTON LAYOUT =====
        button_layout: QHBoxLayout = (
            QHBoxLayout()
        )

        # ===== ACTION BUTTONS =====
        add_miner_button: QPushButton = (
            QPushButton("Assign Miner")
        )

        add_mine_button: QPushButton = (
            QPushButton("Assign Mine")
        )

        self.delete_miner_button: QPushButton = (
            QPushButton("Dismiss Miner")
        )

        self.delete_mine_button: QPushButton = (
            QPushButton("Abandon Mine")
        )

        # ===== BUTTON STYLES =====
        for button in (
            add_miner_button,
            add_mine_button,
            self.delete_miner_button,
            self.delete_mine_button,
        ):
            button.setObjectName("SecondaryButton")

            button.setFixedWidth(120)
            button.setFixedHeight(30)

        # ===== DEFAULT STATES =====
        self.delete_miner_button.setEnabled(
            False
        )

        self.delete_mine_button.setEnabled(
            False
        )

        # ===== BUTTON SIGNALS =====
        add_miner_button.clicked.connect(
            self._add_miner
        )

        add_mine_button.clicked.connect(
            self._add_mine
        )

        self.delete_miner_button.clicked.connect(
            lambda: self._remove_selected_rows(
                self.miners_table
            )
        )

        self.delete_mine_button.clicked.connect(
            self._delete_selected_mines
        )

        # ===== TABLE SIGNALS =====
        self.miners_table.itemSelectionChanged.connect(
            self._update_delete_buttons
        )

        self.mines_table.itemSelectionChanged.connect(
            self._update_delete_buttons
        )

        # ===== CONFIRM BUTTON =====
        confirm_button: QPushButton = (
            QPushButton("Apply Changes")
        )

        confirm_button.setObjectName(
            "PrimaryButton"
        )

        confirm_button.clicked.connect(
            self._save
        )

        # ===== BUTTON LAYOUT =====
        button_layout.addWidget(
            add_miner_button
        )

        button_layout.addWidget(
            add_mine_button
        )

        button_layout.addWidget(
            self.delete_miner_button
        )

        button_layout.addWidget(
            self.delete_mine_button
        )

        button_layout.addStretch()

        button_layout.addWidget(
            confirm_button
        )

        # ===== MAIN LAYOUT =====
        main_layout.addLayout(
            button_layout
        )

    ##
    # @brief Creates and configures a table widget.
    #
    # Initializes a table with the specified column
    # headers and configures row-based multi-selection.
    #
    # @param headers
    # Column header labels displayed by the table.
    #
    # @return QTableWidget
    # Configured table widget instance.
    #
    @staticmethod
    def _build_table(headers: list[str]) -> QTableWidget:

        # ===== TABLE WIDGET =====
        table_widget: QTableWidget = QTableWidget(
            0,
            len(headers),
        )

        # ===== TABLE HEADERS =====
        table_widget.setHorizontalHeaderLabels(
            headers
        )

        # ===== ROW SELECTION =====
        table_widget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # ===== MULTI SELECTION =====
        table_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )

        return table_widget

    ##
    # @brief Creates a read-only identifier table item.
    #
    # Generates a bold table item intended for displaying
    # immutable entity identifiers.
    #
    # @param text
    # Identifier text displayed by the item.
    #
    # @return QTableWidgetItem
    # Configured identifier table item.
    #
    @staticmethod
    def _build_identifier_item(text: str) -> QTableWidgetItem:

        # ===== TABLE ITEM =====
        table_item: QTableWidgetItem = (
            QTableWidgetItem(text)
        )

        # ===== ITEM FONT =====
        font: QFont = QFont()
        font.setBold(True)

        table_item.setFont(font)

        # ===== READ ONLY =====
        table_item.setFlags(
            Qt.ItemFlag.ItemIsEnabled
        )

        return table_item

    ##
    # @brief Safely converts text to a floating-point value.
    #
    # Returns zero when the provided value cannot be
    # converted to a valid floating-point number.
    #
    # @param input_value
    # Text representation of a numeric value.
    #
    # @return float
    # Parsed floating-point value or zero.
    #
    @staticmethod
    def _safe_float(input_value: str) -> float:

        try:
            return float(input_value)

        except ValueError:
            return float(0)

    ##
    # @brief Safely converts text to an integer value.
    #
    # Returns zero when the provided value cannot be
    # converted to a valid integer.
    #
    # @param input_value
    # Text representation of a numeric value.
    #
    # @return int
    # Parsed integer value or zero.
    #
    @staticmethod
    def _safe_int(input_value: str) -> int:

        try:
            return int(float(input_value))

        except ValueError:
            return 0

    ##
    # @brief Safely normalizes text input.
    #
    # Removes surrounding whitespace and returns a
    # fallback value when the resulting text is empty.
    #
    # @param input_text
    # Text value to normalize.
    #
    # @param default
    # Value returned when the input is empty.
    #
    # @return str
    # Normalized text value.
    #
    @staticmethod
    def _safe_str(input_text: str, default: str = "") -> str:

        return (
            input_text.strip()
            if input_text and input_text.strip()
            else default
        )


    ##
    # @brief Retrieves text from a table cell.
    #
    # Returns an empty string when the specified cell
    # does not contain a table item.
    #
    # @param table_widget
    # Source table widget.
    #
    # @param row_index
    # Index of the target row.
    #
    # @param column_index
    # Index of the target column.
    #
    # @return str
    # Cell text or an empty string.
    #
    @staticmethod
    def _get_cell_text(table_widget: QTableWidget, row_index: int, column_index: int,) -> str:

        table_item: QTableWidgetItem | None = (
            table_widget.item(
                row_index,
                column_index,
            )
        )

        return (
            table_item.text()
            if table_item
            else ""
        )

    ##
    # @brief Regenerates entity identifiers.
    #
    # Updates miner, mine, and warden identifiers
    # to ensure sequential numbering after rows
    # have been added, removed, or reordered.
    #
    def _refresh_identifiers(self) -> None:

        # ===== MINER IDENTIFIERS =====
        for row_index in range(self.miners_table.rowCount()):
            self.miners_table.setItem(
                row_index,
                0,
                self._build_identifier_item(
                    f"{row_index + 1}M"
                ),
            )

        # ===== MINE IDENTIFIERS =====
        for row_index in range(self.mines_table.rowCount()):
            mine_identifier: str = (
                f"{row_index + 1}N"
            )

            self.mines_table.setItem(
                row_index,
                0,
                self._build_identifier_item(
                    mine_identifier
                ),
            )

            self.wardens_table.setItem(
                row_index,
                0,
                self._build_identifier_item(
                    mine_identifier
                ),
            )

    ##
    # @brief Validates all world data entered by the user.
    #
    # Performs structural, numerical, and geometric
    # validation of miners, mines, and wardens.
    #
    # The validation process verifies:
    # - minimum entity count requirements,
    # - mine geometry constraints,
    # - coordinate completeness,
    # - mine capacity values,
    # - warden alert volume values.
    #
    # Invalid cells are highlighted and validation
    # states are propagated to the corresponding
    # user interface widgets.
    #
    # @return list[str]
    # Collection of validation error messages.
    #
    def _validate(self) -> list[str]:
        validation_errors: list[str] = []

        # ===== TABLE VALIDATION =====
        self.mines_table.setProperty(
            "invalid",
            False,
        )

        self.miners_table.setProperty(
            "invalid",
            False,
        )

        # ===== MINE TABLE VALIDATION =====
        if self.mines_table.rowCount() < 3:
            validation_errors.append(
                "Please add at least THREE mines before continuing."
            )

            self.mines_table.setProperty(
                "invalid",
                True,
            )

        # ===== MINE GEOMETRY VALIDATION =====
        mine_positions: list[tuple[float | int, float | int]] = []

        for row_index in range(
            self.mines_table.rowCount()
        ):
            position_x = self._safe_float(
                self._get_cell_text(
                    self.mines_table,
                    row_index,
                    3,
                )
            )

            position_y = self._safe_float(
                self._get_cell_text(
                    self.mines_table,
                    row_index,
                    4,
                )
            )

            if (
                position_x is not None
                and position_y is not None
            ):
                mine_positions.append(
                    (position_x, position_y)
                )

        # ===== COLLINEAR VALIDATION =====
        if len(mine_positions) >= 3:

            base_x1, base_y1 = mine_positions[0]
            base_x2, base_y2 = mine_positions[1]

            all_collinear: bool = True

            for position_x, position_y in mine_positions[2:]:

                determinant: float | int = (
                    (base_x2 - base_x1)
                    * (position_y - base_y1)
                    - (base_y2 - base_y1)
                    * (position_x - base_x1)
                )

                if abs(determinant) > 1e-12:
                    all_collinear = False
                    break

            if all_collinear:
                validation_errors.append(
                    "Mine positions cannot all lie on the same line."
                )

                self.mines_table.setProperty(
                    "invalid",
                    True,
                )

        # ===== MINER TABLE VALIDATION =====
        if self.miners_table.rowCount() < 1:
            validation_errors.append(
                "Please add at least ONE miner before continuing."
            )

            self.miners_table.setProperty(
                "invalid",
                True,
            )

        # ===== STYLE REFRESH =====
        self.mines_table.style().polish(
            self.mines_table
        )

        self.miners_table.style().polish(
            self.miners_table
        )

        # ===== MINER VALIDATION =====
        for row_index in range(
            self.miners_table.rowCount()
        ):
            # ===== POSITION VALUES =====
            position_x: float = (
                self._safe_float(
                    self._get_cell_text(
                        self.miners_table,
                        row_index,
                        3,
                    )
                )
            )

            position_y: float = (
                self._safe_float(
                    self._get_cell_text(
                        self.miners_table,
                        row_index,
                        4,
                    )
                )
            )

            # ===== POSITION VALIDATION =====
            if position_x is None and position_y is None:
                validation_errors.append(
                    f"Miner {row_index + 1}: "
                    f"please provide both position coordinates."
                )

                self._mark_cell(
                    self.miners_table,
                    row_index,
                    3,
                )

                self._mark_cell(
                    self.miners_table,
                    row_index,
                    4,
                )

            elif position_x is None:
                validation_errors.append(
                    f"Miner {row_index + 1}: "
                    f"please provide the X position coordinate."
                )

                self._mark_cell(
                    self.miners_table,
                    row_index,
                    3,
                )

                self._clear_mark(
                    self.miners_table,
                    row_index,
                    4,
                )

            elif position_y is None:
                validation_errors.append(
                    f"Miner {row_index + 1}: "
                    f"please provide the Y position coordinate."
                )

                self._mark_cell(
                    self.miners_table,
                    row_index,
                    4,
                )

                self._clear_mark(
                    self.miners_table,
                    row_index,
                    3,
                )

            # ===== VALID POSITION =====
            else:
                self._clear_mark(
                    self.miners_table,
                    row_index,
                    3,
                )

                self._clear_mark(
                    self.miners_table,
                    row_index,
                    4,
                )


        # ===== MINE VALIDATION =====
        for row_index in range(
            self.mines_table.rowCount()
        ):
            # ===== CAPACITY VALUE =====
            capacity: int = (
                self._safe_int(
                    self._get_cell_text(
                        self.mines_table,
                        row_index,
                        2,
                    )
                )
            )

            # ===== CAPACITY VALIDATION =====
            if capacity is None:
                validation_errors.append(
                    f"Mine {row_index + 1}: "
                    f"the maximum capacity value is required."
                )

                self._mark_cell(
                    self.mines_table,
                    row_index,
                    2,
                )

            elif capacity < 0:
                validation_errors.append(
                    f"Mine {row_index + 1}: "
                    f"the maximum capacity cannot be negative."
                )

                self._mark_cell(
                    self.mines_table,
                    row_index,
                    2,
                )

            else:
                self._clear_mark(
                    self.mines_table,
                    row_index,
                    2,
                )

            # ===== POSITION VALUES =====
            position_x: float = (
                self._safe_float(
                    self._get_cell_text(
                        self.mines_table,
                        row_index,
                        3,
                    )
                )
            )

            position_y: float = (
                self._safe_float(
                    self._get_cell_text(
                        self.mines_table,
                        row_index,
                        4,
                    )
                )
            )

            # ===== POSITION VALIDATION =====
            if position_x is None and position_y is None:
                validation_errors.append(
                    f"Mine {row_index + 1}: "
                    f"please provide the X position coordinate."
                )

                self._mark_cell(
                    self.mines_table,
                    row_index,
                    3,
                )

                self._mark_cell(
                    self.mines_table,
                    row_index,
                    4,
                )

            elif position_x is None:
                validation_errors.append(
                    f"Mine {row_index + 1}: "
                    f"please provide the X position coordinate."
                )

                self._mark_cell(
                    self.mines_table,
                    row_index,
                    3,
                )

                self._clear_mark(
                    self.mines_table,
                    row_index,
                    4,
                )

            elif position_y is None:
                validation_errors.append(
                    f"Mine {row_index + 1}: "
                    f"please provide the Y position coordinate."
                )

                self._mark_cell(
                    self.mines_table,
                    row_index,
                    4,
                )

                self._clear_mark(
                    self.mines_table,
                    row_index,
                    3,
                )

            # ===== VALID POSITION =====
            else:
                self._clear_mark(
                    self.mines_table,
                    row_index,
                    3,
                )

                self._clear_mark(
                    self.mines_table,
                    row_index,
                    4,
                )

        # ===== WARDEN VALIDATION =====
        for row_index in range(
            self.wardens_table.rowCount()
        ):
            # ===== ALERT VOLUME =====
            alert_volume: int = (
                self._safe_int(
                    self._get_cell_text(
                        self.wardens_table,
                        row_index,
                        1,
                    )
                )
            )

            # ===== ALERT VALIDATION =====
            if alert_volume is None:
                validation_errors.append(
                    f"Warden {row_index + 1}: "
                    f"the alert volume value is required."
                )

                self._mark_cell(
                    self.wardens_table,
                    row_index,
                    1,
                )

            elif alert_volume < 0:
                validation_errors.append(
                    f"Warden {row_index + 1}: "
                    f"the alert volume cannot be negative."
                )

                self._mark_cell(
                    self.wardens_table,
                    row_index,
                    1,
                )

            else:
                self._clear_mark(
                    self.wardens_table,
                    row_index,
                    1,
                )

        # ===== TABLE REFRESH =====
        self.mines_table.viewport().update()
        self.wardens_table.viewport().update()
        self.miners_table.viewport().update()

        return validation_errors

    ##
    # @brief Marks a table cell as invalid.
    #
    # Applies visual validation feedback to the specified
    # cell by changing its background colour and displaying
    # an explanatory tooltip message.
    #
    # @param table_widget
    # Target table widget.
    #
    # @param row_index
    # Index of the target row.
    #
    # @param column_index
    # Index of the target column.
    #
    @staticmethod
    def _mark_cell(table_widget: QTableWidget, row_index: int, column_index: int) -> None:

        table_item: QTableWidgetItem | None = (
            table_widget.item(
                row_index,
                column_index,
            )
        )

        if table_item:
            # ===== INVALID BACKGROUND =====
            table_item.setData(
                Qt.ItemDataRole.BackgroundRole,
                QColor(255, 220, 220),
            )

            # ===== TOOLTIP =====
            table_item.setToolTip(
                "This field contains an invalid or missing value."
            )

    ##
    # @brief Removes validation feedback from a table cell.
    #
    # Restores the default appearance of the specified cell
    # and removes any validation tooltip previously applied.
    #
    # @param table_widget
    # Target table widget.
    #
    # @param row_index
    # Index of the target row.
    #
    # @param column_index
    # Index of the target column.
    #
    @staticmethod
    def _clear_mark(table_widget: QTableWidget, row_index: int, column_index: int) -> None:

        table_item: QTableWidgetItem | None = (
            table_widget.item(
                row_index,
                column_index,
            )
        )

        if table_item:
            # ===== RESET BACKGROUND =====
            table_item.setData(
                Qt.ItemDataRole.BackgroundRole,
                None,
            )

            # ===== RESET TOOLTIP =====
            table_item.setToolTip("")

    ##
    # @brief Adds a new miner entry to the table.
    #
    # Creates a new miner row, assigns a unique identifier,
    # initializes default values, and configures the
    # resource selection widget.
    #
    def _add_miner(self) -> None:

        # ===== ROW =====
        row_index: int = (
            self.miners_table.rowCount()
        )

        self.miners_table.insertRow(
            row_index
        )

        # ===== IDENTIFIER =====
        self.miners_table.setItem(
            row_index,
            0,
            self._build_identifier_item(
                f"{row_index + 1}M"
            ),
        )

        # ===== DEFAULT NAME =====
        self.miners_table.setItem(
            row_index,
            1,
            QTableWidgetItem("Dwarf"),
        )

        # ===== RESOURCE SELECTION =====
        resource_selector: QComboBox = (
            QComboBox()
        )

        resource_selector.addItems(
            RESOURCES
        )

        self.miners_table.setCellWidget(
            row_index,
            2,
            resource_selector,
        )

        # ===== POSITION CELLS =====
        for column_index in (3, 4):
            self.miners_table.setItem(
                row_index,
                column_index,
                QTableWidgetItem(""),
            )

    ##
    # @brief Adds a new mine entry to the table.
    #
    # Creates a new mine row, assigns a unique identifier,
    # initializes resource selection controls, and creates
    # the corresponding warden entry associated with the mine.
    #
    def _add_mine(self) -> None:

        # ===== ROW =====
        row_index: int = (
            self.mines_table.rowCount()
        )

        self.mines_table.insertRow(
            row_index
        )

        # ===== IDENTIFIER =====
        mine_identifier: str = (
            f"{row_index + 1}N"
        )

        self.mines_table.setItem(
            row_index,
            0,
            self._build_identifier_item(
                mine_identifier
            ),
        )

        # ===== RESOURCE SELECTION =====
        resource_selector: QComboBox = (
            QComboBox()
        )

        resource_selector.addItems(
            RESOURCES
        )

        self.mines_table.setCellWidget(
            row_index,
            1,
            resource_selector,
        )

        # ===== MINE VALUES =====
        for column_index in (2, 3, 4):
            self.mines_table.setItem(
                row_index,
                column_index,
                QTableWidgetItem(""),
            )

        # ===== WARDEN TABLE =====
        self.wardens_table.insertRow(
            row_index
        )

        self.wardens_table.setItem(
            row_index,
            0,
            self._build_identifier_item(
                mine_identifier
            ),
        )

        # ===== ALERT VOLUME =====
        self.wardens_table.setItem(
            row_index,
            1,
            QTableWidgetItem(""),
        )

    ##
    # @brief Removes selected rows from a table.
    #
    # Deletes all currently selected rows from the specified
    # table, refreshes entity identifiers, and updates the
    # state of deletion controls.
    #
    # @param table_widget
    # Table containing rows selected for removal.
    #
    def _remove_selected_rows(self, table_widget: QTableWidget) -> None:

        # ===== SELECTED ROWS =====
        selected_rows: list[int] = sorted(
            {
                table_index.row()
                for table_index
                in table_widget.selectedIndexes()
            },
            reverse=True,
        )

        # ===== REMOVE ROWS =====
        for row_index in selected_rows:
            table_widget.removeRow(
                row_index
            )

        # ===== IDENTIFIER REFRESH =====
        self._refresh_identifiers()

        # ===== BUTTON UPDATE =====
        self._update_delete_buttons()

    ##
    # @brief Removes selected mines and their wardens.
    #
    # Deletes selected mine entries together with their
    # corresponding warden records to preserve data
    # consistency across related tables.
    #
    def _delete_selected_mines(self) -> None:

        # ===== SELECTED ROWS =====
        selected_rows: list[int] = sorted(
            {
                table_index.row()
                for table_index
                in self.mines_table.selectedIndexes()
            },
            reverse=True,
        )

        # ===== REMOVE ROWS =====
        for row_index in selected_rows:
            self.mines_table.removeRow(
                row_index
            )

            self.wardens_table.removeRow(
                row_index
            )

        # ===== IDENTIFIER REFRESH =====
        self._refresh_identifiers()

        # ===== BUTTON UPDATE =====
        self._update_delete_buttons()

    ##
    # @brief Updates deletion button availability.
    #
    # Enables or disables deletion controls according
    # to the current selection state of miner and mine
    # tables.
    #
    def _update_delete_buttons(self) -> None:

        # ===== MINER BUTTON =====
        self.delete_miner_button.setEnabled(
            self.miners_table.selectionModel().hasSelection()
        )

        # ===== MINE BUTTON =====
        self.delete_mine_button.setEnabled(
            self.mines_table.selectionModel().hasSelection()
        )

    ##
    # @brief Loads world data into the user interface.
    #
    # Populates miner, mine, and warden tables using
    # data obtained from the specified world model.
    # Existing entities are reconstructed together with
    # their resources, capacities, positions, and
    # associated warden information.
    #
    # @param world_data
    # World data model used to populate the dialogue.
    #
    def _load_to_tables(self, world_data: WorldData) -> None:

        # ===== MINERS =====
        for miner in world_data.miners:
            self._add_miner()

            row_index: int = (
                self.miners_table.rowCount() - 1
            )

            # ===== MINER NAME =====
            self.miners_table.setItem(
                row_index,
                1,
                QTableWidgetItem(
                    miner.name
                ),
            )

            # ===== RESOURCE TYPE =====
            resource_selector: QWidget = (
                self.miners_table.cellWidget(
                    row_index,
                    2,
                )
            )

            if isinstance(resource_selector, QComboBox):
                resource_selector.setCurrentText(
                    miner.resource
                )

            # ===== POSITION =====
            self.miners_table.setItem(
                row_index,
                3,
                QTableWidgetItem(
                    str(miner.position.x)
                ),
            )

            self.miners_table.setItem(
                row_index,
                4,
                QTableWidgetItem(
                    str(miner.position.y)
                ),
            )

        # ===== MINES =====
        for mine in world_data.mines:
            self._add_mine()

            row_index: int = (
                self.mines_table.rowCount() - 1
            )

            # ===== CAPACITY =====
            self.mines_table.setItem(
                row_index,
                2,
                QTableWidgetItem(
                    str(mine.capacity)
                ),
            )

            # ===== POSITION =====
            self.mines_table.setItem(
                row_index,
                3,
                QTableWidgetItem(
                    str(mine.location.x)
                ),
            )

            self.mines_table.setItem(
                row_index,
                4,
                QTableWidgetItem(
                    str(mine.location.y)
                ),
            )

            # ===== RESOURCE TYPE =====
            resource_selector: QWidget | None = (
                self.mines_table.cellWidget(
                    row_index,
                    1,
                )
            )

            if isinstance(resource_selector, QComboBox):
                resource_selector.setCurrentText(
                    mine.resource_type
                )

            # ===== WARDEN DATA =====
            self.wardens_table.setItem(
                row_index,
                1,
                QTableWidgetItem(
                    str(mine.assigned_warden.loudness)
                ),
            )

    ##
    # @brief Validates and persists world data.
    #
    # Executes data validation, displays validation
    # feedback when errors are detected, persists
    # the current world state, emits the data change
    # notification signal, and closes the dialogue.
    #
    def _save(self) -> None:

        # ===== VALIDATION =====
        validation_errors: list[str] = (
            self._validate()
        )

        # ===== CLEAR SELECTION =====
        self.miners_table.clearSelection()
        self.mines_table.clearSelection()
        self.wardens_table.clearSelection()

        # ===== BUTTON UPDATE =====
        self._update_delete_buttons()

        # ===== VALIDATION FAILED =====
        if validation_errors:
            QMessageBox.warning(
                self,
                "Validation Errors:",
                "• " + "\n• ".join(
                    validation_errors
                ),
            )

            return

        # ===== SAVE DATA =====
        save_default_data(
            self.get_data()
        )

        # ===== SIGNAL =====
        self.data_changed.emit()

        # ===== CLOSE DIALOG =====
        self.accept()

    ##
    # @brief Constructs a world model from dialogue data.
    #
    # Extracts miners, mines, and wardens from the
    # user interface tables and converts them into
    # domain objects used by the optimization engine.
    #
    # Resource selections, coordinates, capacities,
    # and warden assignments are transformed into
    # a complete WorldData instance.
    #
    # @return WorldData
    # World model reconstructed from the current
    # dialogue state.
    #
    def get_data(self) -> WorldData:

        # ===== DATA CONTAINERS =====
        miners: list[Miner] = []
        mines: list[Mine] = []

        # ===== MINERS =====
        for row_index in range(
            self.miners_table.rowCount()
        ):
            # ===== RESOURCE SELECTOR =====
            resource_selector: QComboBox = cast(
                QComboBox,
                self.miners_table.cellWidget(
                    row_index,
                    2,
                ),
            )

            # ===== POSITION =====
            miner_position: Point = Point(
                x=self._safe_float(
                    self._get_cell_text(
                        self.miners_table,
                        row_index,
                        3,
                    )
                ),
                y=self._safe_float(
                    self._get_cell_text(
                        self.miners_table,
                        row_index,
                        4,
                    )
                ),
            )

            # ===== MINER =====
            miners.append(
                Miner(
                    identifier=self._get_cell_text(
                        self.miners_table,
                        row_index,
                        0,
                    ),

                    name=self._safe_str(
                        self._get_cell_text(
                            self.miners_table,
                            row_index,
                            1,
                        ),
                        "Dwarf",
                    ),

                    resource=resource_selector.currentText(),

                    position=miner_position,
                )
            )

        # ===== MINES =====
        for row_index in range(
            self.mines_table.rowCount()
        ):
            # ===== RESOURCE SELECTOR =====
            resource_selector: QComboBox = cast(
                QComboBox,
                self.mines_table.cellWidget(
                    row_index,
                    1,
                ),
            )

            # ===== POSITION VALUES =====
            position_x: float = (
                self._safe_float(
                    self._get_cell_text(
                        self.mines_table,
                        row_index,
                        3,
                    )
                )
            )

            position_y: float = (
                self._safe_float(
                    self._get_cell_text(
                        self.mines_table,
                        row_index,
                        4,
                    )
                )
            )

            # ===== LOCATION =====
            mine_location: Point = Point(
                position_x,
                position_y,
            )

            # ===== WARDEN =====
            assigned_warden: Warden = (
                Warden(
                    identifier=(
                        self._get_cell_text(
                            self.mines_table,
                            row_index,
                            0,
                        ) + "W"
                    ),

                    name="Warden",

                    position=mine_location,

                    loudness=self._safe_int(
                        self._get_cell_text(
                            self.wardens_table,
                            row_index,
                            1,
                        )
                    ),

                    boundary_radius=row_index,
                )
            )

            # ===== MINE =====
            mines.append(
                Mine(
                    identifier=self._get_cell_text(
                        self.mines_table,
                        row_index,
                        0,
                    ),

                    resource_type=(
                        resource_selector.currentText()
                    ),

                    capacity=self._safe_int(
                        self._get_cell_text(
                            self.mines_table,
                            row_index,
                            2,
                        )
                    ),

                    location=mine_location,

                    assigned_warden=assigned_warden,
                )
            )

        return WorldData(miners, mines)