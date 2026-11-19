from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_SOURCE = Path(r"C:\temp\mongo_db\dl_monitoring.sqlite3")
DEFAULT_OUTPUT_ROOT = Path(__file__).resolve().parent
FIELDNAMES = [
    "timestamp",
    "case_id",
    "sample_id",
    "period",
    "image_category",
    "image_class",
    "confidence",
    "metric",
]


def _identifier(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def _dataset_identity(image_category: str, image_class: str) -> tuple[str, str]:
    suffix = f"{_identifier(image_category)}-{_identifier(image_class)}"
    return f"CASE-019-{suffix}", f"CASE-019-{suffix}_object_detection_confidence"


def _export_combination(
    connection: sqlite3.Connection,
    output_root: Path,
    source_db: Path,
    image_category: str,
    image_class: str,
) -> dict[str, object]:
    case_id, directory_name = _dataset_identity(image_category, image_class)
    output_dir = output_root / directory_name
    output_dir.mkdir(parents=True, exist_ok=True)
    data_path = output_dir / "data.csv.gz"
    row_count = 0
    minimum_time: str | None = None
    maximum_time: str | None = None
    minimum_confidence: float | None = None
    maximum_confidence: float | None = None
    confidence_total = 0.0

    rows = connection.execute(
        """
        SELECT mongo_id, confidence_score, recorded_at
        FROM dl_monitoring_data
        WHERE image_category = ? AND image_class = ?
          AND confidence_score IS NOT NULL AND recorded_at IS NOT NULL
        ORDER BY recorded_at, mongo_id
        """,
        (image_category, image_class),
    ).fetchall()
    split_index = max(1, len(rows) // 2)
    drift_start = str(rows[split_index][2]) if rows else None
    with gzip.open(data_path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for index, (mongo_id, confidence_score, recorded_at) in enumerate(rows):
            confidence = float(confidence_score)
            timestamp = str(recorded_at)
            writer.writerow(
                {
                    "timestamp": timestamp,
                    "case_id": case_id,
                    "sample_id": mongo_id,
                    "period": "reference" if index < split_index else "current",
                    "image_category": image_category,
                    "image_class": image_class,
                    "confidence": confidence,
                    "metric": confidence,
                }
            )
            row_count += 1
            minimum_time = timestamp if minimum_time is None else min(minimum_time, timestamp)
            maximum_time = timestamp if maximum_time is None else max(maximum_time, timestamp)
            minimum_confidence = confidence if minimum_confidence is None else min(minimum_confidence, confidence)
            maximum_confidence = confidence if maximum_confidence is None else max(maximum_confidence, confidence)
            confidence_total += confidence

    metadata: dict[str, object] = {
        "case_id": case_id,
        "case_name": "object_detection_confidence",
        "description": f"Object-detection confidence for {image_category} / {image_class}.",
        "data_file": "data.csv.gz",
        "row_count": row_count,
        "frequency": "irregular_event_time",
        "start_inclusive": minimum_time,
        "end_inclusive": maximum_time,
        "drift_start": drift_start,
        "columns": FIELDNAMES,
        "dimensions": {"image_category": image_category, "image_class": image_class},
        "source": {
            "database_file": str(source_db),
            "table": "dl_monitoring_data",
            "exported_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "where": {"image_category": image_category, "image_class": image_class},
            "field_mapping": {
                "recorded_at": "timestamp",
                "mongo_id": "sample_id",
                "confidence_score": ["confidence", "metric"],
            },
        },
        "statistics": {
            "minimum_confidence": minimum_confidence,
            "mean_confidence": confidence_total / row_count if row_count else None,
            "maximum_confidence": maximum_confidence,
        },
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"directory": directory_name, **metadata}


def export_datasets(source_db: Path, output_root: Path) -> list[dict[str, object]]:
    with sqlite3.connect(source_db.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        combinations = connection.execute(
            """
            SELECT image_category, image_class
            FROM dl_monitoring_data
            WHERE image_category IS NOT NULL AND image_class IS NOT NULL
            GROUP BY image_category, image_class
            ORDER BY image_category, image_class
            """
        ).fetchall()
        return [
            _export_combination(connection, output_root, source_db, str(category), str(image_class))
            for category, image_class in combinations
        ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Split object-detection confidence data for Test Feeder.")
    parser.add_argument("--source-db", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    datasets = export_datasets(args.source_db, args.output_root)
    print(json.dumps({
        "dataset_count": len(datasets),
        "row_count": sum(int(item["row_count"]) for item in datasets),
        "datasets": [item["directory"] for item in datasets],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
