from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT_SQL = ROOT / "db" / "load_data.sql"
PROJECT_ROOT = ROOT.parent
CHART_BUILDER_ROOT = PROJECT_ROOT / "chart_builder"
CHART_COMPONENT_DOC_DIR = CHART_BUILDER_ROOT / "docs" / "chart_components"
INTERPRETATION_DOC_DIR = CHART_BUILDER_ROOT / "docs" / "interpretation"
INTERPRETATION_COMPONENT_GUIDE_DIR = INTERPRETATION_DOC_DIR / "component_guides"
INTERPRETATION_CHART_GUIDE_DIR = INTERPRETATION_DOC_DIR / "chart_guides"
COMPONENT_DOC_EXCLUDE = {
    "README.md",
    "IMPLEMENTATION_GUIDE.md",
    "CHART_BUILDER_UI_DESIGN.md",
    "SOURCE_MATCHING_GUIDE.md",
}
CHART_ID_RE = re.compile(r"CHART-[A-Z0-9]+(?:-[A-Z0-9]+)+")
VARIANT_RE = re.compile(r"\b[A-Z][A-Z0-9_]*[A-Z0-9]\b")


def is_chart_interpretation_doc(path: Path) -> bool:
    name = path.name
    return (
        name.startswith("drift_chart_interpretation_")
        and name != "drift_chart_interpretation_guide.md"
    )


