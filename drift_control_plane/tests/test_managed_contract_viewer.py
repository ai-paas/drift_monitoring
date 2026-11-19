from __future__ import annotations

import os

import pytest

from shared.managed_contract_repository import ContractQuery, list_managed_contracts
from tools.managed_contract_viewer import smoke_check


def test_managed_contract_repository_loads_active_rows() -> None:
    rows = list_managed_contracts(ContractQuery(status="active", owner_module="drift_control_plane"))

    assert rows
    assert all(row["status"] == "active" for row in rows)
    assert all(row["owner_module"] == "drift_control_plane" for row in rows)


def test_managed_contract_viewer_offscreen_smoke() -> None:
    pytest.importorskip("PyQt6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    assert smoke_check() == 0
