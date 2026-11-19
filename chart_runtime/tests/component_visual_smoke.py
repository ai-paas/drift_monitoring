import argparse
import copy
import json
import math
import os
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

try:
    from PIL import Image, ImageStat
except Exception:  # pragma: no cover - optional visual heuristic
    Image = None
    ImageStat = None


ROOT = Path(__file__).resolve().parents[2]
CHART_BUILDER_DIR = ROOT / "chart_builder"
RUNTIME_DIR = ROOT / "chart_runtime"
DEFAULT_PAYLOADS_PATH = RUNTIME_DIR / "payloads" / "runtime_chart_payloads.json"
OUT_DIR = RUNTIME_DIR / "test_results" / "component_visual_smoke"
CAPTURE_DIR = OUT_DIR / "captures"


def file_uri(path):
    return Path(path).resolve().as_uri()


def safe_name(value):
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in str(value))[:150]


def signature_for(component):
    config = component.get("config") or {}
    style = (
        config.get("bar_style")
        or config.get("distribution_style")
        or config.get("timeline_style")
        or config.get("matrix_style")
        or config.get("projection_style")
        or ""
    )
    return component.get("componentType") or "unknown", style


def clone_json(value):
    return json.loads(json.dumps(value, ensure_ascii=False))


def rows_for_source(payload, source):
    rows = payload.get("data", {}).get(source, [])
    return rows if isinstance(rows, list) else []


def collect_numeric_ranges(data):
    ranges = {}
    for source, rows in data.items():
        if not isinstance(rows, list):
            continue
        fields = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            for key, value in row.items():
                if isinstance(value, bool):
                    continue
                try:
                    num = float(value)
                except (TypeError, ValueError):
                    continue
                if not math.isfinite(num):
                    continue
                fields.setdefault(key, []).append(num)
        ranges[source] = {
            key: (min(values), max(values))
            for key, values in fields.items()
            if values
        }
    return ranges


def shift_data(data):
    shifted = clone_json(data)
    ranges = collect_numeric_ranges(data)
    for source, rows in shifted.items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            for key, value in list(row.items()):
                if isinstance(value, bool):
                    continue
                try:
                    num = float(value)
                except (TypeError, ValueError):
                    continue
                if not math.isfinite(num):
                    continue
                low, high = ranges.get(source, {}).get(key, (num, num))
                span = high - low
                if span:
                    row[key] = low + (num - low) * 0.72 + span * 0.14
                else:
                    row[key] = num * 1.03
    return shifted


