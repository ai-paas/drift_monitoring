from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

VIEWER_SELECTORS = [
    ".site",
    ".sidebar",
    "#searchInput",
    ".chart-list",
    ".chart-button",
    ".workspace",
    ".workspace-head",
    ".recreated-pane",
    ".issues",
    ".original-popup",
]

RUNTIME_CORE_FORBIDDEN = [
    ".site",
    ".sidebar",
    "#searchInput",
    ".chart-list",
    ".chart-button",
    ".workspace",
    ".original-popup",
]

POPUP_FORBIDDEN = [
    ".site",
    ".sidebar",
    ".workspace",
    ".chart-list",
    ".chart-button",
    ".original-popup",
]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def missing_selectors(text: str, selectors: list[str]) -> list[str]:
    return [selector for selector in selectors if selector not in text]


def present_selectors(text: str, selectors: list[str]) -> list[str]:
    return [selector for selector in selectors if selector in text]


def main() -> int:
    errors: list[str] = []
    chart_runtime_css = read("chart_runtime.css")
    viewer_shell = read("src/styles/viewer-shell.css")
    runtime_core = read("src/styles/runtime-core.css")
    popup = read("src/styles/popup.css")

    for relative in [
        "APPLICATION_SHELL_BOUNDARY.md",
        "src/styles/viewer-shell.css",
        "src/styles/runtime-core.css",
        "src/styles/popup.css",
    ]:
        if not (ROOT / relative).exists():
            errors.append(f"missing required boundary file: {relative}")

    missing_in_viewer_shell = missing_selectors(viewer_shell, VIEWER_SELECTORS)
    if missing_in_viewer_shell:
        errors.append(f"viewer-shell.css missing selectors: {', '.join(missing_in_viewer_shell)}")

    missing_in_current_artifact = missing_selectors(chart_runtime_css, VIEWER_SELECTORS)
    if missing_in_current_artifact:
        errors.append(
            "chart_runtime.css no longer contains current viewer selectors; "
            f"HTML link migration must happen first: {', '.join(missing_in_current_artifact)}"
        )

    runtime_core_leaks = present_selectors(runtime_core, RUNTIME_CORE_FORBIDDEN)
    if runtime_core_leaks:
        errors.append(f"runtime-core.css contains viewer shell selectors: {', '.join(runtime_core_leaks)}")

    popup_leaks = present_selectors(popup, POPUP_FORBIDDEN)
    if popup_leaks:
        errors.append(f"popup.css contains viewer shell selectors: {', '.join(popup_leaks)}")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"applicationShellBoundary=fail errors={len(errors)}")
        return 1

    print("applicationShellBoundary=pass errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
