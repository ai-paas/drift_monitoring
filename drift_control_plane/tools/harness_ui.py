from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


CONTROL_PLANE_DIR = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = CONTROL_PLANE_DIR / "testing" / "harness" / "scenarios"
RUNS_DIR = CONTROL_PLANE_DIR / "testing" / "runs"


@dataclass(frozen=True)
class RunIndexEntry:
    run_id: str
    scenario_id: str
    mode: str
    status: str
    started_at: str
    finished_at: str
    summary_path: str


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pretty_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def load_run_index() -> list[RunIndexEntry]:
    index_path = RUNS_DIR / "index.jsonl"
    entries: list[RunIndexEntry] = []
    if index_path.exists():
        for line in index_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            entries.append(
                RunIndexEntry(
                    run_id=row.get("runId", ""),
                    scenario_id=row.get("scenarioId", ""),
                    mode=row.get("mode", ""),
                    status=row.get("status", ""),
                    started_at=row.get("startedAt", ""),
                    finished_at=row.get("finishedAt", ""),
                    summary_path=row.get("summaryPath", ""),
                )
            )
    entries.extend(load_matrix_run_index())
    return entries


def load_matrix_run_index() -> list[RunIndexEntry]:
    matrix_root = RUNS_DIR / "matrix"
    if not matrix_root.exists():
        return []
    entries: list[RunIndexEntry] = []
    for run_dir in sorted(path for path in matrix_root.iterdir() if path.is_dir()):
        manifest_path = run_dir / "matrix_manifest.json"
        coverage_path = run_dir / "coverage_summary.json"
        if not manifest_path.exists() or not coverage_path.exists():
            continue
        try:
            manifest = read_json(manifest_path)
            coverage = read_json(coverage_path)
        except (OSError, json.JSONDecodeError):
            continue
        status = "failed" if int(coverage.get("failedResults", 0)) else "passed"
        entries.append(
            RunIndexEntry(
                run_id=f"matrix/{run_dir.name}",
                scenario_id=manifest.get("matrixId", "matrix"),
                mode="matrix",
                status=status,
                started_at=manifest.get("startedAt", ""),
                finished_at=manifest.get("finishedAt", ""),
                summary_path=f"matrix/{run_dir.name}/summary.md",
            )
        )
    return entries


