from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

try:
    from PIL import Image, ImageStat
except Exception:  # pragma: no cover - optional image stats
    Image = None
    ImageStat = None


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = ROOT / "chart_runtime"
DEFAULT_PAYLOADS = RUNTIME_DIR / "payloads" / "runtime_chart_payloads.json"
DEFAULT_OUT = RUNTIME_DIR / "test_results" / "full_payload_chart_captures"


def file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def safe_name(value: object) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in str(value))[:120]


def image_stats(path: Path) -> dict[str, object]:
    if Image is None or ImageStat is None:
        return {"blank": False, "mean": None, "stddev": None}
    with Image.open(path) as image:
        stat = ImageStat.Stat(image.convert("L"))
        mean = round(float(stat.mean[0]), 2)
        stddev = round(float(stat.stddev[0]), 2)
        return {"blank": stddev < 1.0, "mean": mean, "stddev": stddev}


def write_harness(out_dir: Path) -> Path:
    harness = out_dir / "full_payload_capture_harness.html"
    harness.write_text(
        f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Full Payload Capture Harness</title>
  <link rel="stylesheet" href="{file_uri(RUNTIME_DIR / 'chart_runtime.css')}">
  <style>
    html, body {{ height: 100%; margin: 0; overflow: hidden; background: #f4f6f7; }}
    body {{ padding: 16px; }}
    #componentChart {{ width: 1400px; height: 900px; }}
  </style>
</head>
<body>
  <div id="componentChart" class="component-chart"></div>
  <script src="{file_uri(RUNTIME_DIR / 'chart_runtime.js')}"></script>
  <script>
    window.renderPayloadForCapture = function(payload) {{
      const target = document.getElementById("componentChart");
      target.innerHTML = "";
      window.ChartRuntime.renderChartPayload(target, payload);
    }};
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )
    return harness


def write_html_report(report_path: Path, results: list[dict[str, object]]) -> None:
    rows = []
    for result in results:
        status = "PASS" if result["status"] == "pass" else "FAIL"
        issues = "<br>".join(result["issues"]) if result["issues"] else ""
        rows.append(
            f"""<tr>
  <td>{result['index']:03d}</td>
  <td>{result['chartId']}</td>
  <td>{status}</td>
  <td>{issues}</td>
  <td><img src="{result['capture']}" loading="lazy"></td>
</tr>"""
        )
    report_path.write_text(
        f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>Full Payload Chart Captures</title>
  <style>
    body {{ margin: 0; padding: 18px; font-family: Segoe UI, Malgun Gothic, Arial, sans-serif; background: #f4f6f7; color: #17212b; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ border: 1px solid #d7dde4; padding: 8px; vertical-align: top; font-size: 13px; }}
    th {{ background: #e9edf1; text-align: left; }}
    img {{ width: 420px; max-width: 100%; border: 1px solid #d7dde4; }}
  </style>
</head>
<body>
  <h1>Full Payload Chart Captures</h1>
  <p>payloads={len(results)} pass={sum(1 for item in results if item['status'] == 'pass')} fail={sum(1 for item in results if item['status'] != 'pass')}</p>
  <table>
    <thead><tr><th>#</th><th>chartId</th><th>status</th><th>issues</th><th>capture</th></tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture full rendered chart images for every runtime payload.")
    parser.add_argument("--payloads", default=str(DEFAULT_PAYLOADS), help="Runtime payload JSON array path")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output directory")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of payloads")
    parser.add_argument("--headed", action="store_true", help="Run browser visibly")
    args = parser.parse_args()

    payloads_path = Path(args.payloads)
    out_dir = Path(args.out)
    captures_dir = out_dir / "captures"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    captures_dir.mkdir(parents=True, exist_ok=True)

    payloads = json.loads(payloads_path.read_text(encoding="utf-8"))
    if args.limit is not None:
        payloads = payloads[: args.limit]

    harness_path = write_harness(out_dir)
    results: list[dict[str, object]] = []
    browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    with sync_playwright() as p:
        launch_args = {"headless": not args.headed}
        if os.path.exists(browser_path):
            launch_args["executable_path"] = browser_path
        browser = p.chromium.launch(**launch_args)
        page = browser.new_page(viewport={"width": 1480, "height": 980}, device_scale_factor=1)
        page.goto(file_uri(harness_path))
        for index, payload in enumerate(payloads, start=1):
            chart_id = payload.get("chartId") or f"chart-{index:03d}"
            capture_name = f"{index:03d}_{safe_name(chart_id)}.png"
            capture_path = captures_dir / capture_name
            console_errors: list[str] = []

            def on_console(message):
                if message.type == "error":
                    console_errors.append(message.text)

            page.on("console", on_console)
            issues: list[str] = []
            try:
                page.evaluate("payload => window.renderPayloadForCapture(payload)", payload)
                page.wait_for_timeout(120)
                page.locator("#componentChart").screenshot(path=str(capture_path))
                stats = image_stats(capture_path)
                if stats.get("blank"):
                    issues.append("blank or near-blank capture")
                if console_errors:
                    issues.extend(f"console error: {message}" for message in console_errors)
                status = "pass" if not issues else "fail"
            except Exception as exc:
                stats = {"blank": True, "mean": None, "stddev": None}
                issues.append(str(exc))
                status = "fail"
            finally:
                page.remove_listener("console", on_console)

            results.append(
                {
                    "index": index,
                    "chartId": chart_id,
                    "status": status,
                    "issues": issues,
                    "capture": str(Path("captures") / capture_name),
                    "image": stats,
                }
            )
        browser.close()

    report_json = out_dir / "full_payload_chart_captures.json"
    report_html = out_dir / "full_payload_chart_captures.html"
    report_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_html_report(report_html, results)

    fail_count = sum(1 for result in results if result["status"] != "pass")
    print(f"payloads={len(results)} pass={len(results) - fail_count} fail={fail_count}")
    print(f"captures={captures_dir}")
    print(f"report={report_html}")
    print(f"json={report_json}")
    return 1 if fail_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
