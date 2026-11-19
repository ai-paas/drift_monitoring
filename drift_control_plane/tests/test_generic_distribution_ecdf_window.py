from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.generic_distribution_ecdf_window import run_generic_distribution_ecdf_window


def _assignment(variant_id: str) -> dict:
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": "generic_distribution_ecdf_window",
        "params_json": json.dumps(
            {
                "variant_id": variant_id,
                "alpha": 0.05,
                "threshold_or_alpha": 0.05,
                "min_reference_size": 20,
                "min_current_size": 20,
            }
        ),
    }


def _bucket(reference_shift: float = 0.0, current_shift: float = 20.0) -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = []
    for index in range(80):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(index % 10) + reference_shift,
                "period": "reference",
            }
        )
    current_start = start + timedelta(days=1)
    for index in range(80):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(index % 10) + current_shift,
                "period": "current",
            }
        )
    return {
        "bucket_id": "bucket-001",
        "source_id": "source-001",
        "adapter_id": "adapter-001",
        "feature_id": "score",
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-02T01:19:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }


def test_registry_resolves_distribution_ecdf_aliases() -> None:
    assert get_runtime_method("generic_distribution_ecdf_window") is run_generic_distribution_ecdf_window
    assert get_runtime_method("ks_test_window") is run_generic_distribution_ecdf_window
    assert get_runtime_method("anderson_darling_window") is run_generic_distribution_ecdf_window
    assert get_runtime_method("energy_distance_window") is run_generic_distribution_ecdf_window
    assert get_runtime_method("univariate_energy_distance") is run_generic_distribution_ecdf_window
    assert get_runtime_method("energy_distance_permutation_test") is run_generic_distribution_ecdf_window
    assert get_runtime_method("lsdd_window") is run_generic_distribution_ecdf_window
    assert get_runtime_method("least_squares_density_difference") is run_generic_distribution_ecdf_window
    assert get_runtime_method("permutation_lsdd") is run_generic_distribution_ecdf_window
    assert get_runtime_method("mmd_window") is run_generic_distribution_ecdf_window
    assert get_runtime_method("kernel_mmd_biased") is run_generic_distribution_ecdf_window
    assert get_runtime_method("kernel_mmd_unbiased") is run_generic_distribution_ecdf_window
    assert get_runtime_method("linear_time_mmd") is run_generic_distribution_ecdf_window


def test_generic_distribution_ecdf_runtime_detects_supported_ks_shift() -> None:
    output = run_generic_distribution_ecdf_window(_assignment("TWO_SAMPLE_KS_TWO_SIDED"), _bucket(), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 160


def test_generic_distribution_ecdf_runtime_executes_promoted_variant() -> None:
    output = run_generic_distribution_ecdf_window(_assignment("ONE_SAMPLE_KS_KNOWN_CDF"), _bucket(), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["diagnostics"]["algorithmMetadata"]["execution_policy"] == "two_sample_ks_reference_current"
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 160


def test_generic_distribution_ecdf_runtime_detects_energy_distance_shift() -> None:
    assignment = _assignment("UNIVARIATE_ENERGY_DISTANCE")
    params = json.loads(assignment["params_json"])
    params["threshold"] = 0.2
    assignment["params_json"] = json.dumps(params)

    output = run_generic_distribution_ecdf_window(assignment, _bucket(current_shift=2.5), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 160
    assert output["metrics"]["measurements"]["ENERGY_DISTANCE"] > 0.2


def test_generic_distribution_ecdf_runtime_executes_energy_permutation_variant() -> None:
    assignment = _assignment("ENERGY_DISTANCE_PERMUTATION_TEST")
    params = json.loads(assignment["params_json"])
    params.update({"permutation_count": 49, "random_seed": 56})
    assignment["params_json"] = json.dumps(params)

    output = run_generic_distribution_ecdf_window(assignment, _bucket(current_shift=2.5), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PERMUTATION_COUNT"] == 49


def test_generic_distribution_ecdf_runtime_detects_lsdd_shift() -> None:
    assignment = _assignment("LEAST_SQUARES_DENSITY_DIFFERENCE")
    params = json.loads(assignment["params_json"])
    params["threshold"] = 0.01
    assignment["params_json"] = json.dumps(params)

    output = run_generic_distribution_ecdf_window(assignment, _bucket(current_shift=2.5), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 160
    assert output["metrics"]["measurements"]["LSDD_SCORE"] > 0.01


def test_generic_distribution_ecdf_runtime_executes_lsdd_permutation_variant() -> None:
    assignment = _assignment("PERMUTATION_LSDD")
    params = json.loads(assignment["params_json"])
    params.update({"permutation_count": 49, "random_seed": 57})
    assignment["params_json"] = json.dumps(params)

    output = run_generic_distribution_ecdf_window(assignment, _bucket(current_shift=2.5), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PERMUTATION_COUNT"] == 49


def test_generic_distribution_ecdf_runtime_detects_mmd_biased_shift() -> None:
    assignment = _assignment("KERNEL_MMD_BIASED")
    params = json.loads(assignment["params_json"])
    params["threshold"] = 0.01
    assignment["params_json"] = json.dumps(params)

    output = run_generic_distribution_ecdf_window(assignment, _bucket(current_shift=2.5), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 160
    assert output["metrics"]["measurements"]["MMD_STATISTIC"] > 0.01


def test_generic_distribution_ecdf_runtime_executes_mmd_unbiased_variant() -> None:
    assignment = _assignment("KERNEL_MMD_UNBIASED")
    params = json.loads(assignment["params_json"])
    params["threshold"] = 0.01
    assignment["params_json"] = json.dumps(params)

    output = run_generic_distribution_ecdf_window(assignment, _bucket(current_shift=2.5), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 160


def test_generic_distribution_ecdf_runtime_detects_linear_time_mmd_feature_shift() -> None:
    assignment = _assignment("LINEAR_TIME_MMD")
    params = json.loads(assignment["params_json"])
    params.update({"feature_cols": ["x", "y"], "threshold": 0.01})
    assignment["runtime_method_key"] = "linear_time_mmd"
    assignment["params_json"] = json.dumps(params)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = []
    for index in range(80):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"x": float(index % 10), "y": float((index * 2) % 10)},
            }
        )
    current_start = start + timedelta(days=1)
    for index in range(80):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {"x": float(index % 10) + 3.0, "y": float((index * 2) % 10) + 3.0},
            }
        )
    bucket = {
        "bucket_id": "bucket-linear-mmd",
        "source_id": "source-001",
        "adapter_id": "adapter-001",
        "feature_id": "multivariate",
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-02T01:19:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }

    output = run_generic_distribution_ecdf_window(assignment, bucket, {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["diagnostics"]["algorithmMetadata"]["projection_policy"] == "feature_matrix_rbf_mmd"
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 160