class HarnessUi(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Drift Harness UI")
        self.resize(1320, 860)
        self.process: QProcess | None = None
        self.run_entries: list[RunIndexEntry] = []
        self.selected_run_dir: Path | None = None

        self.scenario_combo = QComboBox()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["scenario", "A", "B"])
        self.run_button = QPushButton("실행")
        self.refresh_button = QPushButton("새로고침")
        self.status_label = QLabel("대기")
        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)

        self.run_list = QListWidget()
        self.summary_text = QPlainTextEdit()
        self.summary_text.setReadOnly(True)
        self.validation_table = QTableWidget(0, 4)
        self.validation_table.setHorizontalHeaderLabels(["status", "name", "message", "details"])
        self.call_list = QListWidget()
        self.json_text = QPlainTextEdit()
        self.json_text.setReadOnly(True)
        self.artifact_list = QListWidget()

        self._build_layout()
        self._connect_signals()
        self.reload_scenarios()
        self.reload_runs()

    def _build_layout(self) -> None:
        root = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(self._build_left_panel())
        root.addWidget(self._build_right_tabs())
        root.setSizes([360, 960])
        self.setCentralWidget(root)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        server_box = QGroupBox("Server / Run Control")
        server_layout = QGridLayout(server_box)
        server_layout.addWidget(QLabel("상태"), 0, 0)
        server_layout.addWidget(self.status_label, 0, 1)
        server_layout.addWidget(QLabel("Scenario"), 1, 0)
        server_layout.addWidget(self.scenario_combo, 1, 1)
        server_layout.addWidget(QLabel("Mode"), 2, 0)
        server_layout.addWidget(self.mode_combo, 2, 1)
        buttons = QHBoxLayout()
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.refresh_button)
        server_layout.addLayout(buttons, 3, 0, 1, 2)
        layout.addWidget(server_box)

        runs_box = QGroupBox("Runs")
        runs_layout = QVBoxLayout(runs_box)
        runs_layout.addWidget(self.run_list)
        layout.addWidget(runs_box, 1)
        return panel

    def _build_right_tabs(self) -> QTabWidget:
        tabs = QTabWidget()

        run_tab = QWidget()
        run_layout = QVBoxLayout(run_tab)
        run_layout.addWidget(QLabel("실행 로그"))
        run_layout.addWidget(self.output_text)
        tabs.addTab(run_tab, "Run")

        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        summary_layout.addWidget(self.summary_text)
        tabs.addTab(summary_tab, "Summary")

        validation_tab = QWidget()
        validation_layout = QVBoxLayout(validation_tab)
        validation_layout.addWidget(self.validation_table)
        tabs.addTab(validation_tab, "Validation")

        calls_tab = QSplitter(Qt.Orientation.Horizontal)
        calls_tab.addWidget(self.call_list)
        calls_tab.addWidget(self.json_text)
        calls_tab.setSizes([360, 620])
        tabs.addTab(calls_tab, "API / Proxy Calls")

        artifacts_tab = QWidget()
        artifacts_layout = QVBoxLayout(artifacts_tab)
        artifacts_layout.addWidget(self.artifact_list)
        tabs.addTab(artifacts_tab, "Artifacts")

        return tabs

    def _connect_signals(self) -> None:
        self.run_button.clicked.connect(self.run_selected_scenario)
        self.refresh_button.clicked.connect(self.reload_runs)
        self.run_list.currentItemChanged.connect(self.on_run_selected)
        self.call_list.currentItemChanged.connect(self.on_call_selected)
        self.artifact_list.currentItemChanged.connect(self.on_artifact_selected)

    def reload_scenarios(self) -> None:
        self.scenario_combo.clear()
        for path in sorted(SCENARIOS_DIR.glob("*.json")):
            self.scenario_combo.addItem(path.name, str(path))

    def reload_runs(self) -> None:
        self.run_entries = load_run_index()
        self.run_list.clear()
        for entry in reversed(self.run_entries[-200:]):
            item = QListWidgetItem(
                f"{entry.run_id}  {entry.status}  {entry.mode}  {entry.scenario_id}"
            )
            item.setData(Qt.ItemDataRole.UserRole, entry.run_id)
            self.run_list.addItem(item)

    # @managed-contract contract_id=harness_ui.run_selected_scenario level=P1
    def run_selected_scenario(self) -> None:
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            QMessageBox.warning(self, "실행 중", "이미 실행 중인 scenario가 있습니다.")
            return
        scenario_path = self.scenario_combo.currentData()
        if not scenario_path:
            return
        args = [
            "-m",
            "testing.harness.run_with_servers",
            "--scenario",
            str(scenario_path),
        ]
        mode = self.mode_combo.currentText()
        if mode in {"A", "B"}:
            args.extend(["--mode", mode])

        self.output_text.clear()
        self.status_label.setText("실행 중")
        self.run_button.setEnabled(False)
        self.process = QProcess(self)
        self.process.setWorkingDirectory(str(CONTROL_PLANE_DIR))
        self.process.setProgram(sys.executable)
        self.process.setArguments(args)
        self.process.readyReadStandardOutput.connect(self._append_stdout)
        self.process.readyReadStandardError.connect(self._append_stderr)
        self.process.finished.connect(self._on_process_finished)
        self.process.start()

    def _append_stdout(self) -> None:
        if not self.process:
            return
        text = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self.output_text.appendPlainText(text.rstrip())

    def _append_stderr(self) -> None:
        if not self.process:
            return
        text = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace")
        self.output_text.appendPlainText(text.rstrip())

    def _on_process_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        self.status_label.setText(f"완료 exit={exit_code}")
        self.run_button.setEnabled(True)
        self.reload_runs()

    # @managed-contract contract_id=harness_ui.load_run_artifacts level=P1
    def on_run_selected(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        run_id = item.data(Qt.ItemDataRole.UserRole)
        self.selected_run_dir = RUNS_DIR / run_id
        self._load_summary()
        self._load_validation_report()
        self._load_call_list()
        self._load_artifact_list()

    def _load_summary(self) -> None:
        summary_path = self.selected_run_dir / "summary.md" if self.selected_run_dir else None
        self.summary_text.setPlainText(summary_path.read_text(encoding="utf-8") if summary_path and summary_path.exists() else "")

    def _load_validation_report(self) -> None:
        self.validation_table.setRowCount(0)
        report_path = self.selected_run_dir / "validation_report.json" if self.selected_run_dir else None
        if not report_path or not report_path.exists():
            return
        report = read_json(report_path)
        results = report.get("results", [])
        self.validation_table.setRowCount(len(results))
        for row_index, result in enumerate(results):
            values = [
                result.get("status", ""),
                result.get("name", ""),
                result.get("message", ""),
                pretty_json(result.get("details", {})),
            ]
            for col_index, value in enumerate(values):
                self.validation_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
        self.validation_table.resizeColumnsToContents()

    def _load_call_list(self) -> None:
        self.call_list.clear()
        self.json_text.clear()
        if not self.selected_run_dir:
            return
        for directory_name in ("api_calls", "proxy_calls"):
            directory = self.selected_run_dir / directory_name
            if not directory.exists():
                continue
            for path in sorted(directory.glob("*.json")):
                item = QListWidgetItem(f"{directory_name}/{path.name}")
                item.setData(Qt.ItemDataRole.UserRole, str(path))
                self.call_list.addItem(item)

    def _load_artifact_list(self) -> None:
        self.artifact_list.clear()
        if not self.selected_run_dir:
            return
        for path in sorted(self.selected_run_dir.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}:
                item = QListWidgetItem(str(path.relative_to(self.selected_run_dir)))
                item.setData(Qt.ItemDataRole.UserRole, str(path))
                self.artifact_list.addItem(item)

    def on_call_selected(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        path = Path(item.data(Qt.ItemDataRole.UserRole))
        self.json_text.setPlainText(pretty_json(read_json(path)))

    def on_artifact_selected(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        path = Path(item.data(Qt.ItemDataRole.UserRole))
        if path.suffix.lower() == ".json":
            self.json_text.setPlainText(pretty_json(read_json(path)))
        else:
            self.json_text.setPlainText(path.read_text(encoding="utf-8", errors="replace"))


def main() -> int:
    app = QApplication(sys.argv)
    window = HarnessUi()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
