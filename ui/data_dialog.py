from typing import cast
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
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
)

from models.domain import Guard, Mine, Miner, Point, ProblemData
from models.storage import load_default_data, save_default_data


# ===== CONSTANTS =====
RESOURCES: list[str] = [
    "Gold",
    "Coal",
    "Copper",
    "Iron",
    "Silver",
    "Diamond",
]


# ===== DATA DIALOG =====
class DataDialog(QDialog):
    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Enter Data")
        self.resize(1100, 700)

        self._build_ui()

        data = load_default_data()
        if data:
            self._load_to_tables(data)

    # ===== UI =====
    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(QLabel("Miners"))
        self.miners_table = self._create_table(
            ["ID", "Name", "Resource", "X", "Y"]
        )
        main_layout.addWidget(self.miners_table)

        middle_layout = QHBoxLayout()

        mines_layout = QVBoxLayout()
        mines_layout.addWidget(QLabel("Mines"))
        self.mines_table = self._create_table(
            ["ID", "Resource", "Capacity", "X", "Y"]
        )
        mines_layout.addWidget(self.mines_table)

        guards_layout = QVBoxLayout()
        guards_layout.addWidget(QLabel("Guards"))
        self.guards_table = self._create_table(["ID", "Loudness"])
        guards_layout.addWidget(self.guards_table)

        middle_layout.addLayout(mines_layout, 2)
        middle_layout.addLayout(guards_layout, 1)

        main_layout.addLayout(middle_layout)

        # ===== BUTTONS =====
        button_layout = QHBoxLayout()

        add_miner_button = QPushButton("Add Miner")
        add_mine_button = QPushButton("Add Mine")
        self.delete_miner_button = QPushButton("Delete Miner")
        self.delete_mine_button = QPushButton("Delete Mine")

        for button in (
            add_miner_button,
            add_mine_button,
            self.delete_miner_button,
            self.delete_mine_button,
        ):
            button.setObjectName("ActionButton")
            button.setFixedWidth(120)
            button.setFixedHeight(24)

        self.delete_miner_button.setEnabled(False)
        self.delete_mine_button.setEnabled(False)

        add_miner_button.clicked.connect(self._add_miner)
        add_mine_button.clicked.connect(self._add_mine)

        self.delete_miner_button.clicked.connect(
            lambda: self._remove_selected_rows(self.miners_table)
        )
        self.delete_mine_button.clicked.connect(self._delete_selected_mines)

        self.miners_table.itemSelectionChanged.connect(
            self._update_delete_buttons
        )
        self.mines_table.itemSelectionChanged.connect(
            self._update_delete_buttons
        )

        ok_button = QPushButton("OK")
        ok_button.setObjectName("PrimaryButton")
        ok_button.clicked.connect(self._save)

        button_layout.addWidget(add_miner_button)
        button_layout.addWidget(add_mine_button)
        button_layout.addWidget(self.delete_miner_button)
        button_layout.addWidget(self.delete_mine_button)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)

        main_layout.addLayout(button_layout)

    # noinspection PyMethodMayBeStatic
    def _create_table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        return table

    # noinspection PyMethodMayBeStatic
    def _create_id_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)

        font = QFont()
        font.setBold(True)

        item.setFont(font)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        return item

    # ===== SAFE HELPERS =====
    # noinspection PyMethodMayBeStatic
    def _safe_float(self, value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            return None

    # noinspection PyMethodMayBeStatic
    def _safe_int(self, value: str) -> int | None:
        try:
            return int(float(value))
        except ValueError:
            return None

    # noinspection PyMethodMayBeStatic
    def _safe_str(self, value: str, default: str = "") -> str:
        return value.strip() if value and value.strip() else default

    # noinspection PyMethodMayBeStatic
    def _get_cell_text(
        self,
        table: QTableWidget,
        row: int,
        col: int,
    ) -> str:
        item = table.item(row, col)
        return item.text() if item else ""

    def _reindex_ids(self) -> None:
        for row in range(self.miners_table.rowCount()):
            self.miners_table.setItem(
                row,
                0,
                self._create_id_item(f"{row + 1}M"),
            )

        for row in range(self.mines_table.rowCount()):
            self.mines_table.setItem(
                row,
                0,
                self._create_id_item(f"{row + 1}N"),
            )
            self.guards_table.setItem(
                row,
                0,
                self._create_id_item(f"{row + 1}N"),
            )

    # ===== VALIDATION =====
    def _validate(self) -> list[str]:
        errors: list[str] = []

        if self.mines_table.rowCount() < 3:
            errors.append("You must add at least 3 mines")
            self.mines_table.setStyleSheet(
                "background-color: rgb(255, 220, 220);"
            )
        else:
            self.mines_table.setStyleSheet("")

        # ===== MINERS =====
        for row in range(self.miners_table.rowCount()):
            # ===== X =====
            x = self._safe_float(
                self._get_cell_text(self.miners_table, row, 3)
            )

            if x is None:
                errors.append(f"Miner {row + 1}: fill in X")
                self._mark_cell(self.miners_table, row, 3)
            else:
                self._clear_mark(self.miners_table, row, 3)

            # ===== Y =====
            y = self._safe_float(
                self._get_cell_text(self.miners_table, row, 4)
            )

            if y is None:
                errors.append(f"Miner {row + 1}: fill in Y")
                self._mark_cell(self.miners_table, row, 4)
            else:
                self._clear_mark(self.miners_table, row, 4)

        # ===== MINES =====
        for row in range(self.mines_table.rowCount()):
            # ===== CAPACITY =====
            capacity = self._safe_int(
                self._get_cell_text(self.mines_table, row, 2)
            )

            if capacity is None:
                errors.append(f"Mine {row + 1}: fill in capacity")
                self._mark_cell(self.mines_table, row, 2)
            elif capacity < 0:
                errors.append(f"Mine {row + 1}: negative capacity")
                self._mark_cell(self.mines_table, row, 2)
            else:
                self._clear_mark(self.mines_table, row, 2)

            # ===== X =====
            x = self._safe_float(
                self._get_cell_text(self.mines_table, row, 3)
            )

            if x is None:
                errors.append(f"Mine {row + 1}: fill in X")
                self._mark_cell(self.mines_table, row, 3)
            else:
                self._clear_mark(self.mines_table, row, 3)

            # ===== Y =====
            y = self._safe_float(
                self._get_cell_text(self.mines_table, row, 4)
            )

            if y is None:
                errors.append(f"Mine {row + 1}: fill in Y")
                self._mark_cell(self.mines_table, row, 4)
            else:
                self._clear_mark(self.mines_table, row, 4)

        # ===== GUARDS =====
        for row in range(self.guards_table.rowCount()):
            loudness = self._safe_int(
                self._get_cell_text(self.guards_table, row, 1)
            )

            if loudness is None:
                errors.append(f"Mine {row + 1}: fill in loudness")
                self._mark_cell(self.guards_table, row, 1)
            elif loudness < 0:
                errors.append(f"Guard {row + 1}: negative loudness")
                self._mark_cell(self.guards_table, row, 1)
            else:
                self._clear_mark(self.guards_table, row, 1)

        self.mines_table.viewport().update()
        self.guards_table.viewport().update()
        self.miners_table.viewport().update()

        return errors

    # noinspection PyMethodMayBeStatic
    def _mark_cell(
        self,
        table: QTableWidget,
        row: int,
        col: int,
    ) -> None:
        item = table.item(row, col)
        if item:
            item.setData(
                Qt.ItemDataRole.BackgroundRole,
                QColor(255, 200, 200),
            )

    # noinspection PyMethodMayBeStatic
    def _clear_mark(
        self,
        table: QTableWidget,
        row: int,
        col: int,
    ) -> None:
        item = table.item(row, col)
        if item:
            item.setData(Qt.ItemDataRole.BackgroundRole, None)

    # ===== ADD =====
    def _add_miner(self) -> None:
        row = self.miners_table.rowCount()
        self.miners_table.insertRow(row)

        self.miners_table.setItem(
            row,
            0,
            self._create_id_item(f"{row + 1}M"),
        )
        self.miners_table.setItem(
            row,
            1,
            QTableWidgetItem("Krasnoludek"),
        )

        resource_combo = QComboBox()
        resource_combo.addItems(RESOURCES)

        for col in (3, 4):
            self.miners_table.setItem(row, col, QTableWidgetItem(""))

        self.miners_table.setCellWidget(row, 2, resource_combo)

    def _add_mine(self) -> None:
        row = self.mines_table.rowCount()
        self.mines_table.insertRow(row)

        self.mines_table.setItem(
            row,
            0,
            self._create_id_item(f"{row + 1}N"),
        )

        resource_combo = QComboBox()
        resource_combo.addItems(RESOURCES)

        self.mines_table.setCellWidget(row, 1, resource_combo)

        for col in (2, 3, 4):
            self.mines_table.setItem(row, col, QTableWidgetItem(""))

        self.guards_table.insertRow(row)
        self.guards_table.setItem(
            row,
            0,
            self._create_id_item(f"{row + 1}N"),
        )

        self.guards_table.setItem(row, 1, QTableWidgetItem(""))

    # ===== DELETE =====
    def _remove_selected_rows(self, table: QTableWidget) -> None:
        rows = sorted(
            {index.row() for index in table.selectedIndexes()},
            reverse=True,
        )

        for row in rows:
            table.removeRow(row)

        self._reindex_ids()
        self._update_delete_buttons()

    def _delete_selected_mines(self) -> None:
        rows = sorted(
            {
                index.row()
                for index in self.mines_table.selectedIndexes()
            },
            reverse=True,
        )

        for row in rows:
            self.mines_table.removeRow(row)
            self.guards_table.removeRow(row)

        self._reindex_ids()
        self._update_delete_buttons()

    def _update_delete_buttons(self) -> None:
        self.delete_miner_button.setEnabled(
            self.miners_table.selectionModel().hasSelection()
        )
        self.delete_mine_button.setEnabled(
            self.mines_table.selectionModel().hasSelection()
        )

    # ===== LOAD =====
    def _load_to_tables(self, data: ProblemData) -> None:
        for miner in data.miners:
            self._add_miner()
            row = self.miners_table.rowCount() - 1

            self.miners_table.setItem(
                row,
                1,
                QTableWidgetItem(miner.name),
            )

            combo = self.miners_table.cellWidget(row, 2)
            if isinstance(combo, QComboBox):
                combo.setCurrentText(miner.resource)

            self.miners_table.setItem(
                row,
                3,
                QTableWidgetItem(str(miner.position.x)),
            )
            self.miners_table.setItem(
                row,
                4,
                QTableWidgetItem(str(miner.position.y)),
            )

        for mine in data.mines:
            self._add_mine()
            row = self.mines_table.rowCount() - 1

            self.mines_table.setItem(
                row,
                2,
                QTableWidgetItem(str(mine.capacity)),
            )
            self.mines_table.setItem(
                row,
                3,
                QTableWidgetItem(str(mine.location.x)),
            )
            self.mines_table.setItem(
                row,
                4,
                QTableWidgetItem(str(mine.location.y)),
            )

            combo = self.mines_table.cellWidget(row, 1)
            if isinstance(combo, QComboBox):
                combo.setCurrentText(mine.resource_type)

            self.guards_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(mine.assigned_guard.loudness)
                ),
            )

    # ===== SAVE =====
    def _save(self) -> None:
        errors = self._validate()

        self.miners_table.clearSelection()
        self.mines_table.clearSelection()
        self.guards_table.clearSelection()

        self._update_delete_buttons()

        if errors:
            QMessageBox.warning(
                self,
                "Validation error",
                "\n".join(errors),
            )
            return

        save_default_data(self.get_data())
        self.data_changed.emit()
        self.accept()

    def get_data(self) -> ProblemData:
        miners: list[Miner] = []
        mines: list[Mine] = []

        for row in range(self.miners_table.rowCount()):
            miners.append(
                Miner(
                    identifier=self._get_cell_text(
                        self.miners_table,
                        row,
                        0,
                    ),
                    name=self._safe_str(
                        self._get_cell_text(
                            self.miners_table,
                            row,
                            1,
                        ),
                        "Krasnoludek",
                    ),
                    resource=cast(
                        QComboBox,
                        self.miners_table.cellWidget(row, 2),
                    ).currentText(),
                    position=Point(
                        x=self._safe_float(
                            self._get_cell_text(
                                self.miners_table,
                                row,
                                3,
                            )
                        ),
                        y=self._safe_float(
                            self._get_cell_text(
                                self.miners_table,
                                row,
                                4,
                            )
                        ),
                    ),
                )
            )

        for row in range(self.mines_table.rowCount()):
            x = self._safe_float(
                self._get_cell_text(self.mines_table, row, 3)
            )
            y = self._safe_float(
                self._get_cell_text(self.mines_table, row, 4)
            )

            guard = Guard(
                identifier=(
                    self._get_cell_text(self.mines_table, row, 0) + "_G"
                ),
                name="Guard",
                position=Point(x=x, y=y),
                loudness=self._safe_int(
                    self._get_cell_text(
                        self.guards_table,
                        row,
                        1,
                    )
                ),
                boundary_position=row,
            )

            mines.append(
                Mine(
                    identifier=self._get_cell_text(
                        self.mines_table,
                        row,
                        0,
                    ),
                    resource_type=cast(
                        QComboBox,
                        self.mines_table.cellWidget(row, 1),
                    ).currentText(),
                    capacity=self._safe_int(
                        self._get_cell_text(
                            self.mines_table,
                            row,
                            2,
                        )
                    ),
                    location=Point(x, y),
                    assigned_guard=guard,
                )
            )

        return ProblemData(miners, mines)