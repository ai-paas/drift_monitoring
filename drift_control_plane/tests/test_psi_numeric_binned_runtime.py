from __future__ import annotations

from drift_server.app.runtime_methods.psi_numeric_binned import _comparison_values


def test_psi_comparison_values_use_previous_bucket_as_reference_when_periods_are_split() -> None:
    previous_state = {
        "lastBucketValues": [
            {"time": "2026-06-30T20:00:00Z", "value": 10.0, "bin": "0-20"},
            {"time": "2026-06-30T20:01:00Z", "value": 30.0, "bin": "20-40"},
        ]
    }
    current_values = [
        {"time": "2026-07-01T00:00:00Z", "value": 70.0, "period": "current", "bin": "60-80"},
        {"time": "2026-07-01T00:01:00Z", "value": 90.0, "period": "current", "bin": "80-100"},
    ]

    values = _comparison_values(current_values, previous_state, {})

    assert [row["period"] for row in values] == ["reference", "reference", "current", "current"]
    assert [row["bin"] for row in values] == ["0-20", "20-40", "60-80", "80-100"]


def test_psi_comparison_values_preserve_explicit_reference_current_payload() -> None:
    explicit_values = [
        {"time": "2026-06-30T00:00:00Z", "value": 10.0, "period": "reference", "bin": "0-20"},
        {"time": "2026-07-01T00:00:00Z", "value": 90.0, "period": "current", "bin": "80-100"},
    ]

    values = _comparison_values(explicit_values, {"lastBucketValues": [{"value": 1.0}]}, {})

    assert values == explicit_values
