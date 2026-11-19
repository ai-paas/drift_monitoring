from __future__ import annotations

import csv
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shared.dev_db import MANAGED_CONTRACTS_CSV, ROOT_DIR, _managed_contract_descriptions, connect


REPO_ROOT = ROOT_DIR.parent


@dataclass(frozen=True)
class ContractQuery:
    status: str | None = "active"
    owner_module: str | None = None
    contract_level: str | None = None
    text: str | None = None


# @managed-contract contract_id=managed_contract_repository.import_managed_contracts_csv level=P1
def import_managed_contracts_csv(
    csv_path: str | Path = MANAGED_CONTRACTS_CSV,
    db_path: str | Path | None = None,
) -> int:
    """Import managed_contracts.csv into the development SQLite DB."""
    path = Path(csv_path)
    imported = 0
    with connect(db_path) as conn:
        with path.open(encoding="utf-8-sig", newline="") as file:
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
                imported += 1
        conn.commit()
    return imported


# @managed-contract contract_id=managed_contract_repository.list_managed_contracts level=P1
def list_managed_contracts(
    query: ContractQuery | None = None,
    db_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    query = query or ContractQuery()
    clauses: list[str] = []
    params: list[str] = []
    if query.status:
        clauses.append("status = ?")
        params.append(query.status)
    if query.owner_module:
        clauses.append("owner_module = ?")
        params.append(query.owner_module)
    if query.contract_level:
        clauses.append("contract_level = ?")
        params.append(query.contract_level)
    if query.text:
        clauses.append(
            """(
                contract_id LIKE ?
                OR owner_module LIKE ?
                OR file_path LIKE ?
                OR COALESCE(qualified_name, '') LIKE ?
                OR COALESCE(description, '') LIKE ?
            )"""
        )
        like_text = f"%{query.text}%"
        params.extend([like_text] * 5)

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT
                contract_id, contract_level, contract_type, owner_module, file_path,
                COALESCE(qualified_name, '') AS qualified_name,
                COALESCE(source_of_truth_doc, '') AS source_of_truth_doc,
                COALESCE(input_contract, '') AS input_contract,
                COALESCE(output_contract, '') AS output_contract,
                COALESCE(dependent_tests, '') AS dependent_tests,
                status,
                COALESCE(description, '') AS description
            FROM managed_contract
            {where_sql}
            ORDER BY owner_module, contract_level, contract_id
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def list_owner_modules(db_path: str | Path | None = None) -> list[str]:
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT DISTINCT owner_module FROM managed_contract WHERE status = 'active' ORDER BY owner_module"
        ).fetchall()
    return [str(row["owner_module"]) for row in rows]


# @managed-contract contract_id=managed_contract_repository.git_file_statuses level=P1
def git_file_statuses(repo_root: str | Path = REPO_ROOT) -> dict[str, str]:
    """Return git porcelain status by repository-relative file path."""
    root = Path(repo_root)
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return {}

    statuses: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        code = line[:2].strip() or "clean"
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        statuses[path_text.replace("\\", "/")] = code
    return statuses
