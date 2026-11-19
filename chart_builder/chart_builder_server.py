from __future__ import annotations

import json
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
CHART_RUNTIME_DIR = ROOT.parent / "chart_runtime"
PAYLOAD_PATH = ROOT / "builder_prototype_payload.json"
LAYOUTS_PATH = ROOT / "builder_layouts.json"
CHARTS_PATH = ROOT / "builder_charts.json"
HOST = "127.0.0.1"
PORT = int(os.environ.get("CHART_BUILDER_PORT", "8766"))

app = FastAPI(title="Chart Builder Prototype", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

DEFAULT_PAYLOAD: dict[str, object] = {
    "chartId": "CHART-PROTOTYPE-001",
    "layout": {
        "layoutType": "semantic_grid",
        "columns": 2,
        "rows": 2,
        "areas": [
            {"area": "top_left", "role": "primary_visual", "x": 0, "y": 0, "w": 1, "h": 1},
            {"area": "top_right", "role": "secondary_visual", "x": 1, "y": 0, "w": 1, "h": 1},
            {"area": "bottom_left", "role": "primary_visual", "x": 0, "y": 1, "w": 1, "h": 1},
            {"area": "bottom_right", "role": "secondary_visual", "x": 1, "y": 1, "w": 1, "h": 1},
        ],
    },
    "components": [],
}


def load_payload() -> dict[str, object]:
    if PAYLOAD_PATH.exists():
        return json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    return DEFAULT_PAYLOAD


def load_layouts() -> list[dict[str, object]]:
    if LAYOUTS_PATH.exists():
        value = json.loads(LAYOUTS_PATH.read_text(encoding="utf-8"))
        if isinstance(value, list):
            return value
    return []


def save_layouts(layouts: list[dict[str, object]]) -> None:
    LAYOUTS_PATH.write_text(json.dumps(layouts, ensure_ascii=False, indent=2), encoding="utf-8")


def load_charts() -> list[dict[str, object]]:
    if CHARTS_PATH.exists():
        value = json.loads(CHARTS_PATH.read_text(encoding="utf-8"))
        if isinstance(value, list):
            return value
    return []


def save_charts(charts: list[dict[str, object]]) -> None:
    CHARTS_PATH.write_text(json.dumps(charts, ensure_ascii=False, indent=2), encoding="utf-8")


@app.get("/api/health")
def health() -> dict[str, object]:
    return {"ok": True, "service": "chart-builder-prototype", "backend": "fastapi"}


@app.get("/api/chart-builder/prototype")
def get_builder_prototype() -> dict[str, object]:
    return {"ok": True, "payload": load_payload()}


@app.put("/api/chart-builder/prototype")
def save_builder_prototype(payload: dict[str, object]) -> dict[str, object]:
    PAYLOAD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "payload": payload}


@app.get("/api/chart-builder/layouts")
def get_builder_layouts() -> dict[str, object]:
    return {"ok": True, "layouts": load_layouts()}


@app.put("/api/chart-builder/layouts")
def save_builder_layout(payload: dict[str, object]) -> dict[str, object]:
    name = str(payload.get("name", "")).strip()
    layout = payload.get("layout")
    if not name:
        return {"ok": False, "error": "layout name is required"}
    if not isinstance(layout, dict):
        return {"ok": False, "error": "layout object is required"}

    layouts = [item for item in load_layouts() if item.get("name") != name]
    saved = {"name": name, "layout": layout}
    layouts.append(saved)
    layouts.sort(key=lambda item: str(item.get("name", "")).lower())
    save_layouts(layouts)
    return {"ok": True, "layout": saved, "layouts": layouts}


@app.delete("/api/chart-builder/layouts/{layout_name}")
def delete_builder_layout(layout_name: str) -> dict[str, object]:
    layouts = load_layouts()
    next_layouts = [item for item in layouts if item.get("name") != layout_name]
    save_layouts(next_layouts)
    return {"ok": True, "deleted": len(next_layouts) != len(layouts), "layouts": next_layouts}


@app.get("/api/chart-builder/charts")
def get_builder_charts() -> dict[str, object]:
    return {"ok": True, "charts": load_charts()}


@app.put("/api/chart-builder/charts")
def save_builder_chart(payload: dict[str, object]) -> dict[str, object]:
    name = str(payload.get("name", "")).strip()
    chart_payload = payload.get("payload")
    if not name:
        return {"ok": False, "error": "chart name is required"}
    if not isinstance(chart_payload, dict):
        return {"ok": False, "error": "chart payload object is required"}

    charts = [item for item in load_charts() if item.get("name") != name]
    saved = {"name": name, "payload": chart_payload}
    charts.append(saved)
    charts.sort(key=lambda item: str(item.get("name", "")).lower())
    save_charts(charts)
    return {"ok": True, "chart": saved, "charts": charts}


@app.delete("/api/chart-builder/charts/{chart_name}")
def delete_builder_chart(chart_name: str) -> dict[str, object]:
    charts = load_charts()
    next_charts = [item for item in charts if item.get("name") != chart_name]
    save_charts(next_charts)
    return {"ok": True, "deleted": len(next_charts) != len(charts), "charts": next_charts}


@app.get("/api/charts/CHART-PROTOTYPE-001/runtime-render-payload")
def get_prototype_runtime_render_payload() -> dict[str, object]:
    return get_builder_prototype()


app.mount("/chart_runtime", StaticFiles(directory=str(CHART_RUNTIME_DIR), html=True), name="chart_runtime")
app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


def main() -> None:
    print(f"Chart Builder prototype server: http://{HOST}:{PORT}/builder_prototype.html")
    print("Press Ctrl+C to stop.")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
