from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# @managed-contract contract_id=drift_algorithm.core.DriftResult level=P0
@dataclass
class DriftResult:
    method_id: str
    method_name: str
    method_category: str
    variant_id: str | None
    drift_detected: bool | None
    severity: str
    drift_score: float | None = None
    p_value: float | None = None
    test_statistic: float | None = None
    threshold: float | None = None
    measurements: dict[str, Any] = field(default_factory=dict)
    interpretation: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# @managed-contract contract_id=drift_algorithm.core.not_applicable_result level=P0
def not_applicable_result(
    *,
    method_id: str,
    method_name: str,
    method_category: str,
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
) -> DriftResult:
    return DriftResult(
        method_id=method_id,
        method_name=method_name,
        method_category=method_category,
        variant_id=variant_id,
        drift_detected=None,
        severity="not_applicable",
        warnings=[warning],
        metadata=metadata or {},
        interpretation=warning,
    )