def sparse_data(data):
    sparse = clone_json(data)
    for source, rows in sparse.items():
        if isinstance(rows, list) and len(rows) > 4:
            keep = max(3, min(8, len(rows) // 3))
            sparse[source] = rows[:keep]
    return sparse


def dense_data(data):
    dense = clone_json(data)
    ranges = collect_numeric_ranges(data)
    coordinate_names = {"time", "x", "index", "start", "end", "window", "count", "step"}
    label_names = {"label", "category", "feature", "metric", "dimension", "quantile", "bin", "token", "state"}
    for source, rows in list(dense.items()):
        if not isinstance(rows, list) or not rows:
            continue
        target = min(48, max(len(rows) * 3, 18))
        copies = []
        numeric_ranges = ranges.get(source, {})
        for i in range(target):
            base = clone_json(rows[i % len(rows)])
            if not isinstance(base, dict):
                copies.append(base)
                continue
            cycle = i // len(rows)
            for key, value in list(base.items()):
                lower_key = str(key).lower()
                if lower_key in label_names and isinstance(value, str):
                    base[key] = f"{value}-{cycle + 1}" if cycle else value
                if lower_key in coordinate_names:
                    try:
                        num = float(value)
                    except (TypeError, ValueError):
                        continue
                    if math.isfinite(num):
                        low, high = numeric_ranges.get(key, (0, len(rows)))
                        span = max(1, high - low + 1)
                        base[key] = num + cycle * span
            copies.append(base)
        dense[source] = copies
    return dense


def has_bound_rows(payload, component):
    source = (component.get("dataBinding") or {}).get("source")
    if not source:
        return True
    rows = payload.get("data", {}).get(source)
    return isinstance(rows, list) and len(rows) > 0


def clamp(value, low, high):
    if low > high:
        low, high = high, low
    return max(low, min(high, value))


def clamp_config_to_data(payload):
    adjusted = clone_json(payload)
    for component in adjusted.get("components", []):
        binding = component.get("dataBinding") or {}
        source = binding.get("source")
        rows = rows_for_source(adjusted, source)
        if not rows:
            continue
        config = component.get("config") or {}
        x_field = config.get("x_field") or config.get("time_field") or binding.get("x_field") or binding.get("time_field")
        y_field = config.get("y_field") or config.get("value_field") or binding.get("y_field") or binding.get("value_field")
        x_values = []
        y_values = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            for field, bucket in ((x_field, x_values), (y_field, y_values)):
                try:
                    num = float(row.get(field))
                except (TypeError, ValueError):
                    continue
                if math.isfinite(num):
                    bucket.append(num)
        if not x_values:
            continue
        x_low, x_high = min(x_values), max(x_values)
        y_low, y_high = (min(y_values), max(y_values)) if y_values else (0, 1)
        x_span = x_high - x_low
        for marker in config.get("vertical_markers") or []:
            if isinstance(marker, dict) and marker.get("x") is not None:
                marker["x"] = clamp(float(marker["x"]), x_low, x_high)
        for marker in config.get("horizontal_markers") or []:
            if not isinstance(marker, dict):
                continue
            for key in ("x", "x0", "x1", "label_x"):
                if marker.get(key) is not None:
                    marker[key] = clamp(float(marker[key]), x_low, x_high)
            if marker.get("y") is not None:
                marker["y"] = clamp(float(marker["y"]), y_low, y_high)
        for marker in config.get("diagonal_markers") or []:
            if not isinstance(marker, dict):
                continue
            for key in ("x0", "x1"):
                if marker.get(key) is not None:
                    marker[key] = clamp(float(marker[key]), x_low, x_high)
            for key in ("y0", "y1"):
                if marker.get(key) is not None:
                    marker[key] = clamp(float(marker[key]), y_low, y_high)
        for point in config.get("point_highlights") or []:
            if not isinstance(point, dict):
                continue
            if point.get("x") is not None:
                point["x"] = clamp(float(point["x"]), x_low, x_high)
            if point.get("y") is not None:
                point["y"] = clamp(float(point["y"]), y_low, y_high)
        for annotation in config.get("annotations") or []:
            if not isinstance(annotation, dict):
                continue
            if annotation.get("x") is not None:
                annotation["x"] = clamp(float(annotation["x"]), x_low, x_low + x_span * 0.82)
            if annotation.get("y") is not None:
                annotation["y"] = clamp(float(annotation["y"]), y_low, y_high)
        if isinstance(config.get("x_ticks"), list):
            config["x_ticks"] = [tick for tick in config["x_ticks"] if isinstance(tick, (int, float)) and x_low <= tick <= x_high]
    return adjusted


def compact_config(payload):
    compact = clone_json(payload)
    for component in compact.get("components", []):
        config = component.setdefault("config", {})
        box = config.get("view_box")
        if isinstance(box, list) and len(box) >= 2:
            config["view_box"] = [max(260, int(float(box[0]) * 0.82)), max(160, int(float(box[1]) * 0.82))]
        elif config.get("view_box_width") or config.get("view_box_height"):
            config["view_box_width"] = max(260, int(float(config.get("view_box_width", 360)) * 0.82))
            config["view_box_height"] = max(160, int(float(config.get("view_box_height", 220)) * 0.82))

        margin = config.get("margin")
        if isinstance(margin, dict):
            for key in ("top", "right", "bottom", "left"):
                if key in margin:
                    margin[key] = max(8, int(float(margin[key]) * 0.85))
    compact["layout"]["gridTemplateRows"] = "300px"
    return compact


def component_case_payload(chart, component):
    payload = chart["payload"]
    area_name = component.get("area")
    source_areas = payload.get("layout", {}).get("areas", [])
    source_area = next((area for area in source_areas if area.get("area") == area_name), None) or {"area": "main"}

    area = clone_json(source_area)
    area.update({"area": "main", "x": 0, "y": 0, "w": 1, "h": 1, "role": "primary_visual"})
    area["stageInset"] = {"top": 52 if area.get("title") else 10, "right": 12, "bottom": 12, "left": 12}
    area["headerHeight"] = 44 if area.get("title") else 0

    same_area = [c for c in payload.get("components", []) if c.get("area") == area_name]
    if component.get("isOverlay"):
        components = same_area
    else:
        components = [component] + [c for c in same_area if c.get("isOverlay")]

    components = clone_json(components)
    for item in components:
        item["area"] = "main"

    return {
        "chartId": payload.get("chartId"),
        "title": payload.get("title"),
        "layout": {
            "layoutType": "component_visual_smoke",
            "columns": 1,
            "rows": 1,
            "gridTemplateColumns": "1fr",
            "gridTemplateRows": "340px",
            "gap": "0",
            "showAreaLabels": False,
            "areas": [area],
        },
        "components": components,
        "data": clone_json(payload.get("data", {})),
    }


def build_cases(charts):
    seen = {}
    for chart in charts:
        chart_id = chart["payload"].get("chartId", "")
        if not str(chart_id).startswith("CHART-"):
            continue
        for component in chart["payload"].get("components", []):
            if not has_bound_rows(chart["payload"], component):
                continue
            sig = signature_for(component)
            seen.setdefault(sig, (chart, component))

    cases = []
    for sig, (chart, component) in sorted(seen.items(), key=lambda item: item[0]):
        base = component_case_payload(chart, component)
        chart_id = chart["payload"].get("chartId")
        instance_id = component.get("componentInstanceId", "")
        label = f"{sig[0]}:{sig[1] or 'default'}"
        sparse_payload = {**clone_json(base), "data": sparse_data(base["data"])}
        sparse_payload = clamp_config_to_data(sparse_payload)
        dense_payload = {**clone_json(base), "data": dense_data(base["data"])}
        dense_payload = clamp_config_to_data(dense_payload)
        variants = [
            ("source", base),
            ("shifted-data", {**clone_json(base), "data": shift_data(base["data"])}),
            ("sparse-data", sparse_payload),
            ("dense-data", dense_payload),
            ("compact-config", compact_config(base)),
        ]
        for variant, payload in variants:
            cases.append(
                {
                    "id": safe_name(f"{chart_id}__{label}__{variant}"),
                    "chartId": chart_id,
                    "componentType": sig[0],
                    "style": sig[1],
                    "instanceId": instance_id,
                    "variant": variant,
                    "payload": payload,
                }
            )
    return cases


def write_harness():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    css_url = file_uri(RUNTIME_DIR / "chart_runtime.css")
    runtime_url = file_uri(RUNTIME_DIR / "chart_runtime.js")
    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="{css_url}">
  <style>
    body {{ margin: 0; background: #f4f6f8; font-family: Arial, sans-serif; }}
    #caseMeta {{ height: 30px; padding: 7px 12px 0; color: #334155; font-size: 12px; box-sizing: border-box; }}
    #componentChart {{ width: 760px; height: 390px; margin: 0; background: #fff; overflow: hidden; }}
    .chart-container {{ height: 100%; }}
  </style>
</head>
<body>
  <div id="caseMeta"></div>
  <div id="componentChart" class="component-chart"></div>
  <script src="{runtime_url}"></script>
  <script>
    window.renderSmokePayload = function(payload, label) {{
      document.getElementById("caseMeta").textContent = label || "";
      const target = document.getElementById("componentChart");
      window.ChartRuntime.renderChartPayload(target, payload);
    }};
  </script>
</body>
</html>"""
    path = OUT_DIR / "component_visual_smoke.html"
    path.write_text(html, encoding="utf-8")
    return path


def image_stats(path):
    if Image is None:
        return {"blank": False, "mean": None, "stddev": None}
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        stat = ImageStat.Stat(rgb)
        mean = sum(stat.mean) / 3
        stddev = sum(stat.stddev) / 3
        return {
            "blank": stddev < 2.0 or (mean > 252.0 and stddev < 8.0),
            "mean": round(mean, 2),
            "stddev": round(stddev, 2),
        }


CHECK_SCRIPT = """
() => {
  const target = document.querySelector("#componentChart");
  const targetBox = target.getBoundingClientRect();
  const html = target.innerHTML;
  const issues = [];
  if (!html.trim()) issues.push("empty markup");
  if (/\\b(NaN|undefined|Infinity)\\b/.test(html)) issues.push("invalid token in markup");
  if (!target.querySelector(".runtime-component")) issues.push("runtime component missing");
  if (!target.querySelector("svg, table, .summary-card, .summary-grid, .notes-card, .domain-visual")) {
    issues.push("visual surface missing");
  }

  const severeOverflow = [];
  for (const element of target.querySelectorAll(".runtime-component, svg, table, .summary-card, .notes-card")) {
    const box = element.getBoundingClientRect();
    if (box.width < 2 || box.height < 2) severeOverflow.push(`${element.tagName}: tiny bbox`);
    const tolerance = 36;
    if (
      box.right < targetBox.left - tolerance ||
      box.bottom < targetBox.top - tolerance ||
      box.left > targetBox.right + tolerance ||
      box.top > targetBox.bottom + tolerance
    ) {
      severeOverflow.push(`${element.tagName}: outside component chart`);
    }
  }
  if (severeOverflow.length) issues.push(...severeOverflow);

  for (const stage of target.querySelectorAll(".component-stage")) {
    const style = getComputedStyle(stage);
    const hasScrollableContent = stage.scrollWidth > stage.clientWidth + 2 || stage.scrollHeight > stage.clientHeight + 2;
    const allowsScroll = ["auto", "scroll"].includes(style.overflowX) || ["auto", "scroll"].includes(style.overflowY);
    if (hasScrollableContent && !allowsScroll) {
      issues.push("large content is not scrollable");
    }
  }

  for (const svg of target.querySelectorAll("svg")) {
    const viewBox = svg.getAttribute("viewBox");
    if (!viewBox) {
      issues.push("svg without viewBox");
      continue;
    }
    const parts = viewBox.split(/[ ,]+/).map(Number);
    if (parts.length < 4 || parts.some((n) => !Number.isFinite(n))) {
      issues.push("invalid svg viewBox");
      continue;
    }
    const [vx, vy, vw, vh] = parts;
    if (vw <= 0 || vh <= 0) issues.push("non-positive svg viewBox");
    let elementCount = 0;
    for (const node of svg.querySelectorAll("path, line, rect, circle, polygon, polyline, text")) {
      let box;
      try {
        box = node.getBBox();
      } catch (error) {
        continue;
      }
      if (!box || !Number.isFinite(box.x) || !Number.isFinite(box.y)) {
        issues.push(`${node.tagName}: invalid bbox`);
        continue;
      }
      if (box.width > 0 || box.height > 0) elementCount += 1;
      const padX = Math.max(52, vw * 0.22);
      const padY = Math.max(42, vh * 0.22);
      if (box.x < vx - padX || box.y < vy - padY || box.x + box.width > vx + vw + padX || box.y + box.height > vy + vh + padY) {
        issues.push(`${node.tagName}: bbox outside viewBox`);
        break;
      }
    }
    if (elementCount === 0) issues.push("svg has no visible geometry");
  }

  return {
    issues,
    componentCount: target.querySelectorAll(".runtime-component").length,
    svgCount: target.querySelectorAll("svg").length,
    text: target.innerText.slice(0, 240),
  };
}
"""


def run_cases(cases, harness_path, headless=True, limit=None):
    results = []
    browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    with sync_playwright() as p:
        launch_args = {"headless": headless}
        if os.path.exists(browser_path):
            launch_args["executable_path"] = browser_path
        browser = p.chromium.launch(**launch_args)
        page = browser.new_page(viewport={"width": 780, "height": 430}, device_scale_factor=1)
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.goto(file_uri(harness_path))

        for index, case in enumerate(cases[:limit] if limit else cases, start=1):
            console_errors.clear()
            label = f"{case['chartId']} | {case['componentType']} {case['style']} | {case['variant']}"
            status = "pass"
            issues = []
            capture_path = CAPTURE_DIR / f"{index:03d}_{case['id']}.png"
            try:
                page.evaluate(
                    "(args) => window.renderSmokePayload(args.payload, args.label)",
                    {"payload": case["payload"], "label": label},
                )
                page.wait_for_timeout(80)
                check = page.evaluate(CHECK_SCRIPT)
                issues.extend(check["issues"])
                if console_errors:
                    issues.extend(f"console error: {message}" for message in console_errors)
                page.locator("#componentChart").screenshot(path=str(capture_path))
                stats = image_stats(capture_path)
                if stats.get("blank"):
                    issues.append("blank or near-blank capture")
                if issues:
                    status = "fail"
                result = {**case, "payload": None, "status": status, "issues": issues, "capture": str(capture_path.relative_to(OUT_DIR)), "image": stats, "check": check}
            except Exception as exc:
                status = "fail"
                issues.append(f"exception: {exc}")
                result = {**case, "payload": None, "status": status, "issues": issues, "capture": None}
            results.append(result)
        browser.close()
    return results


def write_report(results):
    report_json = OUT_DIR / "component_visual_smoke_report.json"
    report_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    failures = [item for item in results if item["status"] != "pass"]
    cards = []
    for item in results:
        badge = "PASS" if item["status"] == "pass" else "FAIL"
        issues = "<br>".join(item.get("issues") or [])
        image = item.get("capture")
        image_html = f'<img src="{quote(image)}" alt="capture">' if image else "<div>No capture</div>"
        cards.append(
            f"""<section class="card {item['status']}">
  <div class="meta"><strong>{badge}</strong> {item['chartId']} / {item['componentType']} {item['style'] or ''} / {item['variant']}</div>
  {image_html}
  <p>{issues}</p>
</section>"""
        )
    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>Component visual smoke report</title>
  <style>
    body {{ margin: 0; padding: 18px; font-family: Arial, sans-serif; background: #eef2f6; color: #17202a; }}
    h1 {{ margin: 0 0 6px; font-size: 22px; }}
    .summary {{ margin-bottom: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 14px; }}
    .card {{ background: #fff; border: 1px solid #d6dee8; border-radius: 6px; padding: 10px; }}
    .card.fail {{ border-color: #c2410c; box-shadow: inset 4px 0 #c2410c; }}
    .meta {{ font-size: 12px; margin-bottom: 8px; line-height: 1.35; }}
    img {{ width: 100%; border: 1px solid #e1e7ef; background: #fff; }}
    p {{ min-height: 16px; margin: 8px 0 0; font-size: 12px; color: #7c2d12; }}
  </style>
</head>
<body>
  <h1>Component visual smoke report</h1>
  <div class="summary">Total {len(results)} cases / Pass {len(results) - len(failures)} / Fail {len(failures)}</div>
  <div class="grid">
    {''.join(cards)}
  </div>
</body>
</html>"""
    report_html = OUT_DIR / "component_visual_smoke_report.html"
    report_html.write_text(html, encoding="utf-8")
    return report_json, report_html, failures


def main():
    parser = argparse.ArgumentParser(description="Capture and validate chart runtime components with data/config variants.")
    parser.add_argument(
        "--payloads",
        default=str(DEFAULT_PAYLOADS_PATH),
        help="Path to a JSON array of runtime payloads. Defaults to payloads/runtime_chart_payloads.json.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases while developing the smoke test.")
    parser.add_argument("--headed", action="store_true", help="Run browser visibly.")
    args = parser.parse_args()

    payloads_path = Path(args.payloads)
    with payloads_path.open(encoding="utf-8") as f:
        payloads = json.load(f)
    charts = [{"name": item.get("chartId"), "payload": item} for item in payloads]

    cases = build_cases(charts)
    harness_path = write_harness()
    results = run_cases(cases, harness_path, headless=not args.headed, limit=args.limit)
    report_json, report_html, failures = write_report(results)
    print(f"cases={len(results)} pass={len(results) - len(failures)} fail={len(failures)}")
    print(f"report={report_html}")
    print(f"json={report_json}")
    if failures:
        print("failures:")
        for item in failures[:30]:
            print(f"- {item['chartId']} {item['componentType']} {item['style'] or ''} {item['variant']}: {'; '.join(item['issues'])}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
