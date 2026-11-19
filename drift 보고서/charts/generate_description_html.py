from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "charts" / "descriptions"
CHART_ID_RE = re.compile(r"CHART-[A-Z0-9]+(?:-[A-Z0-9]+)+")


def chart_id_to_file(chart_id: str) -> str:
    return chart_id.lower().replace("-", "_") + "_desc.html"


def inline_md(text: str) -> str:
    value = html.escape(text)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    return value


def extract_sections(markdown: str) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_id: str | None = None
    current_lines: list[str] = []
    for line in markdown.splitlines():
        match = re.match(r"^##\s+(CHART-[A-Z0-9]+(?:-[A-Z0-9]+)+)(?:\s*:.*)?\s*$", line)
        if match:
            if current_id:
                sections.append((current_id, current_lines))
            current_id = match.group(1)
            current_lines = []
        elif current_id:
            current_lines.append(line)
    if current_id:
        sections.append((current_id, current_lines))
    return sections


def section_to_html(chart_id: str, lines: list[str]) -> str:
    body = markdown_lines_to_body(lines)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(chart_id)} 설명</title>
  <link rel="stylesheet" href="./description.css">
</head>
<body>
  <main class="doc">
    <p class="chart-id">{html.escape(chart_id)}</p>
    <h1>{html.escape(chart_id)} 해석</h1>
    {' '.join(body)}
  </main>
