from __future__ import annotations

"""Sprint 28 managed contract viewer MVP.

This module keeps the existing PyQt viewer entrypoint and makes its Sprint 28
scope explicit: DB-backed contract browsing, owner/folder filtering, source
snippet display, and file-level git status.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CONTROL_PLANE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CONTROL_PLANE_DIR.parent
if str(CONTROL_PLANE_DIR) not in sys.path:
    sys.path.insert(0, str(CONTROL_PLANE_DIR))

from shared.managed_contract_repository import (  # noqa: E402
    ContractQuery,
    git_file_statuses,
    import_managed_contracts_csv,
    list_managed_contracts,
    list_owner_modules,
)


FOLDER_ORDER = [
    "chart_builder",
    "chart_runtime",
    "drift 보고서",
    "drift_algorithm_impl",
    "drift_control_plane",
    "drift_metric_timeseries",
    "root",
]


@dataclass(frozen=True)
class ManagedContract:
    contract_id: str
    contract_level: str
    contract_type: str
    owner_module: str
    file_path: str
    qualified_name: str
    source_of_truth_doc: str
    input_contract: str
    output_contract: str
    dependent_tests: str
    status: str
    description: str
    git_status: str = ""

    @property
    def display_name(self) -> str:
        return self.qualified_name or self.contract_id


def load_contracts() -> list[ManagedContract]:
    rows = list_managed_contracts(ContractQuery(status="active"))
    statuses = git_file_statuses(REPO_ROOT)
    contracts: list[ManagedContract] = []
    for row in rows:
        contract = ManagedContract(**row)
        repo_path = repo_relative_path(contract)
        contracts.append(
            ManagedContract(
                **row,
                git_status=statuses.get(repo_path, "clean"),
            )
        )
    return contracts


def resolve_contract_path(contract: ManagedContract) -> Path:
    raw_path = Path(contract.file_path)
    if raw_path.is_absolute():
        return raw_path
    if contract.file_path.startswith("../"):
        return (CONTROL_PLANE_DIR / raw_path).resolve()
    return (CONTROL_PLANE_DIR / raw_path).resolve()


def folder_for_contract(contract: ManagedContract) -> str:
    path = resolve_contract_path(contract)
    try:
        relative = path.relative_to(REPO_ROOT)
    except ValueError:
        return contract.owner_module
    if not relative.parts:
        return "root"
    top = relative.parts[0]
    return top if top in FOLDER_ORDER else contract.owner_module


def repo_relative_path(contract: ManagedContract) -> str:
    path = resolve_contract_path(contract)
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return contract.file_path.replace("\\", "/")


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def marker_pattern(contract_id: str) -> re.Pattern[str]:
    return re.compile(rf"@managed-contract\s+contract_id={re.escape(contract_id)}(\s|$)")


def definition_pattern(qualified_name: str, contract_type: str) -> re.Pattern[str] | None:
    if not qualified_name:
        return None
    name = qualified_name.split(".")[-1]
    if not name or name.startswith("window"):
        return None

    escaped = re.escape(name)
    if contract_type.startswith("python"):
        return re.compile(rf"^\s*(def|class)\s+{escaped}\b")
    if contract_type.startswith("javascript"):
        return re.compile(
            rf"^\s*(function\s+{escaped}\b|const\s+{escaped}\b|let\s+{escaped}\b|var\s+{escaped}\b|{escaped}\s*[:=])"
        )
    return re.compile(rf"\b{escaped}\b")


def locate_line(lines: list[str], contract: ManagedContract) -> int | None:
    marker = marker_pattern(contract.contract_id)
    for index, line in enumerate(lines):
        if marker.search(line):
            return index

    pattern = definition_pattern(contract.qualified_name, contract.contract_type)
    if pattern:
        for index, line in enumerate(lines):
            if pattern.search(line):
                return index

    if contract.qualified_name:
        token = contract.qualified_name.split(".")[-1]
        for index, line in enumerate(lines):
            if token and token in line:
                return index
    return None


def extract_code(contract: ManagedContract) -> tuple[str, int | None, Path]:
    path = resolve_contract_path(contract)
    if not path.exists():
        return f"파일을 찾을 수 없습니다: {path}", None, path

    text = read_text(path)
    lines = text.splitlines()
    if contract.contract_type == "document" or contract.qualified_name == "":
        return with_line_numbers(lines), 1, path

    line_index = locate_line(lines, contract)
    if line_index is None:
        return with_line_numbers(lines), None, path

    start = max(0, line_index - 8)
    end = min(len(lines), line_index + 80)
    return with_line_numbers(lines[start:end], start + 1), line_index + 1, path


def with_line_numbers(lines: Iterable[str], start_line: int = 1) -> str:
    return "\n".join(f"{line_no:>5}  {line}" for line_no, line in enumerate(lines, start_line))


class ManagedContractViewer:
    def __init__(self) -> None:
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        from PyQt6.QtWidgets import (
            QAbstractItemView,
            QApplication,
            QHBoxLayout,
            QLabel,
            QComboBox,
            QLineEdit,
            QListWidget,
            QMainWindow,
            QPlainTextEdit,
            QSplitter,
            QTableWidget,
            QTableWidgetItem,
            QVBoxLayout,
            QWidget,
        )

        self.Qt = Qt
        self.QApplication = QApplication
        self.QMainWindow = QMainWindow
        self.QWidget = QWidget
        self.QVBoxLayout = QVBoxLayout
        self.QHBoxLayout = QHBoxLayout
        self.QLabel = QLabel
        self.QComboBox = QComboBox
        self.QLineEdit = QLineEdit
        self.QListWidget = QListWidget
        self.QPlainTextEdit = QPlainTextEdit
        self.QSplitter = QSplitter
        self.QTableWidget = QTableWidget
        self.QTableWidgetItem = QTableWidgetItem
        self.QAbstractItemView = QAbstractItemView
        self.QFont = QFont

        self.contracts = load_contracts()
        self.current_folder = FOLDER_ORDER[0]
        self.current_owner = "전체"
        self.search_text = ""
        self.filtered_contracts: list[ManagedContract] = []
        self.window = None

    def run(self) -> int:
        app = self.QApplication.instance() or self.QApplication(sys.argv)
        window = self.build_window()
        window.show()
        return app.exec()

    def build_window(self):
        window = self.QMainWindow()
        window.setWindowTitle("Managed Contract Viewer - Sprint 28 MVP")
        window.resize(1440, 900)

        splitter = self.QSplitter(self.Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_folder_panel())
        splitter.addWidget(self._build_contract_panel())
        splitter.addWidget(self._build_code_panel())
        splitter.setSizes([220, 480, 740])

        window.setCentralWidget(splitter)
        self._populate_folders()
        self._populate_owner_filter()
        self._refresh_contract_table()
        self.window = window
        return window

    def row_count(self) -> int:
        return len(self.contracts)

    def _build_folder_panel(self):
        panel = self.QWidget()
        layout = self.QVBoxLayout(panel)
        layout.addWidget(self.QLabel("폴더"))
        self.folder_list = self.QListWidget()
        self.folder_list.currentTextChanged.connect(self._on_folder_changed)
        layout.addWidget(self.folder_list)
        return panel

    def _build_contract_panel(self):
        panel = self.QWidget()
        layout = self.QVBoxLayout(panel)

        header = self.QHBoxLayout()
        header.addWidget(self.QLabel("함수 / 자료구조 / 계약"))
        self.owner_combo = self.QComboBox()
        self.owner_combo.currentTextChanged.connect(self._on_owner_changed)
        header.addWidget(self.owner_combo)
        self.search = self.QLineEdit()
        self.search.setPlaceholderText("검색")
        self.search.textChanged.connect(self._on_search_changed)
        header.addWidget(self.search)
        layout.addLayout(header)

        self.contract_table = self.QTableWidget(0, 5)
        self.contract_table.setHorizontalHeaderLabels(["Level", "Git", "Type", "Name", "Description"])
        self.contract_table.setSelectionBehavior(self.QAbstractItemView.SelectionBehavior.SelectRows)
        self.contract_table.setEditTriggers(self.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.contract_table.verticalHeader().setVisible(False)
        self.contract_table.itemSelectionChanged.connect(self._on_contract_selected)
        self.contract_table.setColumnWidth(0, 58)
        self.contract_table.setColumnWidth(1, 58)
        self.contract_table.setColumnWidth(2, 130)
        self.contract_table.setColumnWidth(3, 210)
        layout.addWidget(self.contract_table)
        return panel

    def _build_code_panel(self):
        panel = self.QWidget()
        layout = self.QVBoxLayout(panel)
        self.meta = self.QLabel("항목을 선택하세요.")
        self.meta.setTextInteractionFlags(self.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.meta.setWordWrap(True)
        layout.addWidget(self.meta)

        vertical_splitter = self.QSplitter(self.Qt.Orientation.Vertical)

        self.code_view = self.QPlainTextEdit()
        self.code_view.setReadOnly(True)
        font = self.QFont("Consolas")
        font.setStyleHint(self.QFont.StyleHint.Monospace)
        font.setPointSize(10)
        self.code_view.setFont(font)
        vertical_splitter.addWidget(self.code_view)

        self.description_view = self.QPlainTextEdit()
        self.description_view.setReadOnly(True)
        self.description_view.setMinimumHeight(180)
        vertical_splitter.addWidget(self.description_view)
        vertical_splitter.setSizes([620, 240])

        layout.addWidget(vertical_splitter)
        return panel

    def _populate_folders(self) -> None:
        counts = {folder: 0 for folder in FOLDER_ORDER}
        for contract in self.contracts:
            folder = folder_for_contract(contract)
            if folder in counts:
                counts[folder] += 1

        for folder in FOLDER_ORDER:
            self.folder_list.addItem(f"{folder} ({counts[folder]})")
        self.folder_list.setCurrentRow(0)

    def _populate_owner_filter(self) -> None:
        self.owner_combo.addItem("전체")
        for owner_module in list_owner_modules():
            self.owner_combo.addItem(owner_module)

    def _on_folder_changed(self, text: str) -> None:
        self.current_folder = text.split(" (", 1)[0]
        self._refresh_contract_table()

    def _on_search_changed(self, text: str) -> None:
        self.search_text = text.strip().lower()
        self._refresh_contract_table()

    def _on_owner_changed(self, text: str) -> None:
        self.current_owner = text or "전체"
        self._refresh_contract_table()

    def _refresh_contract_table(self) -> None:
        selected = [
            contract
            for contract in self.contracts
            if folder_for_contract(contract) == self.current_folder
            and self._matches_owner(contract)
            and self._matches_search(contract)
        ]
        self.filtered_contracts = selected
        self.contract_table.setRowCount(len(selected))

        for row_index, contract in enumerate(selected):
            values = [
                contract.contract_level,
                contract.git_status,
                contract.contract_type,
                contract.display_name,
                contract.description,
            ]
            for col_index, value in enumerate(values):
                item = self.QTableWidgetItem(value)
                item.setToolTip(value)
                self.contract_table.setItem(row_index, col_index, item)

        if selected:
            self.contract_table.selectRow(0)
        else:
            self.meta.setText("표시할 항목이 없습니다.")
            self.code_view.clear()
            self.description_view.clear()

    def _matches_search(self, contract: ManagedContract) -> bool:
        if not self.search_text:
            return True
        haystack = " ".join(
            [
                contract.contract_id,
                contract.contract_level,
                contract.contract_type,
                contract.owner_module,
                contract.file_path,
                contract.qualified_name,
                contract.description,
                contract.input_contract,
                contract.output_contract,
            ]
        ).lower()
        return self.search_text in haystack

    def _matches_owner(self, contract: ManagedContract) -> bool:
        return self.current_owner == "전체" or contract.owner_module == self.current_owner

    def _on_contract_selected(self) -> None:
        rows = self.contract_table.selectionModel().selectedRows()
        if not rows:
            return
        contract = self.filtered_contracts[rows[0].row()]
        code, line_no, path = extract_code(contract)
        line_text = f":{line_no}" if line_no else ""
        self.meta.setText(
            "\n".join(
                [
                    f"{contract.contract_id} [{contract.contract_level}]",
                    f"Git: {contract.git_status}",
                    f"{path}{line_text}",
                    f"문서: {contract.source_of_truth_doc or '-'}",
                    f"테스트: {contract.dependent_tests or '-'}",
                ]
            )
        )
        self.code_view.setPlainText(code)
        self.description_view.setPlainText(format_contract_description(contract))


def format_contract_description(contract: ManagedContract) -> str:
    return "\n\n".join(
        [
            "설명\n" + (contract.description or "-"),
            "입력/관리 대상\n" + (contract.input_contract or "-"),
            "출력/영향 범위\n" + (contract.output_contract or "-"),
        ]
    )


def check_database() -> int:
    contracts = load_contracts()
    counts = {folder: 0 for folder in FOLDER_ORDER}
    for contract in contracts:
        folder = folder_for_contract(contract)
        if folder in counts:
            counts[folder] += 1
    print(f"managed_contract rows: {len(contracts)}")
    for folder in FOLDER_ORDER:
        print(f"{folder}: {counts[folder]}")
    return 0


def smoke_check() -> int:
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    viewer = ManagedContractViewer()
    viewer.build_window()
    if viewer.row_count() <= 0:
        print("managed_contract viewer smoke failed: no rows")
        return 1
    print(f"managed_contract viewer smoke passed: {viewer.row_count()} rows")
    app.quit()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="DB에서 계약 목록을 읽을 수 있는지만 확인한다.")
    parser.add_argument("--import-csv", action="store_true", help="managed_contracts.csv를 DB에 적재한다.")
    parser.add_argument("--smoke", action="store_true", help="PyQt UI를 offscreen smoke 용도로 생성한다.")
    args = parser.parse_args()

    if args.import_csv:
        imported = import_managed_contracts_csv()
        print(f"managed_contract imported rows: {imported}")
        return 0
    if args.smoke:
        return smoke_check()
    if args.check:
        return check_database()
    return ManagedContractViewer().run()


if __name__ == "__main__":
    raise SystemExit(main())
