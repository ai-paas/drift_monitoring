from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path


START = datetime(2026, 1, 1, 0, 0)
END = datetime(2027, 1, 1, 0, 0)
TOTAL_MINUTES = int((END - START).total_seconds() // 60)
DRIFT_START = datetime(2026, 7, 1, 0, 0)
TRANSITION_MINUTES = 60 * 24 * 60
WINDOW_MINUTES = 60


CASE_NAMES = {
    "CASE-001": "numeric_location_shift",
    "CASE-002": "numeric_tail_and_shape_change",
    "CASE-003": "numeric_variance_spread",
    "CASE-004": "binned_numeric_population_shift",
    "CASE-005": "categorical_proportion_shift",
    "CASE-006": "binary_event_rate_shift",
    "CASE-007": "probability_vector_shift",
    "CASE-008": "multivariate_embedding_shift",
    "CASE-009": "multivariate_local_density_or_anomaly",
    "CASE-010": "stream_numeric_mean_shift",
    "CASE-011": "stream_error_rate_and_performance",
    "CASE-012": "supervised_concept_boundary_shift",
    "CASE-013": "text_topic_semantic_shift",
    "CASE-014": "explanation_importance_shift",
    "CASE-015": "annotation_label_quality_shift",
    "CASE-016": "graph_or_feature_map_representation_shift",
}


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def weighted_choice(rng: random.Random, items: list[str], weights: list[float]) -> str:
    threshold = rng.random() * sum(weights)
    running = 0.0
    for item, weight in zip(items, weights):
        running += weight
        if threshold <= running:
            return item
    return items[-1]


def timestamp_context(index: int) -> dict[str, object]:
    ts = START + timedelta(minutes=index)
    after_start = (ts - DRIFT_START).total_seconds() / 60
    abrupt = 1.0 if ts >= DRIFT_START else 0.0
    gradual = clamp(after_start / TRANSITION_MINUTES)
    seasonal = 1.0 if ts.month in {3, 6, 9, 12} else 0.0
    yearly_angle = 2.0 * math.pi * index / TOTAL_MINUTES
    weekly_angle = 2.0 * math.pi * (index % (60 * 24 * 7)) / (60 * 24 * 7)
    cycle_phase = (index // (60 * 24 * 30)) % 4
    return {
        "timestamp": ts,
        "window_id": index // WINDOW_MINUTES,
        "is_reference": ts < DRIFT_START,
        "abrupt": abrupt,
        "gradual": gradual,
        "seasonal": seasonal,
        "yearly_sin": math.sin(yearly_angle),
        "weekly_sin": math.sin(weekly_angle),
        "cycle_phase": cycle_phase,
    }


def common_row(case_id: str, index: int, ctx: dict[str, object]) -> dict[str, object]:
    ts = ctx["timestamp"]
    return {
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "case_id": case_id,
        "sample_id": f"{case_id}-{index:06d}",
        "window_id": ctx["window_id"],
        "period": "reference" if ctx["is_reference"] else "current",
        "drift_start": DRIFT_START.strftime("%Y-%m-%d %H:%M:%S"),
        "abrupt_strength": round(float(ctx["abrupt"]), 6),
        "gradual_strength": round(float(ctx["gradual"]), 6),
        "season_factor": round(float(ctx["seasonal"]), 6),
        "cycle_phase": ctx["cycle_phase"],
    }


def case_001(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    mu = 0.75 * float(ctx["abrupt"]) + 0.35 * float(ctx["seasonal"]) + 0.25 * (int(ctx["cycle_phase"]) - 1)
    value = rng.gauss(mu, 1.0)
    return {"x": round(value, 6), "reference_mean": 0.0, "current_mean": round(mu, 6)}


def case_002(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    minute_of_day = index % (60 * 24)
    is_current_sample = (not bool(ctx["is_reference"])) and minute_of_day >= (60 * 12)
    tail_weight = (
        clamp(0.22 + 0.48 * float(ctx["gradual"]) + 0.08 * float(ctx["seasonal"]))
        if is_current_sample
        else 0.04
    )
    if rng.random() < tail_weight:
        if is_current_sample:
            value = rng.choice([-1, 1]) * abs(rng.gauss(0, 3.6)) + rng.choice([-1.25, 1.25])
        else:
            value = rng.choice([-1, 1]) * abs(rng.gauss(0, 2.2))
        component = "tail"
    else:
        value = rng.gauss(0.25 if is_current_sample else 0.0, 1.0)
        component = "body"
    period = "current" if is_current_sample else "reference"
    return {"period": period, "x": round(value, 6), "tail_weight": round(tail_weight, 6), "mixture_component": component}


def case_003(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    minute_of_day = index % (60 * 24)
    is_current_sample = (not bool(ctx["is_reference"])) and minute_of_day >= (60 * 12)
    sigma = 1.85 + 0.45 * float(ctx["seasonal"]) if is_current_sample else 1.0
    value = rng.gauss(0, sigma)
    period = "current" if is_current_sample else "reference"
    return {"period": period, "x": round(value, 6), "std_target": round(sigma, 6), "abs_deviation": round(abs(value), 6)}


def case_004(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    strength = max(float(ctx["gradual"]), 0.75 * float(ctx["abrupt"]))
    score = clamp(rng.betavariate(2.2 + 2.8 * strength, 5.0 - 2.0 * strength)) * 100
    bin_id = min(4, int(score // 20))
    return {"score": round(score, 6), "score_bin": f"{bin_id * 20}-{bin_id * 20 + 20}", "bin_index": bin_id}


def case_005(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    minute_in_hour = index % WINDOW_MINUTES
    is_current_sample = minute_in_hour >= (WINDOW_MINUTES // 2)
    strength = float(ctx["abrupt"]) if is_current_sample else 0.0
    categories = ["A", "B", "C", "D"]
    base = [0.50, 0.30, 0.20, 0.00]
    drifted = [0.10, 0.10, 0.70, 0.10]
    weights = [(1 - strength) * b + strength * d for b, d in zip(base, drifted)]
    threshold = ((minute_in_hour % (WINDOW_MINUTES // 2)) + 0.5) / (WINDOW_MINUTES // 2)
    cumulative = 0.0
    category = categories[-1]
    for candidate, weight in zip(categories, weights):
        cumulative += weight
        if threshold <= cumulative:
            category = candidate
            break
    period = "current" if is_current_sample else "reference"
    return {"period": period, "category": category, "category_weight_c": round(weights[2], 6)}


def case_006(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    probability = clamp(0.08 + 0.34 * float(ctx["abrupt"]))
    event = 1 if rng.random() < probability else 0
    return {"event": event, "event_probability": round(probability, 6), "group": "current" if ctx["abrupt"] else "reference"}


def case_007(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    minute_in_hour = index % WINDOW_MINUTES
    is_current_sample = minute_in_hour >= (WINDOW_MINUTES // 2)
    strength = float(ctx["abrupt"]) if is_current_sample else 0.0
    base = [0.40, 0.25, 0.20, 0.10, 0.05]
    drifted = [0.10, 0.10, 0.20, 0.35, 0.25]
    probs = [(1 - strength) * b + strength * d for b, d in zip(base, drifted)]
    labels = ["p0", "p1", "p2", "p3", "p4"]
    threshold = ((minute_in_hour % (WINDOW_MINUTES // 2)) + 0.5) / (WINDOW_MINUTES // 2)
    cumulative = 0.0
    label = labels[-1]
    for candidate, probability in zip(labels, probs):
        cumulative += probability
        if threshold <= cumulative:
            label = candidate
            break
    period = "current" if is_current_sample else "reference"
    return {
        "period": period,
        "category": label,
        "class_label": label,
        "p0": round(probs[0], 6),
        "p1": round(probs[1], 6),
        "p2": round(probs[2], 6),
        "p3": round(probs[3], 6),
        "p4": round(probs[4], 6),
    }


def case_008(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    minute_in_hour = index % 60
    is_current_sample = minute_in_hour >= 30
    strength = max(float(ctx["gradual"]), float(ctx["abrupt"])) if is_current_sample else 0.0
    angle = 2 * math.pi * int(ctx["cycle_phase"]) / 4
    cx = 1.4 * strength + 0.35 * math.cos(angle)
    cy = 1.0 * strength + 0.35 * math.sin(angle)
    e1 = rng.gauss(cx, 0.75)
    e2 = rng.gauss(cy, 0.75)
    return {
        "period": "current" if is_current_sample else "reference",
        "embedding_x": round(e1, 6),
        "embedding_y": round(e2, 6),
        "centroid_x": round(cx, 6),
        "centroid_y": round(cy, 6),
    }


def case_009(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    strength = max(float(ctx["abrupt"]), float(ctx["gradual"]))
    anomaly_probability = clamp(0.02 + 0.24 * strength + 0.04 * float(ctx["seasonal"]))
    is_anomaly = rng.random() < anomaly_probability
    if is_anomaly:
        x = rng.gauss(3.0, 0.45)
        y = rng.gauss(2.7, 0.55)
        cluster = "novel"
    else:
        x = rng.gauss(0, 0.85)
        y = rng.gauss(0, 0.85)
        cluster = "baseline"
    return {"embedding_x": round(x, 6), "embedding_y": round(y, 6), "cluster": cluster, "anomaly_score": round(math.hypot(x, y), 6)}


def case_010(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    level = 0.50 + 0.30 * float(ctx["abrupt"]) + 0.12 * float(ctx["weekly_sin"])
    metric = rng.gauss(level, 0.06)
    threshold = 0.68
    return {"metric": round(metric, 6), "target_level": round(level, 6), "threshold": threshold, "alarm": 1 if metric > threshold else 0}


def case_011(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    error_probability = clamp(0.08 + 0.18 * float(ctx["gradual"]) + 0.07 * float(ctx["seasonal"]))
    y_true = 1 if rng.random() < 0.42 else 0
    wrong = rng.random() < error_probability
    y_pred = 1 - y_true if wrong else y_true
    confidence = clamp(rng.gauss(0.86 - 0.22 * float(ctx["gradual"]), 0.08), 0.01, 0.99)
    return {"y_true": y_true, "y_pred": y_pred, "error": int(wrong), "error_probability": round(error_probability, 6), "confidence": round(confidence, 6)}


def case_012(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    strength = float(ctx["gradual"])
    f1 = rng.gauss(0, 1)
    f2 = rng.gauss(0, 1)
    old_score = f1 + 0.4 * f2
    new_score = -0.2 * f1 + 1.2 * f2
    score = (1 - strength) * old_score + strength * new_score
    y_true = 1 if score > 0 else 0
    y_pred = 1 if old_score > 0 else 0
    return {"feature_1": round(f1, 6), "feature_2": round(f2, 6), "label": y_true, "model_prediction": y_pred, "concept_score": round(score, 6)}


def case_013(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    topics = ["billing", "login", "delivery", "refund", "technical"]
    strength = max(float(ctx["gradual"]), float(ctx["seasonal"]))
    base = [0.30, 0.25, 0.20, 0.15, 0.10]
    drifted = [0.12, 0.16, 0.20, 0.27, 0.25]
    weights = [(1 - strength) * b + strength * d for b, d in zip(base, drifted)]
    topic = weighted_choice(rng, topics, weights)
    semantic_x = rng.gauss(topics.index(topic) * 0.6, 0.35)
    return {"topic": topic, "semantic_x": round(semantic_x, 6), "technical_topic_weight": round(weights[-1], 6)}


def case_014(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    strength = max(float(ctx["gradual"]), float(ctx["abrupt"]))
    imp_a = clamp(rng.gauss(0.45 - 0.25 * strength, 0.04))
    imp_b = clamp(rng.gauss(0.25 + 0.30 * strength, 0.04))
    imp_c = clamp(1.0 - imp_a - imp_b)
    top_feature = max([("feature_a", imp_a), ("feature_b", imp_b), ("feature_c", imp_c)], key=lambda item: item[1])[0]
    return {"importance_a": round(imp_a, 6), "importance_b": round(imp_b, 6), "importance_c": round(imp_c, 6), "top_feature": top_feature}


def case_015(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    noise = clamp(0.05 + 0.18 * float(ctx["gradual"]) + 0.10 * float(ctx["seasonal"]))
    true_label = weighted_choice(rng, ["safe", "review", "risk"], [0.55, 0.30, 0.15])
    observed_label = true_label if rng.random() > noise else weighted_choice(rng, ["safe", "review", "risk"], [0.25, 0.35, 0.40])
    annotator = weighted_choice(rng, ["ann_a", "ann_b", "ann_c"], [0.5, 0.3, 0.2 if not ctx["seasonal"] else 0.45])
    confidence = clamp(rng.gauss(0.88 - noise, 0.08))
    return {"true_label": true_label, "observed_label": observed_label, "annotator": annotator, "label_noise_probability": round(noise, 6), "annotation_confidence": round(confidence, 6)}


def case_016(rng: random.Random, index: int, ctx: dict[str, object]) -> dict[str, object]:
    strength = max(float(ctx["gradual"]), float(ctx["abrupt"]))
    layer = weighted_choice(rng, ["layer_1", "layer_2", "layer_3"], [0.35, 0.35, 0.30])
    group = weighted_choice(rng, ["node_a", "node_b", "node_c"], [0.45, 0.35, 0.20])
    shift = strength if layer == "layer_3" or group == "node_c" else 0.25 * strength
    activation = rng.gauss(0.4 + shift, 0.12)
    return {"layer": layer, "node_group": group, "activation": round(activation, 6), "representation_shift": round(shift, 6)}


GENERATORS = {
    "CASE-001": case_001,
    "CASE-002": case_002,
    "CASE-003": case_003,
    "CASE-004": case_004,
    "CASE-005": case_005,
    "CASE-006": case_006,
    "CASE-007": case_007,
    "CASE-008": case_008,
    "CASE-009": case_009,
    "CASE-010": case_010,
    "CASE-011": case_011,
    "CASE-012": case_012,
    "CASE-013": case_013,
    "CASE-014": case_014,
    "CASE-015": case_015,
    "CASE-016": case_016,
}


def case_dir_name(case_id: str) -> str:
    return f"{case_id}_{CASE_NAMES[case_id]}"


def write_case(case_id: str, output_root: Path, overwrite: bool = False) -> dict[str, object]:
    case_dir = output_root / case_dir_name(case_id)
    case_dir.mkdir(parents=True, exist_ok=True)
    data_path = case_dir / "data.csv.gz"
    metadata_path = case_dir / "metadata.json"
    if data_path.exists() and not overwrite:
        return {"case_id": case_id, "status": "skipped", "path": str(data_path), "rows": None}

    rng = random.Random(2026000 + int(case_id[-3:]))
    generator = GENERATORS[case_id]
    first_ctx = timestamp_context(0)
    sample = common_row(case_id, 0, first_ctx)
    sample.update(generator(rng, 0, first_ctx))
    fieldnames = list(sample.keys())

    rng = random.Random(2026000 + int(case_id[-3:]))
    with gzip.open(data_path, "wt", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for index in range(TOTAL_MINUTES):
            ctx = timestamp_context(index)
            row = common_row(case_id, index, ctx)
            row.update(generator(rng, index, ctx))
            writer.writerow(row)

    metadata = {
        "case_id": case_id,
        "case_name": CASE_NAMES[case_id],
        "data_file": "data.csv.gz",
        "row_count": TOTAL_MINUTES,
        "frequency": "1min",
        "start_inclusive": START.strftime("%Y-%m-%d %H:%M:%S"),
        "end_exclusive": END.strftime("%Y-%m-%d %H:%M:%S"),
        "drift_start": DRIFT_START.strftime("%Y-%m-%d %H:%M:%S"),
        "transition_minutes": TRANSITION_MINUTES,
        "window_minutes": WINDOW_MINUTES,
        "columns": fieldnames,
        "random_seed": 2026000 + int(case_id[-3:]),
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"case_id": case_id, "status": "created", "path": str(data_path), "rows": TOTAL_MINUTES}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 2026 minute-level drift test datasets.")
    parser.add_argument("--output-root", default=str(Path(__file__).resolve().parent), help="Output root directory.")
    parser.add_argument("--case", action="append", choices=sorted(CASE_NAMES), help="Generate only selected case. Can be repeated.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data.csv.gz files.")
    args = parser.parse_args()

    output_root = Path(args.output_root)
    cases = args.case or sorted(CASE_NAMES)
    summary = [write_case(case_id, output_root, overwrite=args.overwrite) for case_id in cases]
    summary_path = output_root / "generated_data_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    for item in summary:
        print(f"{item['case_id']}: {item['status']} {item['rows'] or ''} {item['path']}")


if __name__ == "__main__":
    main()
