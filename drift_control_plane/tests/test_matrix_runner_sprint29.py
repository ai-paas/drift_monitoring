from __future__ import annotations

from pathlib import Path

from testing.harness.matrix_runner import DEFAULT_MATRIX_PATH, load_matrix_pack, run_matrix


def test_representative_pack_loads_expected_rows() -> None:
    pack = load_matrix_pack("v2_representative")

    assert pack is not None
    assert pack["packId"] == "v2_representative"
    assert len(pack["rowIds"]) == 10


def test_representative_pack_dry_run_selects_seed_modes() -> None:
    result = run_matrix(
        matrix_path=DEFAULT_MATRIX_PATH,
        pack_id="v2_representative",
        dry_run=True,
    )

    coverage = result["coverageSummary"]
    assert coverage["dryRunResults"] == 11
    assert coverage["failedResults"] == 0
    assert coverage["skippedResults"] == 1
    assert coverage["skipReasonCounts"]["pack_filter"] == 1
    assert result["manifest"]["filters"]["packId"] == "v2_representative"


def test_generated_matrix_reports_candidate_gap_reasons() -> None:
    generated_path = Path("testing/harness/matrix/generated/v2_matrix_generated.json")
    result = run_matrix(
        matrix_path=generated_path,
        status_filter="all",
        dry_run=True,
    )

    coverage = result["coverageSummary"]
    assert coverage["dryRunResults"] == 12
    assert coverage["skippedResults"] == 178
    assert coverage["candidateGapReasonCounts"]["scenario_missing"] == 178
    assert coverage["candidateGapReasonCounts"]["dataset_adapter_mapping_missing"] == 178
    assert coverage["candidateGapReasonCounts"]["runtime_method_key_not_selected"] == 178
