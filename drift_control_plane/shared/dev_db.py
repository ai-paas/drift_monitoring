from __future__ import annotations

import csv
import sqlite3
import threading
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT_DIR / "runtime" / "sprint2_dev.sqlite3"
MANAGED_CONTRACTS_CSV = ROOT_DIR / "managed_contracts.csv"
SQLITE_BUSY_TIMEOUT_MS = 30000
_SCHEMA_INITIALIZED_DB_PATHS: set[str] = set()
_INIT_LOCK = threading.Lock()


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=SQLITE_BUSY_TIMEOUT_MS / 1000)
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    db_key = _db_key(path)
    with _INIT_LOCK:
        if db_key not in _SCHEMA_INITIALIZED_DB_PATHS:
            ensure_schema(conn)
            _SCHEMA_INITIALIZED_DB_PATHS.add(db_key)
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS raw_event (
            source_id TEXT NOT NULL,
            row_index INTEGER NOT NULL,
            source_event_time TEXT NOT NULL,
            event_time TEXT NOT NULL,
            collected_at TEXT,
            source_clock_offset_ms INTEGER NOT NULL DEFAULT 0,
            metric REAL NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (source_id, row_index)
        );

        CREATE TABLE IF NOT EXISTS feed_state (
            source_id TEXT PRIMARY KEY,
            logical_cursor_time TEXT,
            inserted_rows INTEGER NOT NULL DEFAULT 0,
            future_rejected_rows INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS adapter_state (
            adapter_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            cursor_time TEXT,
            status TEXT NOT NULL DEFAULT 'ready',
            poll_count INTEGER NOT NULL DEFAULT 0,
            last_logical_now TEXT,
            diagnostics_json TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS metric_bucket (
            bucket_id TEXT PRIMARY KEY,
            adapter_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            feature_id TEXT NOT NULL,
            window_start TEXT NOT NULL,
            window_end TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            mean_value REAL,
            min_value REAL,
            max_value REAL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (adapter_id, feature_id, window_start, window_end)
        );

        CREATE TABLE IF NOT EXISTS source_method_assignment (
            assignment_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            adapter_id TEXT NOT NULL,
            feature_id TEXT NOT NULL,
            runtime_method_key TEXT NOT NULL,
            params_json TEXT NOT NULL,
            threshold_json TEXT NOT NULL,
            window_config_json TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS method_state (
            assignment_id TEXT PRIMARY KEY,
            state_json TEXT NOT NULL,
            last_bucket_id TEXT,
            last_bucket_end TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS method_run (
            method_run_id TEXT PRIMARY KEY,
            assignment_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            adapter_id TEXT NOT NULL,
            feature_id TEXT NOT NULL,
            bucket_id TEXT NOT NULL,
            window_start TEXT NOT NULL,
            window_end TEXT NOT NULL,
            run_status TEXT NOT NULL,
            level TEXT NOT NULL,
            score REAL,
            input_bucket_count INTEGER NOT NULL,
            result_json TEXT NOT NULL,
            error_message TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (assignment_id, bucket_id)
        );

        CREATE TABLE IF NOT EXISTS drift_event (
            event_id TEXT PRIMARY KEY,
            method_run_id TEXT NOT NULL UNIQUE,
            assignment_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            adapter_id TEXT NOT NULL,
            feature_id TEXT NOT NULL,
            event_start TEXT NOT NULL,
            event_end TEXT NOT NULL,
            event_level TEXT NOT NULL,
            event_title TEXT NOT NULL,
            score REAL,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS analysis_chart_registration (
            analysis_chart_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            assignment_id TEXT NOT NULL,
            chart_id TEXT NOT NULL,
            chart_definition_id TEXT NOT NULL,
            chart_definition_json TEXT NOT NULL,
            payload_adapter_key TEXT NOT NULL,
            payload_adapter_config_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (source_id, assignment_id, chart_id)
        );

        CREATE TABLE IF NOT EXISTS managed_contract (
            contract_id TEXT PRIMARY KEY,
            contract_level TEXT NOT NULL,
            contract_type TEXT NOT NULL,
            owner_module TEXT NOT NULL,
            file_path TEXT NOT NULL,
            qualified_name TEXT,
            source_of_truth_doc TEXT,
            input_contract TEXT,
            output_contract TEXT,
            dependent_tests TEXT,
            signature_hash TEXT,
            body_hash TEXT,
            content_hash TEXT,
            last_git_commit TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            description TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    _ensure_column(conn, "raw_event", "collected_at", "TEXT")
    _ensure_column(conn, "feed_state", "future_rejected_rows", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(conn, "adapter_state", "diagnostics_json", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(conn, "metric_bucket", "error_count", "INTEGER")
    _ensure_column(conn, "metric_bucket", "error_rate", "REAL")
    _ensure_column(conn, "metric_bucket", "mean_confidence", "REAL")
    _ensure_column(conn, "metric_bucket", "payload_json", "TEXT NOT NULL DEFAULT '{}'")
    _seed_managed_contracts(conn)
    conn.commit()


def _db_key(path: Path) -> str:
    return str(path.resolve())


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


# @managed-contract contract_id=drift_control_plane.dev_db.managed_contract_table level=P0
def _seed_managed_contracts(conn: sqlite3.Connection) -> None:
    if not MANAGED_CONTRACTS_CSV.exists():
        return
    with MANAGED_CONTRACTS_CSV.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            description, input_contract, output_contract = _managed_contract_descriptions(row)
            conn.execute(
                """
                INSERT INTO managed_contract (
                    contract_id, contract_level, contract_type, owner_module, file_path,
                    qualified_name, source_of_truth_doc, input_contract, output_contract,
                    dependent_tests, status, description, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(contract_id) DO UPDATE SET
                    contract_level = excluded.contract_level,
                    contract_type = excluded.contract_type,
                    owner_module = excluded.owner_module,
                    file_path = excluded.file_path,
                    qualified_name = excluded.qualified_name,
                    source_of_truth_doc = excluded.source_of_truth_doc,
                    input_contract = excluded.input_contract,
                    output_contract = excluded.output_contract,
                    dependent_tests = excluded.dependent_tests,
                    status = excluded.status,
                    description = excluded.description,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    row["contract_id"],
                    row["contract_level"],
                    row["contract_type"],
                    row["owner_module"],
                    row["file_path"],
                    row.get("qualified_name") or None,
                    row.get("source_of_truth_doc") or None,
                    input_contract,
                    output_contract,
                    row.get("dependent_tests") or None,
                    row.get("status") or "active",
                    description,
                ),
            )


def _managed_contract_descriptions(row: dict[str, str]) -> tuple[str, str, str]:
    contract_id = row["contract_id"]
    level = row["contract_level"]
    contract_type = row["contract_type"]
    owner = row["owner_module"]
    file_path = row["file_path"]
    qualified_name = row.get("qualified_name") or "(파일 전체)"
    source_doc = row.get("source_of_truth_doc") or "(미지정)"
    tests = row.get("dependent_tests") or "(미지정)"
    base_description = row.get("description") or "핵심 계약 관리 대상"

    approval_rule = (
        "P0 핵심 계약이므로 수정이 필요하면 구현을 멈추고 사용자 동의를 먼저 받아야 한다."
        if level == "P0"
        else "P1 관리 대상이므로 변경 전 영향 범위를 확인하고 계약 변경 가능성이 있으면 사용자 동의를 받아야 한다."
    )
    type_description = _managed_contract_type_description(contract_type)

    description = f"{base_description} {type_description} {approval_rule}"
    input_contract = (
        f"관리 대상: {qualified_name}\n"
        f"소유 모듈: {owner}\n"
        f"파일 위치: {file_path}\n"
        f"기준 문서: {source_doc}\n"
        "검토 기준: 이 항목의 이름, 입력 구조, 필수 필드, 호출 조건, 저장 형식 또는 공개 API 형태가 바뀌는지 확인한다."
    )
    output_contract = (
        f"영향 범위: {contract_id}\n"
        f"검증 기준: {tests}\n"
        "변경 시 확인할 것: 이 항목을 호출하거나 읽는 서버, UI, payload adapter, chart runtime, 테스트 데이터가 같은 계약을 계속 만족해야 한다. "
        "계약이 바뀌면 기준 문서와 managed_contract 테이블 설명도 함께 갱신한다."
    )
    return description, input_contract, output_contract


def _managed_contract_type_description(contract_type: str) -> str:
    if contract_type in {"python_function", "python_method"}:
        return "이 함수/메서드는 모듈 간 호출 경계에 있으므로 인자, 반환값, 예외 처리, 부수효과가 계약이다."
    if contract_type == "python_dataclass":
        return "이 자료구조는 필드 이름과 의미가 하위 모듈 또는 서버 응답에 전달되는 계약이다."
    if contract_type in {"javascript_function", "javascript_global"}:
        return "이 JavaScript API는 브라우저 UI, 테스트, runtime 연동에서 직접 참조되는 계약이다."
    if contract_type == "javascript_constant":
        return "이 상수는 component, renderer, payload 또는 UI state 매핑의 기준 목록이다."
    if contract_type in {"json_contract", "csv_contract"}:
        return "이 데이터 파일은 코드가 읽는 원본 계약이므로 key, column, value shape가 중요하다."
    if contract_type == "api_endpoint":
        return "이 API endpoint는 request/response shape와 저장 책임이 외부 계약이다."
    if contract_type == "document":
        return "이 문서는 구현 판단의 source of truth이므로 코드 변경과 함께 내용 일치가 필요하다."
    return "이 항목은 핵심 관리 대상으로 등록된 계약이다."


def reset_source(conn: sqlite3.Connection, source_id: str | None) -> None:
    if source_id:
        conn.execute("DELETE FROM raw_event WHERE source_id = ?", (source_id,))
        conn.execute("DELETE FROM feed_state WHERE source_id = ?", (source_id,))
        conn.execute("DELETE FROM metric_bucket WHERE source_id = ?", (source_id,))
        conn.execute("DELETE FROM adapter_state WHERE source_id = ?", (source_id,))
        conn.execute("DELETE FROM drift_event WHERE source_id = ?", (source_id,))
        conn.execute("DELETE FROM method_run WHERE source_id = ?", (source_id,))
        conn.execute("DELETE FROM analysis_chart_registration WHERE source_id = ?", (source_id,))
        conn.execute(
            "DELETE FROM method_state WHERE assignment_id IN (SELECT assignment_id FROM source_method_assignment WHERE source_id = ?)",
            (source_id,),
        )
        conn.execute("DELETE FROM source_method_assignment WHERE source_id = ?", (source_id,))
    else:
        conn.execute("DELETE FROM raw_event")
        conn.execute("DELETE FROM feed_state")
        conn.execute("DELETE FROM metric_bucket")
        conn.execute("DELETE FROM adapter_state")
        conn.execute("DELETE FROM drift_event")
        conn.execute("DELETE FROM method_run")
        conn.execute("DELETE FROM analysis_chart_registration")
        conn.execute("DELETE FROM method_state")
        conn.execute("DELETE FROM source_method_assignment")
    conn.commit()
