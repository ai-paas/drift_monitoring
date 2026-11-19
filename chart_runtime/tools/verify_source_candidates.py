from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "chart_runtime.js",
    "chart_runtime.css",
    "src/runtime/utils.js",
    "src/runtime/format.js",
    "src/runtime/svg.js",
    "src/runtime/color.js",
    "src/renderers/overlay.js",
    "src/renderers/table.js",
    "src/renderers/card.js",
    "src/renderers/matrix.js",
    "src/renderers/scatter.js",
    "src/renderers/timeline.js",
    "src/renderers/distribution.js",
    "src/renderers/line.js",
    "src/renderers/bar.js",
    "src/styles/runtime-core.css",
    "src/styles/chart-visuals.css",
    "src/styles/popup.css",
    "src/styles/viewer-shell.css",
]


def run_node_check(path: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["node", "--check", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    return result.returncode == 0, output


def main() -> int:
    errors: list[str] = []
    checked_js = 0

    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing required file: {relative}")

    js_files = [ROOT / "chart_runtime.js"] + sorted((ROOT / "src").rglob("*.js"))
    for path in js_files:
        ok, output = run_node_check(path)
        checked_js += 1
        if not ok:
            errors.append(f"node --check failed: {path.relative_to(ROOT)}\n{output}")

    css_files = sorted((ROOT / "src" / "styles").glob("*.css"))
    if len(css_files) < 4:
        errors.append("expected at least 4 split CSS source candidates under src/styles")

    for css_file in css_files:
        if css_file.stat().st_size == 0:
            errors.append(f"empty CSS source candidate: {css_file.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"sourceCandidates=fail jsChecked={checked_js} cssChecked={len(css_files)} errors={len(errors)}")
        return 1

    print(f"sourceCandidates=pass jsChecked={checked_js} cssChecked={len(css_files)} errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
