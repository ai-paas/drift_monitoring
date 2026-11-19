from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.multivariate_process_window import run_multivariate_process_window


def _assignment(variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "feature_cols": ["x1", "x2", "x3"],
        "min_reference_size": 20,
        "min_current_size": 20,
        **params,
    }
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": "multivariate_process_window",
        "params_json": json.dumps(payload),
    }


def _bucket(current_shift: tuple[float, float, float] = (1.5, 1.0, -1.2)) -> dict:
    start = datetime(2026, 12, 1, tzinfo=timezone.utc)
    values = []
    for index in range(80):
        x1 = -1.0 + (index % 20) / 10.0
        x2 = (index % 10) / 10.0
        x3 = ((index * 2) % 11) / 10.0
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"x1": x1, "x2": x2, "x3": x3},
                "metric": x1 + x2 + x3,
            }
        )
    current_start = start + timedelta(days=1)
    for index in range(80):
        x1 = -1.0 + (index % 20) / 10.0 + current_shift[0]
        x2 = (index % 10) / 10.0 + current_shift[1]
        x3 = ((index * 2) % 11) / 10.0 + current_shift[2]
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {"x1": x1, "x2": x2, "x3": x3},
                "metric": x1 + x2 + x3,
            }
        )
    return {
        "bucket_id": "bucket-mv-001",
        "source_id": "source-mv-001",
        "adapter_id": "adapter-mv-001",
        "feature_id": "multivariate",
        "window_start": "2026-12-01T00:00:00Z",
        "window_end": "2026-12-02T01:19:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values, "featureColumns": ["x1", "x2", "x3"]}),
    }


def test_registry_resolves_multivariate_aliases() -> None:
    assert get_runtime_method("multivariate_process_window") is run_multivariate_process_window
    assert get_runtime_method("mewma_window") is run_multivariate_process_window
    assert get_runtime_method("hotelling_t2_window") is run_multivariate_process_window
    assert get_runtime_method("mahalanobis_window") is run_multivariate_process_window


def test_multivariate_runtime_detects_mewma_shift() -> None:
    output = run_multivariate_process_window(
        _assignment("MEWMA_STANDARD", **{"lambda": 0.3}, control_limit=5.0),
        _bucket(),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["MEWMA_STATISTIC"] > 5.0


def test_multivariate_runtime_detects_mewma_mahalanobis_shift() -> None:
    output = run_multivariate_process_window(
        _assignment(
            "MEWMA_WITH_MAHALANOBIS_D2",
            covariance_estimator="regularized",
            regularization_strength=0.1,
            control_limit=0.1,
        ),
        _bucket(),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["MAHALANOBIS_DISTANCE"] >= 0.0


def test_multivariate_runtime_detects_hotelling_two_sample_shift() -> None:
    output = run_multivariate_process_window(
        _assignment("HOTELLING_T2_TWO_SAMPLE", alpha=0.05),
        _bucket(),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["FEATURE_DIMENSION"] == 3


def test_multivariate_runtime_detects_regularized_hotelling_shift() -> None:
    output = run_multivariate_process_window(
        _assignment("REGULARIZED_HOTELLING_T2", control_limit=0.1, regularization_strength=0.1),
        _bucket(),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["HOTELLING_T2_STATISTIC"] > 0.1


def test_multivariate_runtime_detects_mahalanobis_shift() -> None:
    output = run_multivariate_process_window(
        _assignment("WINDOW_MEAN_MAHALANOBIS", threshold=2.0),
        _bucket(),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["MAHALANOBIS_D2"] > 2.0


def test_multivariate_runtime_detects_sample_mahalanobis_outlier() -> None:
    output = run_multivariate_process_window(
        _assignment("SAMPLE_MAHALANOBIS_OUTLIER", threshold=10.0, min_current_size=10),
        _bucket(current_shift=(4.0, 4.0, -4.0)),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["OUTLIER_COUNT"] >= 1