def sql(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    return "'" + text.replace("'", "''") + "'"


def json_sql(value: object) -> str:
    return sql(json.dumps(value, ensure_ascii=False)) + "::jsonb"


def inline_markdown_to_html(text: str) -> str:
    value = html.escape(text)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    return value


def markdown_body_to_html(markdown: str) -> str | None:
    if not markdown.strip():
        return None

    parts: list[str] = []
    paragraph: list[str] = []
    code_lines: list[str] = []
    in_code = False
    in_list = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            parts.append(f"<p>{inline_markdown_to_html(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            parts.append("</ul>")
            in_list = False

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                parts.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not stripped:
            flush_paragraph()
            close_list()
            continue
        if stripped == "---":
            flush_paragraph()
            close_list()
            continue
        heading = re.match(r"^(#{3,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = min(6, len(heading.group(1)) - 1)
            parts.append(f"<h{level}>{inline_markdown_to_html(heading.group(2))}</h{level}>")
            continue
        item = re.match(r"^-\s+(.+)$", stripped)
        if item:
            flush_paragraph()
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{inline_markdown_to_html(item.group(1))}</li>")
            continue
        paragraph.append(stripped)

    flush_paragraph()
    close_list()
    if in_code:
        parts.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    return "".join(parts)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_title(path: Path) -> str:
    if path.suffix.lower() == ".md":
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for line in text.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return path.stem


def source_path_for(path: Path) -> str:
    path = path.resolve()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.relative_to(PROJECT_ROOT).as_posix()


def source_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".md":
        return "markdown"
    if suffix == ".csv":
        return "csv"
    if suffix in {".py", ".js", ".css", ".cmd", ".sql"}:
        return "code"
    if suffix == ".html":
        return "html"
    if suffix == ".png":
        return "image"
    return "other"


def domain_for(path: Path) -> str:
    rel = source_path_for(path)
    if rel.startswith("chart_builder/docs/interpretation/chart_guides/"):
        return "chart"
    if rel.startswith("chart_builder/docs/interpretation/component_guides/"):
        return "component"
    if rel.startswith("chart_builder/docs/interpretation/"):
        return "interpretation"
    if rel.startswith("chart_builder/docs/chart_components/"):
        return "component"
    if rel.startswith("chart_builder/docs/") and "chart_component" in path.name:
        return "component"
    if rel.startswith("algorithm_variants/"):
        return "variant"
    if rel.startswith("chart_docs/"):
        return "chart"
    if "measurement" in path.name:
        return "measurement"
    if "parameter" in path.name:
        return "parameter"
    if path.name == "drift_methods_catalog.md":
        return "method"
    return "document"


def normalize_doc_path(path_text: str | None) -> str | None:
    if not path_text:
        return None
    value = path_text.strip()
    if value == "ks_test_algorithm_variants.md":
        return "algorithm_variants/ks_test_algorithm_variants.md"
    return value


def method_status(value: str | None) -> str:
    if value and value.strip() in {"확정", "active", "Active"}:
        return "active"
    return "draft"


def param_role(param: str) -> str:
    p = param.lower()
    if "threshold" in p or p in {"alpha", "delta"}:
        return "threshold"
    if "window" in p or "sample" in p or "warmup" in p:
        return "window"
    if "policy" in p or "correction" in p or "method" in p:
        return "policy"
    if "preprocess" in p or "embedding" in p or "projection" in p:
        return "preprocessing"
    return "input"


def chart_family(chart_id: str) -> str:
    parts = chart_id.split("-")
    return parts[1] if len(parts) > 1 else "UNKNOWN"


def method_code_from_name(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", name.upper()).strip("_")
    return value or "UNKNOWN_METHOD"


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_csv_path(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def markdown_sections(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    sections: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    body: list[str] = []

    def flush(end_line: int) -> None:
        nonlocal current, body
        if not current:
            return
        body_text = "\n".join(body).strip()
        heading = str(current["heading_text"])
        key_base = re.sub(r"[^A-Za-z0-9가-힣_-]+", "_", heading).strip("_")[:140]
        if not key_base:
            key_base = f"section_{current['display_order']}"
        current["section_key"] = f"{current['display_order']:04d}_{key_base}"
        current["body_markdown"] = body_text
        current["body_plain_text"] = re.sub(r"!\[[^\]]*\]|\]\([^)]+\)|[*_`#>|()\[\]]", "", body_text)
        current["body_html"] = markdown_body_to_html(body_text)
        current["line_end"] = end_line
        current["content_hash"] = hashlib.sha256((heading + "\n" + body_text).encode("utf-8")).hexdigest()
        sections.append(current)
        current = None
        body = []

    order = 0
    for index, line in enumerate(lines, start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            flush(index - 1)
            order += 1
            current = {
                "heading_text": match.group(2).strip(),
                "heading_level": len(match.group(1)),
                "line_start": index,
                "display_order": order,
                "section_type": infer_section_type(match.group(2), path),
            }
        elif current:
            body.append(line)
    flush(len(lines))
    return sections


def section_body_by_heading(path: Path) -> dict[str, str]:
    sections = markdown_sections(path)
    return {
        str(section["heading_text"]).strip(): str(section.get("body_markdown") or "").strip()
        for section in sections
    }


def component_code_from_doc(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    match = re.search(r"Component key:\s*`([^`]+)`", text)
    if match:
        return match.group(1).strip()
    return path.stem.replace("-", "_")


def component_parameter_schema(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in markdown.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {"파라미터", "---"}:
            continue
        rows.append({"name": cells[0].strip("`"), "description": cells[1]})
    return rows


def component_input_contract(markdown: str) -> dict[str, object] | None:
    match = re.search(r"```json\s*(.*?)```", markdown, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {"raw_json_example": match.group(1).strip()}


def component_docs() -> list[Path]:
    if not CHART_COMPONENT_DOC_DIR.exists():
        return []
    return [
        path
        for path in sorted(CHART_COMPONENT_DOC_DIR.glob("*.md"))
        if path.name not in COMPONENT_DOC_EXCLUDE
    ]


def interpretation_docs() -> list[Path]:
    if not INTERPRETATION_DOC_DIR.exists():
        return []
    paths = [
        INTERPRETATION_DOC_DIR / "general_guide.md",
        INTERPRETATION_DOC_DIR / "chart_level_guide.md",
    ]
    if INTERPRETATION_COMPONENT_GUIDE_DIR.exists():
        paths.extend(sorted(INTERPRETATION_COMPONENT_GUIDE_DIR.glob("*.md")))
    if INTERPRETATION_CHART_GUIDE_DIR.exists():
        paths.extend(sorted(INTERPRETATION_CHART_GUIDE_DIR.glob("CHART-*.md")))
    return [path for path in paths if path.exists() and path.is_file()]


def visual_interpretation_rules(component_code: str) -> list[dict[str, object]]:
    common_severity = {
        "normal": "현재 그래프에서 기준 초과 또는 급격한 이상 신호가 뚜렷하지 않다.",
        "watch": "기준 미초과라도 추세, 근접도, 최근 이력 때문에 관찰이 필요하다.",
        "candidate": "시각적 기준을 넘거나 주요 변화 패턴이 명확해 drift 후보로 본다.",
    }
    rules_by_component: dict[str, list[dict[str, object]]] = {
        "threshold_line": [
            {
                "rule_code": "LATEST_VALUE_VS_THRESHOLD",
                "signal_type": "latest_value_vs_threshold",
                "condition": {"latest": "compare threshold", "direction": "config.threshold_type"},
                "template": "현재 값 {latest}를 기준선 {threshold}와 비교한다. {direction} 기준에서 선을 넘으면 drift 후보, 넘지 않으면 기준 미초과로 해석한다.",
                "caution": "기준선은 component가 보여주는 판정 보조선이며, method의 통계적 가정과 sample size를 함께 확인한다.",
            },
            {
                "rule_code": "BELOW_THRESHOLD_BUT_NEAR_OR_RECENT_TOUCH",
                "signal_type": "threshold_proximity_with_recent_history",
                "condition": {"latest": "below threshold", "distance_to_threshold": "small or recent_max >= threshold", "direction": "upper"},
                "template": "현재 값은 기준선 {threshold} 아래인 {latest}로 기준을 넘지 않았지만, 기준선에 가깝거나 최근 구간에서 닿은 이력이 있으면 위험 완화 또는 관찰 필요 신호로 해석한다.",
                "caution": "현재 시점의 미초과만으로 위험이 사라졌다고 단정하지 않는다.",
            },
        ],
        "trend_line": [
            {
                "rule_code": "RECENT_TREND_DIRECTION",
                "signal_type": "recent_slope_and_turning_point",
                "condition": {"recent_slope": "positive|negative|flat", "turning_point": "optional"},
                "template": "최근 선의 기울기와 변곡점을 읽어 값이 악화 방향으로 이동하는지, 안정화되는지, 회복 중인지 해석한다.",
                "caution": "짧은 구간의 기울기는 노이즈일 수 있으므로 window 길이와 반복 여부를 함께 본다.",
            },
            {
                "rule_code": "RISING_TOWARD_LIMIT",
                "signal_type": "slope_to_threshold",
                "condition": {"latest": "below threshold", "recent_slope": "> 0", "distance_to_threshold": "small"},
                "template": "현재 값은 아직 기준선 아래지만 최근 추세가 기준선 방향으로 상승하고 있으면 기준 미초과 상태의 위험 신호로 해석한다.",
                "caution": "기준선 접근은 경보가 아니라 사전 관찰 신호다.",
            },
        ],
        "distance_metric_view": [
            {
                "rule_code": "DISTANCE_LEVEL_AND_HISTORY",
                "signal_type": "distance_latest_threshold_history",
                "condition": {"latest_distance": "compare threshold", "recent_max": "compare threshold", "direction": "higher_is_more_drift"},
                "template": "현재 distance {latest}와 기준선 {threshold}, 최근 최대값 {recent_max}를 함께 본다. 현재는 기준 미초과라도 최근 기준 접촉 이력이 있으면 완화 중인 위험 신호로 해석한다.",
                "caution": "거리 값은 차이의 크기이지 원인을 직접 설명하지 않는다.",
            },
        ],
        "control_chart": [
            {
                "rule_code": "CONTROL_LIMIT_PATTERN",
                "signal_type": "control_limit_breach_or_run_pattern",
                "condition": {"latest": "compare control limits", "run_pattern": "optional consecutive side"},
                "template": "관리한계선과 중심선 대비 위치를 보고 초과, 한쪽 편중, 연속 상승/하락 패턴을 구분한다.",
                "caution": "관리한계 초과는 조사 시작 신호이며 원인 확정은 아니다.",
            },
        ],
        "bar_chart": [
            {
                "rule_code": "DOMINANT_BAR_OR_DELTA",
                "signal_type": "largest_bar_or_absolute_delta",
                "condition": {"max_item": "exists", "value_or_delta": "largest absolute value"},
                "template": "{category} 항목의 값 또는 변화량 {value}가 가장 크면 현재 그래프에서 가장 먼저 확인할 변화 후보로 해석한다.",
                "caution": "막대가 크다는 사실만으로 원인을 확정하지 말고 denominator와 segment 정의를 확인한다.",
            },
        ],
        "proportion_view": [
            {
                "rule_code": "PROPORTION_SHIFT",
                "signal_type": "reference_current_proportion_shift",
                "condition": {"reference": "compare current", "delta": "signed"},
                "template": "기준 대비 현재 비율의 증가/감소 방향과 크기를 읽어 category mix 변화 후보를 판단한다.",
                "caution": "비율 변화는 표본 수 변화와 함께 해석해야 한다.",
            },
        ],
        "reference_current_comparison": [
            {
                "rule_code": "REFERENCE_CURRENT_GAP",
                "signal_type": "paired_reference_current_gap",
                "condition": {"reference": "compare current", "gap": "signed or absolute"},
                "template": "reference와 current의 간격이 큰 항목을 찾아 현재 구간이 기준 구간과 어느 방향으로 달라졌는지 해석한다.",
                "caution": "비교 기준 기간이 바뀌면 같은 gap도 다른 의미가 될 수 있다.",
            },
        ],
        "distribution_view": [
            {
                "rule_code": "DISTRIBUTION_OVERLAP_AND_TAIL",
                "signal_type": "distribution_overlap_tail_shift",
                "condition": {"overlap": "low|high", "tail_gap": "optional", "center_shift": "optional"},
                "template": "분포의 중심 이동, 꼬리 차이, 겹침 감소를 함께 읽어 분포 drift 후보를 해석한다.",
                "caution": "분포 모양 차이는 성능 저하나 원인을 직접 의미하지 않는다.",
            },
        ],
        "histogram_view": [
            {
                "rule_code": "BIN_MASS_SHIFT",
                "signal_type": "histogram_bin_mass_shift",
                "condition": {"bin_delta": "largest positive or negative"},
                "template": "질량이 증가하거나 감소한 bin을 확인해 어느 값 구간에서 분포 변화가 집중되는지 해석한다.",
                "caution": "bin 폭과 경계 설정에 따라 강조 구간이 달라질 수 있다.",
            },
        ],
        "distribution_summary_plot": [
            {
                "rule_code": "SUMMARY_STAT_SHIFT",
                "signal_type": "distribution_summary_stat_shift",
                "condition": {"mean_or_median_shift": "exists", "spread_change": "exists"},
                "template": "중심값과 산포 요약을 함께 보고 평균 이동인지, 분산 확대인지, 둘 다인지 구분한다.",
                "caution": "요약 통계는 다봉성이나 꼬리 변화를 숨길 수 있다.",
            },
        ],
        "quantile_view": [
            {
                "rule_code": "QUANTILE_GAP_PATTERN",
                "signal_type": "quantile_gap_by_rank",
                "condition": {"quantile_gap": "varies by quantile"},
                "template": "분위수별 간격을 보고 변화가 전체 범위에 고르게 있는지, 상위/하위 tail에 집중되는지 해석한다.",
                "caution": "분위수 해석은 표본 수가 작으면 불안정하다.",
            },
        ],
        "state_timeline": [
            {
                "rule_code": "STATE_TRANSITION_SEQUENCE",
                "signal_type": "state_transition_sequence",
                "condition": {"sequence": "normal -> warning -> drift/recover/reset"},
                "template": "상태 전이가 normal, warning, drift 또는 recovery 순서로 이어지는지 보고 일시 신호인지 지속 위험인지 해석한다.",
                "caution": "상태명은 detector 정책에 의존하므로 detector별 의미를 함께 확인한다.",
            },
        ],
        "event_marker": [
            {
                "rule_code": "EVENT_AROUND_VALUE_CHANGE",
                "signal_type": "event_marker_before_after_change",
                "condition": {"event_time": "exists", "before_after_change": "compare"},
                "template": "event marker 전후의 값 변화를 비교해 alarm, warning, replacement 같은 사건이 그래프 변화와 맞물리는지 해석한다.",
                "caution": "event가 원인이라는 뜻이 아니라 해석해야 할 시간 경계다.",
            },
        ],
        "window_view": [
            {
                "rule_code": "WINDOW_CONTEXT_SHIFT",
                "signal_type": "reference_current_window_context",
                "condition": {"reference_window": "exists", "current_window": "exists"},
                "template": "reference/current window의 위치와 길이를 보고 현재 비교가 안정적인지, 최근 변화에 민감한지 해석한다.",
                "caution": "window 정의가 달라지면 이전 결과와 직접 비교하지 않는다.",
            },
        ],
        "decision_card": [
            {
                "rule_code": "SUMMARY_DECISION_WITH_SUPPORTING_VALUES",
                "signal_type": "summary_metric_decision",
                "condition": {"decision": "exists", "supporting_metrics": "exists"},
                "template": "요약 카드의 판정 문구와 보조 수치를 함께 읽어 그래프 전체의 핵심 결론을 짧게 정리한다.",
                "caution": "요약 카드는 근거를 압축한 것이므로 상세 component와 함께 검증한다.",
            },
        ],
        "detector_statistic_view": [
            {
                "rule_code": "DETECTOR_STATISTIC_LEVEL",
                "signal_type": "detector_statistic_threshold_or_bound",
                "condition": {"statistic": "compare bound", "direction": "higher_or_lower_is_drift"},
                "template": "detector statistic이 bound나 threshold에 접근하거나 초과하는지 보고 drift 후보 강도를 해석한다.",
                "caution": "검정량 크기는 detector 내부 scale에 종속되므로 다른 method와 직접 비교하지 않는다.",
            },
        ],
        "p_value_view": [
            {
                "rule_code": "P_VALUE_ALPHA_DECISION",
                "signal_type": "p_value_vs_alpha",
                "condition": {"p_value": "compare alpha"},
                "template": "p-value가 alpha보다 낮으면 통계적으로 유의한 차이 후보로, 높으면 현재 검정 조건에서 유의하지 않음으로 해석한다.",
                "caution": "p-value는 drift 크기가 아니며 effect size와 표본 수를 함께 봐야 한다.",
            },
        ],
        "performance_metric_view": [
            {
                "rule_code": "PERFORMANCE_DROP_OR_RECOVERY",
                "signal_type": "performance_metric_trend",
                "condition": {"metric_direction": "higher_or_lower_is_better", "recent_change": "signed"},
                "template": "성능 지표가 악화 방향으로 움직이는지, 이벤트 이후 회복되는지 그래프 흐름으로 해석한다.",
                "caution": "label 지연이나 평가 기준 변경이 있으면 성능 drift로 단정하지 않는다.",
            },
        ],
        "projection_scatter": [
            {
                "rule_code": "CLUSTER_SEPARATION_OR_OUTLIER",
                "signal_type": "projection_cluster_separation_outlier",
                "condition": {"group_separation": "visible", "outlier_group": "optional"},
                "template": "투영 공간에서 current 점이 reference 영역과 분리되거나 outlier로 모이면 representation drift 후보로 해석한다.",
                "caution": "투영 결과는 차원축소 방식에 영향을 받으므로 원공간 검증이 필요하다.",
            },
        ],
        "heatmap": [
            {
                "rule_code": "CELL_INTENSITY_HOTSPOT",
                "signal_type": "heatmap_hotspot_or_pattern",
                "condition": {"hotspot": "max intensity", "pattern": "block or diagonal"},
                "template": "색이 강한 cell이나 block 패턴을 찾아 변화가 특정 feature 조합, class, segment에 집중되는지 해석한다.",
                "caution": "색상 scale과 normalization 기준을 확인한다.",
            },
        ],
        "matrix_view": [
            {
                "rule_code": "MATRIX_ACTIVE_PATTERN",
                "signal_type": "matrix_cell_pattern",
                "condition": {"active_cells": "exists", "row_col_group": "optional"},
                "template": "활성 cell의 행/열 패턴을 보고 어떤 method, 방향, class 조합에서 신호가 반복되는지 해석한다.",
                "caution": "matrix는 관계를 압축하므로 개별 cell의 원자료를 확인한다.",
            },
        ],
        "ranking_view": [
            {
                "rule_code": "RANK_SHIFT_TOP_ITEMS",
                "signal_type": "ranking_top_item_shift",
                "condition": {"rank_delta": "largest", "top_k": "exists"},
                "template": "상위 rank에 새로 진입하거나 순위가 크게 바뀐 항목을 주요 변화 후보로 해석한다.",
                "caution": "rank 변화는 원점수 차이가 작아도 크게 보일 수 있다.",
            },
        ],
        "contribution_view": [
            {
                "rule_code": "TOP_CONTRIBUTOR",
                "signal_type": "largest_contribution",
                "condition": {"top_contributor": "exists", "contribution_direction": "optional"},
                "template": "기여도가 가장 큰 항목을 drift score 또는 alarm의 주요 기여 후보로 해석한다.",
                "caution": "기여도는 원인 확정이 아니라 조사 우선순위다.",
            },
        ],
        "raw_signal_trend": [
            {
                "rule_code": "RAW_SIGNAL_CHANGE",
                "signal_type": "raw_signal_trend_change",
                "condition": {"recent_change": "signed", "noise_level": "optional"},
                "template": "원 신호의 변화 방향과 변동성을 보고 detector 입력 자체가 흔들리는지 해석한다.",
                "caution": "원 신호는 전처리와 smoothing 여부에 민감하다.",
            },
        ],
        "cumulative_curve": [
            {
                "rule_code": "CUMULATIVE_GAP",
                "signal_type": "cumulative_curve_gap",
                "condition": {"curve_gap": "max or signed", "crossing": "optional"},
                "template": "누적 곡선 간 최대 간격과 방향을 보고 어느 구간에서 분포 차이가 누적되는지 해석한다.",
                "caution": "곡선 간격의 방향은 component의 대립가설 설정과 함께 읽는다.",
            },
        ],
        "uncertainty_band": [
            {
                "rule_code": "VALUE_OUTSIDE_UNCERTAINTY_BAND",
                "signal_type": "value_vs_uncertainty_band",
                "condition": {"value": "inside_or_outside_band", "band_width": "optional"},
                "template": "값이 uncertainty band 안에 있는지 밖으로 벗어났는지 보고 통계적 불확실성 대비 변화가 큰지 해석한다.",
                "caution": "band 폭은 신뢰수준과 표본 수에 따라 달라진다.",
            },
        ],
        "annotation_callout": [
            {
                "rule_code": "CALLOUT_HIGHLIGHTED_EVIDENCE",
                "signal_type": "annotation_highlight",
                "condition": {"anchor": "exists", "severity": "optional"},
                "template": "callout이 가리키는 위치와 문구를 우선 확인해 그래프에서 해석자가 놓치기 쉬운 근거를 읽는다.",
                "caution": "callout은 보조 해석이며 데이터 전체 흐름과 충돌하지 않아야 한다.",
            },
        ],
        "domain_specific_visual": [
            {
                "rule_code": "DOMAIN_CONTEXT_NOTE",
                "signal_type": "domain_specific_context",
                "condition": {"domain_text": "exists"},
                "template": "도메인별 시각 요소와 설명을 보고 수치 신호가 운영 맥락에서 어떤 의미인지 보완한다.",
                "caution": "도메인 설명은 통계적 증거를 대체하지 않는다.",
            },
        ],
        "comparison_table": [
            {
                "rule_code": "TABLE_DELTA_COMPARISON",
                "signal_type": "table_row_column_delta",
                "condition": {"baseline": "compare candidate", "delta": "exists"},
                "template": "행/열별 delta를 비교해 어떤 모델, 구간, metric에서 차이가 가장 큰지 해석한다.",
                "caution": "서로 다른 scale의 metric을 크기만으로 비교하지 않는다.",
            },
        ],
        "model_diagnostic_curve": [
            {
                "rule_code": "DIAGNOSTIC_CURVE_SHIFT",
                "signal_type": "diagnostic_curve_shape_change",
                "condition": {"curve_shift": "exists", "auc_or_gap": "optional"},
                "template": "진단 곡선의 위치나 면적 변화로 모델 구분력 또는 calibration 변화 후보를 해석한다.",
                "caution": "진단 곡선은 label 품질과 평가 표본 구성에 민감하다.",
            },
        ],
        "adaptive_model_structure_view": [
            {
                "rule_code": "ADAPTIVE_STRUCTURE_EVENT",
                "signal_type": "model_structure_change_event",
                "condition": {"structure_metric": "trend", "event": "replacement|promotion|reset"},
                "template": "모델 구조 metric과 교체/승격 이벤트를 함께 보고 drift 대응 후 구조가 안정화되는지 해석한다.",
                "caution": "구조 변화는 적응 사건이지 성능 개선 보장은 아니다.",
            },
        ],
        "small_multiples": [
            {
                "rule_code": "REPEATED_PATTERN_ACROSS_PANELS",
                "signal_type": "small_multiple_repeated_pattern",
                "condition": {"panels": "multiple", "shared_pattern": "exists"},
                "template": "여러 panel에서 같은 방향의 변화가 반복되는지 보고 segment 또는 feature 전반의 일관된 drift 신호를 해석한다.",
                "caution": "panel별 scale이 다르면 시각적 크기를 직접 비교하지 않는다.",
            },
        ],
        "feature_projection_view": [
            {
                "rule_code": "FEATURE_PROJECTION_SHIFT",
                "signal_type": "feature_projection_shift",
                "condition": {"projection_axis": "exists", "group_shift": "visible"},
                "template": "feature projection 축에서 current 분포가 reference와 분리되는지 보고 feature representation 변화 후보를 해석한다.",
                "caution": "projection 축의 의미와 전처리 기준을 확인한다.",
            },
        ],
        "circular_histogram": [
            {
                "rule_code": "CIRCULAR_MASS_SHIFT",
                "signal_type": "circular_histogram_mass_shift",
                "condition": {"angle_bin_delta": "largest"},
                "template": "원형 bin에서 질량이 몰리거나 이동한 각도 구간을 확인해 주기성 또는 방향성 분포 변화를 해석한다.",
                "caution": "원형 데이터는 0도/360도 경계를 이어서 해석해야 한다.",
            },
        ],
        "event_raster": [
            {
                "rule_code": "EVENT_DENSITY_BURST",
                "signal_type": "event_raster_density_burst",
                "condition": {"event_density": "increases", "time_cluster": "exists"},
                "template": "특정 시간대에 event가 밀집되는지 보고 운영 이벤트 또는 anomaly burst 후보를 해석한다.",
                "caution": "이벤트 밀집은 수집 주기 변경으로도 생길 수 있다.",
            },
        ],
        "forest_plot": [
            {
                "rule_code": "INTERVAL_EXCLUDES_NULL",
                "signal_type": "forest_interval_vs_null",
                "condition": {"confidence_interval": "compare null line"},
                "template": "신뢰구간이 null 기준선을 포함하는지 여부와 효과 크기 방향을 함께 보고 유의한 변화 후보를 해석한다.",
                "caution": "구간이 넓으면 추정 불확실성이 크다.",
            },
        ],
        "node_link_diagram": [
            {
                "rule_code": "GRAPH_STRUCTURE_CHANGE",
                "signal_type": "node_link_structure_change",
                "condition": {"node_or_edge_change": "exists"},
                "template": "node와 edge 구조의 추가, 제거, 강조 패턴을 보고 관계 구조 변화 후보를 해석한다.",
                "caution": "그래프 배치는 시각화 알고리즘에 영향을 받을 수 있다.",
            },
        ],
    }
    rules = rules_by_component.get(component_code)
    if rules:
        return [
            {**rule, "severity": common_severity}
            for rule in rules
        ]
    return [
        {
            "rule_code": "GENERIC_VISUAL_EVIDENCE",
            "signal_type": "generic_component_visual_evidence",
            "condition": {"visible_pattern": "compare config and dataBinding"},
            "severity": common_severity,
            "template": "component의 주요 값, 강조 요소, 기준 요소를 함께 읽어 그래프에서 두드러진 변화 후보를 해석한다.",
            "caution": "component 일반 규칙만으로 원인을 확정하지 않는다.",
        }
    ]


def infer_section_type(heading: str, path: Path) -> str:
    h = heading.lower()
    rel = source_path_for(path)
    if rel.endswith("chart_builder/docs/interpretation/general_guide.md"):
        return "general_interpretation_guide"
    if rel.endswith("chart_builder/docs/interpretation/chart_level_guide.md"):
        return "chart_level_interpretation_guide"
    if rel.startswith("chart_builder/docs/interpretation/component_guides/"):
        return "component_interpretation_guide"
    if rel.startswith("chart_builder/docs/interpretation/chart_guides/"):
        return "chart_specific_interpretation_guide"
    if "chart-" in h:
        return "chart_interpretation"
    if "차트 목적" in heading:
        return "chart_purpose"
    if "차트 구성" in heading:
        return "chart_components"
    if "해석 순서" in heading:
        return "interpretation_steps"
    if "판단 기준" in heading:
        return "drift_decision_criteria"
    if "금지" in heading:
        return "forbidden_interpretation"
    if "추가 확인" in heading:
        return "additional_checks"
    if "적합한 사용" in heading:
        return "suitable_use_cases"
    if "변종" in heading:
        return "variant_detail"
    if "selectionrule" in h or "선택" in heading:
        return "selection_rule"
    if "parameter" in path.name or "파라미터" in heading:
        return "parameter_explanation"
    if "measurement" in path.name or "측정" in heading:
        return "measurement_interpretation"
    return "general"


def parse_chart_guide() -> tuple[dict[str, str], list[dict[str, str]]]:
    path = ROOT / "chart_docs" / "drift_method_variant_chart_guide.md"
    chart_defs: dict[str, str] = {}
    variant_links: list[dict[str, str]] = []
    section = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("## 1."):
            section = "links"
            continue
        if line.startswith("## 2."):
            section = "catalog"
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"---", "drift 메소드", "chart id"}:
            continue
        if section == "links":
            if len(cells) < 3:
                continue
            method_variant, chart_cell, desc = cells[:3]
            if "/" not in method_variant:
                continue
            method, variant = [part.strip() for part in method_variant.rsplit("/", 1)]
            for order, chart_id in enumerate(CHART_ID_RE.findall(chart_cell), start=1):
                variant_links.append({
                    "method": method,
                    "variant": variant,
                    "chart_id": chart_id,
                    "description": desc,
                    "order": str(order),
                })
        elif section == "catalog":
            if len(cells) < 2:
                continue
            chart_id, desc = cells[:2]
            if CHART_ID_RE.fullmatch(chart_id):
                chart_defs[chart_id] = desc
    return chart_defs, variant_links


def compact_text(text: str | None, limit: int = 900) -> str:
    value = re.sub(r"\s+", " ", text or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def build_chart_interpretation_template(chart_id: str, section_map: dict[str, list[dict[str, object]]]) -> str:
    def first_body(section_type: str) -> str:
        sections = section_map.get(section_type) or []
        if not sections:
            return ""
        return compact_text(str(sections[0].get("body_plain_text") or sections[0].get("body_markdown") or ""), 700)

    purpose = first_body("chart_purpose")
    components = first_body("chart_components")
    steps = first_body("interpretation_steps")
    decision = first_body("drift_decision_criteria")
    forbidden = first_body("forbidden_interpretation")
    additional = first_body("additional_checks")
    current_summary = ""
    for section in section_map.get("general", []):
        heading = str(section.get("heading_text") or "")
        if "현재 상황" in heading or "해석" in heading or "패널" in heading:
            current_summary = compact_text(str(section.get("body_plain_text") or section.get("body_markdown") or ""), 700)
            break

    parts = [
        f"{chart_id}의 전체 해석은 component별 그래프 판독을 chart 목적에 맞게 종합한다.",
    ]
    if purpose:
        parts.append(f"차트 목적: {purpose}")
    if components:
        parts.append(f"component 판독: {components}")
    if steps:
        parts.append(f"해석 순서: {steps}")
    if decision:
        parts.append(f"종합 판단 기준: {decision}")
    if current_summary:
        parts.append(f"현재 상황 문장화 기준: {current_summary}")
    if additional:
        parts.append(f"추가 확인: {additional}")
    if forbidden:
        parts.append(f"금지 해석: {forbidden}")
    parts.append(
        "LLM은 각 component의 visual interpretation rule 결과를 위 순서대로 결합해, "
        "기준 초과 여부뿐 아니라 기준선 근접, 최근 접촉 이력, 회복/악화 추세, 주요 기여 항목을 함께 반영한 현재 상황 해석 문장을 작성한다."
    )
    return "\n\n".join(parts)


def chart_interpretation_guides() -> list[dict[str, object]]:
    guide_sections = {
        "chart_purpose",
        "chart_components",
        "interpretation_steps",
        "drift_decision_criteria",
        "suitable_use_cases",
        "additional_checks",
        "forbidden_interpretation",
        "general",
    }
    guides: list[dict[str, object]] = []
    for doc in sorted((ROOT / "chart_docs").glob("drift_chart_interpretation_*.md")):
        if not is_chart_interpretation_doc(doc):
            continue
        rel = source_path_for(doc)
        current_chart_id: str | None = None
        section_map: dict[str, list[dict[str, object]]] = {}

        def flush_current() -> None:
            nonlocal section_map, current_chart_id
            if not current_chart_id or not section_map:
                section_map = {}
                return
            flow = []
            step = 1
            for section_type in [
                "chart_purpose",
                "chart_components",
                "interpretation_steps",
                "drift_decision_criteria",
                "suitable_use_cases",
                "additional_checks",
                "forbidden_interpretation",
            ]:
                for section in section_map.get(section_type, []):
                    body = str(section.get("body_plain_text") or section.get("body_markdown") or "")
                    flow.append({
                        "step": step,
                        "section_type": section_type,
                        "heading": section.get("heading_text"),
                        "read": compact_text(body),
                    })
                    step += 1
            synthesis_rule = {
                section_type: [
                    {
                        "heading": section.get("heading_text"),
                        "body": compact_text(str(section.get("body_plain_text") or section.get("body_markdown") or ""), 1400),
                    }
                    for section in sections
                ]
                for section_type, sections in section_map.items()
                if section_type in guide_sections
            }
            guides.append({
                "chart_id": current_chart_id,
                "guide_code": "DEFAULT_SYNTHESIS",
                "flow": flow,
                "synthesis_rule": synthesis_rule,
                "template": build_chart_interpretation_template(current_chart_id, section_map),
                "caution": (
                    "component별 그래프 판독을 단순 나열하지 말고 chart 목적과 drift 판단 기준에 맞게 종합한다. "
                    "기준 미초과는 안전 확정이 아니며, 최근 기준 접촉 이력과 추세를 함께 확인한다."
                ),
                "source_path": rel,
            })
            section_map = {}

        for section in markdown_sections(doc):
            heading = str(section.get("heading_text") or "")
            heading_chart_ids = CHART_ID_RE.findall(heading)
            if heading_chart_ids and int(section.get("heading_level") or 0) <= 2:
                flush_current()
                current_chart_id = heading_chart_ids[0]
            if not current_chart_id:
                continue
            section_type = str(section.get("section_type") or "general")
            if section_type in guide_sections:
                section_map.setdefault(section_type, []).append(section)
        flush_current()
    return guides


def builder_chart_interpretation_guides() -> list[dict[str, object]]:
    if not INTERPRETATION_CHART_GUIDE_DIR.exists():
        return []
    guides: list[dict[str, object]] = []
    for doc in sorted(INTERPRETATION_CHART_GUIDE_DIR.glob("CHART-*.md")):
        chart_id = doc.stem
        rel = source_path_for(doc)
        sections = markdown_sections(doc)
        flow = []
        synthesis_rule: dict[str, list[dict[str, str]]] = {}
        for step, section in enumerate(sections, start=1):
            section_type = str(section.get("section_type") or "chart_specific_interpretation_guide")
            body = str(section.get("body_plain_text") or section.get("body_markdown") or "")
            flow.append({
                "step": step,
                "section_type": section_type,
                "heading": section.get("heading_text"),
                "read": compact_text(body),
            })
            synthesis_rule.setdefault(section_type, []).append({
                "heading": str(section.get("heading_text") or ""),
                "body": compact_text(body, 1400),
            })
        if not flow:
            continue
        guides.append({
            "chart_id": chart_id,
            "guide_code": "BUILDER_CHART_GUIDE",
            "flow": flow,
            "synthesis_rule": synthesis_rule,
            "template": (
                f"{chart_id}의 chart-specific guide를 우선 참조해 component evidence를 종합한다. "
                "현재 payload의 실제 값과 visual encoding을 기준으로 설명하고, guide의 예시 값을 그대로 복사하지 않는다."
            ),
            "caution": (
                "chart-specific guide는 해석 순서와 판단 경계를 제공한다. "
                "payload에 없는 원인, 영향, 결론은 추가로 추정하지 않는다."
            ),
            "source_path": rel,
        })
    return guides


def emit_source_documents(sql_lines: list[str]) -> None:
    patterns = [
        "*.csv",
        "*.md",
        "algorithm_variants/*.md",
        "chart_docs/*.md",
        "charts/chart_*.html",
        "charts/chart_*.css",
        "charts/chart_*.js",
        "charts/output/CHART-*.png",
    ]
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(ROOT.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            rel = source_path_for(path)
            sql_lines.append(
                "insert into source_document "
                "(source_path, source_type, domain, title, checksum_sha256, file_size_bytes, last_seen_at, is_active) values "
                f"({sql(rel)}, {sql(source_type(path))}, {sql(domain_for(path))}, {sql(file_title(path))}, "
                f"{sql(sha256(path))}, {path.stat().st_size}, now(), true) "
                "on conflict (source_path) do update set "
                "source_type=excluded.source_type, domain=excluded.domain, title=excluded.title, "
                "checksum_sha256=excluded.checksum_sha256, file_size_bytes=excluded.file_size_bytes, "
                "last_seen_at=now(), is_active=true;"
            )
    external_paths: list[Path] = []
    if CHART_COMPONENT_DOC_DIR.exists():
        external_paths.extend(sorted(CHART_COMPONENT_DOC_DIR.glob("*.md")))
    external_paths.extend(interpretation_docs())
    for rel_text in [
        "docs/chart_component_to_chart.csv",
        "docs/chart_component_raw_to_chart.csv",
    ]:
        path = CHART_BUILDER_ROOT / rel_text
        if path.exists():
            external_paths.append(path)
    for path in external_paths:
        if not path.is_file() or path in seen:
            continue
        seen.add(path)
        rel = source_path_for(path)
        sql_lines.append(
            "insert into source_document "
            "(source_path, source_type, domain, title, checksum_sha256, file_size_bytes, last_seen_at, is_active) values "
            f"({sql(rel)}, {sql(source_type(path))}, {sql(domain_for(path))}, {sql(file_title(path))}, "
            f"{sql(sha256(path))}, {path.stat().st_size}, now(), true) "
            "on conflict (source_path) do update set "
            "source_type=excluded.source_type, domain=excluded.domain, title=excluded.title, "
            "checksum_sha256=excluded.checksum_sha256, file_size_bytes=excluded.file_size_bytes, "
            "last_seen_at=now(), is_active=true;"
        )


def source_id_subquery(path_text: str | None) -> str:
    path = normalize_doc_path(path_text)
    if not path:
        return "null"
    return f"(select source_document_id from source_document where source_path={sql(path)})"


def main() -> None:
    sql_lines: list[str] = [
        "begin;",
        "insert into source_import_batch (import_status, git_commit_sha, source_root, summary_json) values "
        f"('running', {sql(git_commit())}, {sql(str(ROOT))}, '{{}}'::jsonb) returning import_batch_id;",
    ]
    emit_source_documents(sql_lines)

    method_rows = read_csv("drift_method_variant_links.csv")
    methods: dict[str, dict[str, str]] = {}
    variants: dict[str, dict[str, str]] = {}
    for row in method_rows:
        methods[row["method_id"]] = row
        variants[row["variant_id"]] = row

    for row in methods.values():
        sql_lines.append(
            "insert into drift_method (method_code, display_name, method_category, status, updated_at) values "
            f"({sql(row['method_id'])}, {sql(row['method_name'])}, {sql(row['method_category'])}, "
            f"{sql(method_status(row.get('method_status')))}, now()) "
            "on conflict (method_code) do update set "
            "display_name=excluded.display_name, method_category=excluded.method_category, "
            "status=excluded.status, updated_at=now();"
        )

    for variant_code, row in variants.items():
        sql_lines.append(
            "insert into algorithm_variant "
            "(variant_code, display_name, variant_family, status, source_document_id, updated_at) values "
            f"({sql(variant_code)}, {sql(variant_code)}, {sql(method_code_from_name(row['method_name']))}, "
            f"'active', {source_id_subquery(row.get('variant_doc'))}, now()) "
            "on conflict (variant_code) do update set "
            "display_name=excluded.display_name, variant_family=excluded.variant_family, "
            "source_document_id=excluded.source_document_id, updated_at=now();"
        )

    for row in method_rows:
        sql_lines.append(
            "insert into method_variant "
            "(drift_method_id, algorithm_variant_id, is_default_variant, selection_priority, source_document_id) values "
            f"((select drift_method_id from drift_method where method_code={sql(row['method_id'])}), "
            f"(select algorithm_variant_id from algorithm_variant where variant_code={sql(row['variant_id'])}), "
            f"{'true' if row.get('variant_order') == '1' else 'false'}, {int(row.get('variant_order') or 0)}, "
            f"{source_id_subquery(row.get('variant_doc'))}) "
            "on conflict (drift_method_id, algorithm_variant_id) do update set "
            "is_default_variant=excluded.is_default_variant, selection_priority=excluded.selection_priority, "
            "source_document_id=excluded.source_document_id;"
        )

    for row in read_csv("drift_measurements_catalog.csv"):
        sql_lines.append(
            "insert into measurement "
            "(measurement_id, measurement_code, canonical_name, measurement_category, value_type, interpretation_text) values "
            f"({sql(row['measurement_id'])}, {sql(row['canonical_measurement'])}, {sql(row['canonical_measurement'])}, "
            f"{sql(row.get('measurement_type'))}, {sql(row.get('measurement_type'))}, {sql(row.get('description_ko'))}) "
            "on conflict (measurement_id) do update set "
            "measurement_code=excluded.measurement_code, canonical_name=excluded.canonical_name, "
            "measurement_category=excluded.measurement_category, value_type=excluded.value_type, "
            "interpretation_text=excluded.interpretation_text;"
        )

    for row in read_csv("drift_method_variant_measurement_links.csv"):
        is_primary = row.get("output_order") == "1"
        sql_lines.append(
            "insert into variant_measurement "
            "(method_variant_id, measurement_pk, raw_measurement_name, output_order, is_primary, required_for_report, "
            "interpretation_override_text, source_document_id) values "
            f"((select mv.method_variant_id from method_variant mv "
            f"join drift_method dm on dm.drift_method_id=mv.drift_method_id "
            f"join algorithm_variant av on av.algorithm_variant_id=mv.algorithm_variant_id "
            f"where dm.method_code={sql(row['method_id'])} and av.variant_code={sql(row['variant_id'])}), "
            f"(select measurement_pk from measurement where measurement_id={sql(row['measurement_id'])}), "
            f"{sql(row['raw_measurement'])}, {int(row.get('output_order') or 0)}, {sql(is_primary)}, {sql(is_primary)}, "
            f"{sql(row.get('measurement_description_ko'))}, {source_id_subquery(row.get('variant_doc'))}) "
            "on conflict (method_variant_id, measurement_pk, raw_measurement_name) do update set "
            "output_order=excluded.output_order, is_primary=excluded.is_primary, "
            "required_for_report=excluded.required_for_report, interpretation_override_text=excluded.interpretation_override_text, "
            "source_document_id=excluded.source_document_id;"
        )

    seen_params: set[str] = set()
    param_rows = read_csv("drift_method_variant_parameters.csv")
    for row in param_rows:
        for param in [p.strip() for p in row["parameters"].split(";") if p.strip()]:
            if param in seen_params:
                continue
            seen_params.add(param)
            sql_lines.append(
                "insert into parameter (parameter_code, display_name, value_type) values "
                f"({sql(param)}, {sql(param)}, 'text') "
                "on conflict (parameter_code) do update set display_name=excluded.display_name;"
            )

    for row in param_rows:
        if "/" not in row["drift_measurement_method"]:
            continue
        method, variant = [part.strip() for part in row["drift_measurement_method"].rsplit("/", 1)]
        for param in [p.strip() for p in row["parameters"].split(";") if p.strip()]:
            sql_lines.append(
                "insert into variant_parameter "
                "(method_variant_id, parameter_id, is_required, parameter_role, source_document_id) values "
                f"((select mv.method_variant_id from method_variant mv "
                f"join drift_method dm on dm.drift_method_id=mv.drift_method_id "
                f"join algorithm_variant av on av.algorithm_variant_id=mv.algorithm_variant_id "
                f"where dm.display_name={sql(method)} and av.variant_code={sql(variant)}), "
                f"(select parameter_id from parameter where parameter_code={sql(param)}), "
                f"true, {sql(param_role(param))}, "
                f"{source_id_subquery('drift_method_variant_parameters.csv')}) "
                "on conflict (method_variant_id, parameter_id) do update set "
                "is_required=excluded.is_required, parameter_role=excluded.parameter_role, source_document_id=excluded.source_document_id;"
            )

    chart_defs, variant_chart_rows = parse_chart_guide()
    all_variant_codes = set(variants)
    all_variant_codes.update(row["variant"] for row in variant_chart_rows)
    for row in variant_chart_rows:
        variant_code = row["variant"]
        if variant_code in variants:
            continue
        method_code = method_code_from_name(row["method"])
        sql_lines.append(
            "insert into drift_method (method_code, display_name, method_category, status, updated_at) values "
            f"({sql(method_code)}, {sql(row['method'])}, 'OperationalFallback', 'active', now()) "
            "on conflict (method_code) do update set "
            "display_name=excluded.display_name, method_category=excluded.method_category, status=excluded.status, updated_at=now();"
        )
        sql_lines.append(
            "insert into algorithm_variant "
            "(variant_code, display_name, variant_family, status, source_document_id, updated_at) values "
            f"({sql(variant_code)}, {sql(variant_code)}, {sql(method_code)}, 'active', "
            f"{source_id_subquery('chart_docs/drift_method_variant_chart_guide.md')}, now()) "
            "on conflict (variant_code) do update set "
            "display_name=excluded.display_name, variant_family=excluded.variant_family, "
            "source_document_id=excluded.source_document_id, updated_at=now();"
        )
        sql_lines.append(
            "insert into method_variant "
            "(drift_method_id, algorithm_variant_id, is_default_variant, selection_priority, source_document_id) values "
            f"((select drift_method_id from drift_method where method_code={sql(method_code)}), "
            f"(select algorithm_variant_id from algorithm_variant where variant_code={sql(variant_code)}), "
            f"true, 999, {source_id_subquery('chart_docs/drift_method_variant_chart_guide.md')}) "
            "on conflict (drift_method_id, algorithm_variant_id) do update set "
            "is_default_variant=excluded.is_default_variant, selection_priority=excluded.selection_priority, "
            "source_document_id=excluded.source_document_id;"
        )

    for chart_id, desc in chart_defs.items():
        sql_lines.append(
            "insert into chart_definition "
            "(chart_code, chart_family, display_title, purpose_text, component_summary_text, status, source_document_id) values "
            f"({sql(chart_id)}, {sql(chart_family(chart_id))}, {sql(chart_id)}, {sql(desc)}, {sql(desc)}, "
            f"'active', {source_id_subquery('chart_docs/drift_method_variant_chart_guide.md')}) "
            "on conflict (chart_code) do update set "
            "chart_family=excluded.chart_family, display_title=excluded.display_title, purpose_text=excluded.purpose_text, "
            "component_summary_text=excluded.component_summary_text, source_document_id=excluded.source_document_id;"
        )

    for row in variant_chart_rows:
        sql_lines.append(
            "insert into variant_chart "
            "(method_variant_id, chart_definition_id, is_primary_chart, selection_reason_text, display_order, source_document_id) values "
            f"((select mv.method_variant_id from method_variant mv "
            f"join drift_method dm on dm.drift_method_id=mv.drift_method_id "
            f"join algorithm_variant av on av.algorithm_variant_id=mv.algorithm_variant_id "
            f"where dm.display_name={sql(row['method'])} and av.variant_code={sql(row['variant'])}), "
            f"(select chart_definition_id from chart_definition where chart_code={sql(row['chart_id'])}), "
            f"{'true' if row['order'] == '1' else 'false'}, {sql(row['description'])}, {int(row['order'])}, "
            f"{source_id_subquery('chart_docs/drift_method_variant_chart_guide.md')}) "
            "on conflict (method_variant_id, chart_definition_id) do update set "
            "is_primary_chart=excluded.is_primary_chart, selection_reason_text=excluded.selection_reason_text, "
            "display_order=excluded.display_order, source_document_id=excluded.source_document_id;"
        )

    for chart_id in sorted(chart_defs):
        base = chart_id.lower().replace("-", "_")
        for asset_type, rel, generated in [
            ("html", f"charts/{base}.html", False),
            ("css", f"charts/{base}.css", False),
            ("js", f"charts/{base}.js", False),
            ("png", f"charts/output/{chart_id}.png", True),
            ("description_html", f"charts/descriptions/{base}_desc.html", True),
        ]:
            path = ROOT / rel
            if not path.exists():
                continue
            sql_lines.append(
                "insert into chart_asset "
                "(chart_definition_id, asset_type, asset_path, checksum_sha256, is_generated) values "
                f"((select chart_definition_id from chart_definition where chart_code={sql(chart_id)}), "
                f"{sql(asset_type)}, {sql(rel)}, {sql(sha256(path))}, {sql(generated)}) "
                "on conflict (asset_path) do update set "
                "chart_definition_id=excluded.chart_definition_id, asset_type=excluded.asset_type, "
                "checksum_sha256=excluded.checksum_sha256, is_generated=excluded.is_generated;"
            )

    component_doc_paths = component_docs()
    component_codes: set[str] = set()
    for doc in component_doc_paths:
        rel = source_path_for(doc)
        sections_by_heading = section_body_by_heading(doc)
        component_code = component_code_from_doc(doc)
        component_codes.add(component_code)
        purpose_text = sections_by_heading.get("목적")
        shows_text = sections_by_heading.get("주요 기능")
        interpretation_text = sections_by_heading.get("파라미터 변경 시 화면 변화")
        caution_text = sections_by_heading.get("렌더링 규칙")
        input_contract = component_input_contract(sections_by_heading.get("입력 데이터 계약", ""))
        config_schema = {
            "parameters": component_parameter_schema(sections_by_heading.get("주요 파라미터", ""))
        }
        sql_lines.append(
            "insert into chart_component "
            "(component_code, display_name, purpose_text, shows_text, interpretation_text, caution_text, "
            "input_contract_json, config_schema_json, renderer_status, source_document_id, updated_at) values "
            f"({sql(component_code)}, {sql(file_title(doc))}, {sql(purpose_text)}, {sql(shows_text)}, "
            f"{sql(interpretation_text)}, {sql(caution_text)}, {json_sql(input_contract or {})}, "
            f"{json_sql(config_schema)}, 'active', {source_id_subquery(rel)}, now()) "
            "on conflict (component_code) do update set "
            "display_name=excluded.display_name, purpose_text=excluded.purpose_text, shows_text=excluded.shows_text, "
            "interpretation_text=excluded.interpretation_text, caution_text=excluded.caution_text, "
            "input_contract_json=excluded.input_contract_json, config_schema_json=excluded.config_schema_json, "
            "renderer_status=excluded.renderer_status, source_document_id=excluded.source_document_id, updated_at=now();"
        )
        for rule in visual_interpretation_rules(component_code):
            sql_lines.append(
                "insert into chart_component_interpretation_rule "
                "(chart_component_id, rule_code, signal_type, condition_json, severity_mapping_json, "
                "interpretation_template_text, caution_text, source_document_id, updated_at) values "
                f"((select chart_component_id from chart_component where component_code={sql(component_code)}), "
                f"{sql(rule['rule_code'])}, {sql(rule.get('signal_type'))}, {json_sql(rule.get('condition') or {})}, "
                f"{json_sql(rule.get('severity') or {})}, {sql(rule['template'])}, {sql(rule.get('caution'))}, "
                f"{source_id_subquery(rel)}, now()) "
                "on conflict (chart_component_id, rule_code) do update set "
                "signal_type=excluded.signal_type, condition_json=excluded.condition_json, "
                "severity_mapping_json=excluded.severity_mapping_json, "
                "interpretation_template_text=excluded.interpretation_template_text, "
                "caution_text=excluded.caution_text, source_document_id=excluded.source_document_id, updated_at=now();"
            )

    component_to_chart_path = CHART_BUILDER_ROOT / "docs" / "chart_component_to_chart.csv"
    if component_to_chart_path.exists():
        rel = source_path_for(component_to_chart_path)
        usage_order_by_chart: dict[str, int] = {}
        for row in read_csv_path(component_to_chart_path):
            chart_id = row.get("chart", "").strip()
            component_code = row.get("component", "").strip()
            if not chart_id or not component_code:
                continue
            usage_order_by_chart[chart_id] = usage_order_by_chart.get(chart_id, 0) + 1
            display_order = usage_order_by_chart[chart_id]
            sql_lines.append(
                "insert into chart_component_usage "
                "(chart_definition_id, chart_component_id, usage_role, display_order, usage_reason_text, source_document_id) values "
                f"((select chart_definition_id from chart_definition where chart_code={sql(chart_id)}), "
                f"(select chart_component_id from chart_component where component_code={sql(component_code)}), "
                f"'declared_component', {display_order}, null, {source_id_subquery(rel)}) "
                "on conflict (chart_definition_id, chart_component_id, usage_role) do update set "
                "display_order=excluded.display_order, usage_reason_text=excluded.usage_reason_text, "
                "source_document_id=excluded.source_document_id;"
            )

    raw_component_to_chart_path = CHART_BUILDER_ROOT / "docs" / "chart_component_raw_to_chart.csv"
    if raw_component_to_chart_path.exists():
        rel = source_path_for(raw_component_to_chart_path)
        for row in read_csv_path(raw_component_to_chart_path):
            chart_id = row.get("chart", "").strip()
            raw_component = row.get("component", "").strip()
            if not chart_id or not raw_component:
                continue
            normalized_component = raw_component if raw_component in component_codes else None
            sql_lines.append(
                "insert into chart_component_raw_mapping "
                "(chart_definition_id, raw_component_text, normalized_component_id, source_document_id) values "
                f"((select chart_definition_id from chart_definition where chart_code={sql(chart_id)}), "
                f"{sql(raw_component)}, "
                f"{'(select chart_component_id from chart_component where component_code=' + sql(normalized_component) + ')' if normalized_component else 'null'}, "
                f"{source_id_subquery(rel)}) "
                "on conflict (chart_definition_id, raw_component_text) do update set "
                "normalized_component_id=excluded.normalized_component_id, source_document_id=excluded.source_document_id;"
            )

    chart_synthesis_guides = [
        *chart_interpretation_guides(),
        *builder_chart_interpretation_guides(),
    ]
    for guide in chart_synthesis_guides:
        sql_lines.append(
            "insert into chart_interpretation_guide "
            "(chart_definition_id, guide_code, interpretation_flow_json, synthesis_rule_json, "
            "interpretation_template_text, caution_text, source_document_id, updated_at) values "
            f"((select chart_definition_id from chart_definition where chart_code={sql(guide['chart_id'])}), "
            f"{sql(guide['guide_code'])}, {json_sql(guide['flow'])}, {json_sql(guide['synthesis_rule'])}, "
            f"{sql(guide['template'])}, {sql(guide['caution'])}, {source_id_subquery(str(guide['source_path']))}, now()) "
            "on conflict (chart_definition_id, guide_code) do update set "
            "interpretation_flow_json=excluded.interpretation_flow_json, "
            "synthesis_rule_json=excluded.synthesis_rule_json, "
            "interpretation_template_text=excluded.interpretation_template_text, "
            "caution_text=excluded.caution_text, source_document_id=excluded.source_document_id, updated_at=now();"
        )

    docs_for_sections = [
        ROOT / "drift_methods_catalog.md",
        ROOT / "drift_measurements_interpretation_guide.md",
        ROOT / "drift_measurement_method_selection_guide.md",
        ROOT / "drift_method_parameter_guide.md",
        *sorted((ROOT / "algorithm_variants").glob("*.md")),
        *sorted((ROOT / "chart_docs").glob("*.md")),
        *component_doc_paths,
        *interpretation_docs(),
    ]
    section_doc_paths = [source_path_for(doc) for doc in docs_for_sections if doc.exists()]
    sql_lines.append(
        "delete from section_entity_link sel using document_section ds, source_document sd "
        "where sel.document_section_id=ds.document_section_id "
        "and ds.source_document_id=sd.source_document_id "
        f"and sd.source_path in ({', '.join(sql(path) for path in section_doc_paths)});"
    )
    for doc in docs_for_sections:
        if not doc.exists():
            continue
        rel = source_path_for(doc)
        sections = markdown_sections(doc)
        inherit_chart_context = (
            is_chart_interpretation_doc(doc)
            or source_path_for(doc).startswith("chart_builder/docs/interpretation/chart_guides/")
        )
        active_chart_ids: set[str] = set()
        rel_default_chart_ids = set(CHART_ID_RE.findall(rel))
        for section in sections:
            sql_lines.append(
                "insert into document_section "
                "(source_document_id, section_key, section_type, heading_text, heading_level, body_markdown, body_plain_text, "
                "body_html, line_start, line_end, content_hash, display_order, is_active) values "
                f"({source_id_subquery(rel)}, {sql(section['section_key'])}, {sql(section['section_type'])}, "
                f"{sql(section['heading_text'])}, {section['heading_level']}, {sql(section.get('body_markdown'))}, "
                f"{sql(section.get('body_plain_text'))}, {sql(section.get('body_html'))}, {section['line_start']}, "
                f"{section['line_end']}, {sql(section['content_hash'])}, {section['display_order']}, true) "
                "on conflict (source_document_id, section_key) do update set "
                "section_type=excluded.section_type, heading_text=excluded.heading_text, heading_level=excluded.heading_level, "
                "body_markdown=excluded.body_markdown, body_plain_text=excluded.body_plain_text, body_html=excluded.body_html, "
                "line_start=excluded.line_start, line_end=excluded.line_end, content_hash=excluded.content_hash, "
                "display_order=excluded.display_order, is_active=true;"
            )
            heading_body = f"{section['heading_text']}\n{section.get('body_markdown') or ''}"
            explicit_chart_ids = set(CHART_ID_RE.findall(heading_body))
            if inherit_chart_context:
                heading_chart_ids = set(CHART_ID_RE.findall(str(section["heading_text"])))
                if heading_chart_ids and int(section["heading_level"]) <= 2:
                    active_chart_ids = heading_chart_ids
                chart_link_ids = explicit_chart_ids | active_chart_ids | rel_default_chart_ids
            elif rel.startswith("chart_docs/"):
                chart_link_ids = set()
            else:
                chart_link_ids = explicit_chart_ids
            for chart_id in sorted(chart_link_ids):
                sql_lines.append(
                    "insert into section_entity_link (document_section_id, entity_type, entity_id, link_role, confidence) values "
                    f"((select ds.document_section_id from document_section ds join source_document sd on sd.source_document_id=ds.source_document_id "
                    f"where sd.source_path={sql(rel)} and ds.section_key={sql(section['section_key'])}), "
                    f"'chart', (select chart_definition_id from chart_definition where chart_code={sql(chart_id)}), "
                    "'describes', 1.0) "
                    "on conflict (document_section_id, entity_type, entity_id, link_role) do update set confidence=excluded.confidence;"
                )
            for variant_code in sorted(set(VARIANT_RE.findall(heading_body))):
                if variant_code in all_variant_codes:
                    sql_lines.append(
                        "insert into section_entity_link (document_section_id, entity_type, entity_id, link_role, confidence) values "
                        f"((select ds.document_section_id from document_section ds join source_document sd on sd.source_document_id=ds.source_document_id "
                        f"where sd.source_path={sql(rel)} and ds.section_key={sql(section['section_key'])}), "
                        f"'variant', (select algorithm_variant_id from algorithm_variant where variant_code={sql(variant_code)}), "
                        "'describes', 0.9) "
                        "on conflict (document_section_id, entity_type, entity_id, link_role) do update set confidence=excluded.confidence;"
                    )
            if rel.startswith("chart_builder/docs/chart_components/"):
                component_code = component_code_from_doc(doc)
                sql_lines.append(
                    "insert into section_entity_link (document_section_id, entity_type, entity_id, link_role, confidence) values "
                    f"((select ds.document_section_id from document_section ds join source_document sd on sd.source_document_id=ds.source_document_id "
                    f"where sd.source_path={sql(rel)} and ds.section_key={sql(section['section_key'])}), "
                    f"'component', (select chart_component_id from chart_component where component_code={sql(component_code)}), "
                    "'describes', 1.0) "
                    "on conflict (document_section_id, entity_type, entity_id, link_role) do update set confidence=excluded.confidence;"
                )
            if rel.startswith("chart_builder/docs/interpretation/component_guides/"):
                component_code = doc.stem.replace("-", "_")
                if component_code in component_codes:
                    sql_lines.append(
                        "insert into section_entity_link (document_section_id, entity_type, entity_id, link_role, confidence) values "
                        f"((select ds.document_section_id from document_section ds join source_document sd on sd.source_document_id=ds.source_document_id "
                        f"where sd.source_path={sql(rel)} and ds.section_key={sql(section['section_key'])}), "
                        f"'component', (select chart_component_id from chart_component where component_code={sql(component_code)}), "
                        "'interpretation_guide', 1.0) "
                        "on conflict (document_section_id, entity_type, entity_id, link_role) do update set confidence=excluded.confidence;"
                    )

    summary = {
        "methods": len(methods),
        "variants": len(variants),
        "measurements": len(read_csv("drift_measurements_catalog.csv")),
        "variant_measurements": len(read_csv("drift_method_variant_measurement_links.csv")),
        "parameters": len(seen_params),
        "charts": len(chart_defs),
        "variant_charts": len(variant_chart_rows),
        "chart_components": len(component_codes),
        "chart_component_usages": len(read_csv_path(component_to_chart_path)) if component_to_chart_path.exists() else 0,
        "chart_component_raw_mappings": len(read_csv_path(raw_component_to_chart_path)) if raw_component_to_chart_path.exists() else 0,
        "chart_component_interpretation_rules": sum(len(visual_interpretation_rules(code)) for code in component_codes),
        "chart_interpretation_guides": len(chart_synthesis_guides),
    }
    sql_lines.append(
        "update source_import_batch set finished_at=now(), import_status='success', "
        f"summary_json={json_sql(summary)} where import_batch_id=(select max(import_batch_id) from source_import_batch);"
    )
    sql_lines.append("commit;")
    OUT_SQL.write_text("\n".join(sql_lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {OUT_SQL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