</body>
</html>
"""


def markdown_lines_to_body(lines: list[str]) -> list[str]:
    body: list[str] = []
    paragraph: list[str] = []
    code_lines: list[str] = []
    in_code = False
    in_list = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            body.append(f"<p>{inline_md(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            body.append("</ul>")
            in_list = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("!["):
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                body.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
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
            body.append(f"<h{level}>{inline_md(heading.group(2))}</h{level}>")
            continue
        item = re.match(r"^-\s+(.+)$", stripped)
        if item:
            flush_paragraph()
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{inline_md(item.group(1))}</li>")
            continue
        paragraph.append(stripped)

    flush_paragraph()
    close_list()
    if in_code:
        body.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")

    return body


def write_css() -> None:
    css = """body{margin:0;background:#fff;color:#17212b;font-family:"Segoe UI",Arial,sans-serif}.doc{max-width:920px;margin:0 auto;padding:34px 42px 54px}.chart-id{margin:0 0 8px;color:#5e6976;font-size:13px;font-weight:800}h1{margin:0 0 24px;font-size:28px;line-height:1.25}h2{margin:28px 0 10px;font-size:20px}h3{margin:24px 0 8px;font-size:17px}p,li{font-size:14px;line-height:1.65}p{margin:0 0 12px}ul{margin:0 0 14px 20px;padding:0}pre{margin:12px 0 18px;padding:14px 16px;border:1px solid #d8dee4;border-radius:8px;background:#f6f7f8;overflow:auto}code{font-family:Consolas,"Courier New",monospace;font-size:13px}p code,li code{padding:1px 4px;border-radius:4px;background:#eef2f5}"""
    (OUT_DIR / "description.css").write_text(css, encoding="utf-8")


def extract_method_mapping(markdown: str) -> dict[str, list[dict[str, str]]]:
    mapping: dict[str, list[dict[str, str]]] = {}
    seen: set[tuple[str, str]] = set()
    for line in markdown.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        method, chart_cell, description = cells[:3]
        if (
            method in {"drift 메소드", "---"}
            or method.startswith("CHART-")
            or not CHART_ID_RE.search(chart_cell)
        ):
            continue
        for chart_id in CHART_ID_RE.findall(chart_cell):
            key = (chart_id, method)
            if key in seen:
                continue
            seen.add(key)
            mapping.setdefault(chart_id, []).append({
                "method": method,
                "description": description,
            })
    return dict(sorted(mapping.items()))


def render_method_doc_section(heading: str, lines: list[str]) -> str:
    return f"<h2>{inline_md(heading)}</h2>" + " ".join(markdown_lines_to_body(lines))


def extract_variant_sections(markdown: str, source_name: str) -> dict[str, dict[str, str]]:
    title_match = re.search(r"^#\s+(.+)$", markdown, re.M)
    title = title_match.group(1).strip() if title_match else source_name
    h2_sections: list[dict[str, object]] = []
    sections: dict[str, dict[str, str]] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_heading, current_lines
        if not current_heading:
            return
        variant_match = re.match(r"^(?:\d+\.\s*)?변종(?:\s+\d+)?:\s*([A-Z0-9_]+)\s*$", current_heading)
        h2_sections.append({
            "heading": current_heading,
            "lines": current_lines,
            "variant": variant_match.group(1) if variant_match else None,
        })

    for line in markdown.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            flush()
            current_heading = match.group(1)
            current_lines = []
        elif current_heading:
            current_lines.append(line)
    flush()

    variant_indexes = [index for index, section in enumerate(h2_sections) if section["variant"]]
    if not variant_indexes:
      return sections
    first_variant = min(variant_indexes)
    last_variant = max(variant_indexes)
    intro_sections = h2_sections[:first_variant]
    guide_sections = [section for index, section in enumerate(h2_sections) if index > last_variant and not section["variant"]]

    for section in h2_sections:
        variant = section["variant"]
        if not variant:
            continue
        selected_heading = f"{variant} 탐지 방법"
        html_parts = [
            f'<p class="chart-id">{html.escape(source_name)}</p>',
            f"<h1>{html.escape(selected_heading)}</h1>",
            f'<p class="method-source">{html.escape(title)}</p>',
        ]
        if intro_sections:
            html_parts.append("<h2>방법 family 개요</h2>")
            for intro in intro_sections:
                html_parts.append(render_method_doc_section(str(intro["heading"]), list(intro["lines"])))
        html_parts.append("<h2>선택한 변종 상세</h2>")
        html_parts.append(render_method_doc_section(str(section["heading"]), list(section["lines"])))
        if guide_sections:
            html_parts.append("<h2>선택 및 보고 가이드</h2>")
            for guide in guide_sections:
                html_parts.append(render_method_doc_section(str(guide["heading"]), list(guide["lines"])))
        sections[str(variant)] = {
            "title": selected_heading,
            "source": title,
            "html": "".join(html_parts),
        }
    return sections


def load_variant_sections() -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    paths = sorted((ROOT / "algorithm_variants").glob("*_algorithm_variants.md"))
    for path in paths:
        if not path.exists():
            continue
        source_name = path.relative_to(ROOT).as_posix()
        sections.update(extract_variant_sections(path.read_text(encoding="utf-8"), source_name))
    return sections


def write_method_data() -> tuple[int, int]:
    guide_path = ROOT / "chart_docs" / "drift_method_variant_chart_guide.md"
    method_mapping = extract_method_mapping(guide_path.read_text(encoding="utf-8"))
    data_js = "window.CHART_METHODS = " + json.dumps(method_mapping, ensure_ascii=False) + ";\n"
    (ROOT / "charts" / "method_data.js").write_text(data_js, encoding="utf-8")
    variant_sections = load_variant_sections()
    method_descriptions: dict[str, dict[str, str]] = {}
    for methods in method_mapping.values():
        for item in methods:
            method = item["method"]
            variant = method.rsplit("/", 1)[-1].strip()
            if method in method_descriptions:
                continue
            section = variant_sections.get(variant)
            if section:
                method_descriptions[method] = {
                    "variant": variant,
                    "source": section["source"],
                    "html": section["html"],
                }
            else:
                method_descriptions[method] = {
                    "variant": variant,
                    "source": "",
                    "html": (
                        f'<p class="chart-id">{html.escape(variant)}</p>'
                        f'<h1>{html.escape(method)} 탐지 방법</h1>'
                        f'<p>{html.escape(item["description"])}</p>'
                        "<p>연결된 상세 알고리즘 변종 문서 섹션을 찾지 못했습니다.</p>"
                    ),
                }
    desc_js = "window.METHOD_DESCRIPTIONS = " + json.dumps(method_descriptions, ensure_ascii=False) + ";\n"
    (ROOT / "charts" / "method_description_data.js").write_text(desc_js, encoding="utf-8")
    return sum(len(methods) for methods in method_mapping.values()), len(method_descriptions)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_css()
    written = 0
    description_data: dict[str, str] = {}
    chart_doc_dir = ROOT / "chart_docs"
    for path in sorted(chart_doc_dir.glob("drift_chart_interpretation_*.md")):
        if path.name == "drift_chart_interpretation_guide.md":
            continue
        for chart_id, lines in extract_sections(path.read_text(encoding="utf-8")):
            html_text = section_to_html(chart_id, lines)
            (OUT_DIR / chart_id_to_file(chart_id)).write_text(html_text, encoding="utf-8")
            parsed = re.search(r'<main class="doc">(.*)</main>', html_text, re.S)
            description_data[chart_id] = parsed.group(1).strip() if parsed else ""
            written += 1
    data_js = "window.CHART_DESCRIPTIONS = " + json.dumps(description_data, ensure_ascii=False) + ";\n"
    (ROOT / "charts" / "description_data.js").write_text(data_js, encoding="utf-8")
    methods, method_descriptions = write_method_data()
    print(f"written={written} methods={methods} method_descriptions={method_descriptions}")


if __name__ == "__main__":
    main()
