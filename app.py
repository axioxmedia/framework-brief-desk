"""Framework Brief Desk — local wizard for game briefs and investor plans."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from axioxmedia import aio_logo_png, apply_hwnd_icon, axiox_window_title
from exporter import to_docx_bytes, to_json_bytes, to_pdf_bytes
from schema import APP_VERSION, PRESETS, PRODUCT_EN, PRODUCT_ZH, public_schema, steps_for

def app_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


ROOT = app_root()
STATIC = ROOT / "static"


def data_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "data"
    return Path(__file__).resolve().parent / "data"


PROJECTS = data_root() / "projects"
EXPORTS = data_root() / "exports"
LOG_FILE = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent) / "framework_brief.log"

app = FastAPI(title=PRODUCT_ZH, version=APP_VERSION)
app.mount("/assets", StaticFiles(directory=STATIC), name="assets")


def write_log(msg: str) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")
    except Exception:
        pass


def show_error(text: str) -> None:
    try:
        if os.name == "nt":
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, text, PRODUCT_ZH, 0x10)
    except Exception:
        pass


class SaveBody(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)
    step: str = ""
    sub: str = ""
    lang: str = "zh"


class NewBody(BaseModel):
    docType: str = "game"
    projectName: str = ""


class PresetBody(BaseModel):
    genre: str


class ExportBody(BaseModel):
    id: str
    scope: str = Field(pattern="^(step|full|sub)$")
    step: str = ""
    sub: str = ""
    format: str = Field(pattern="^(json|docx|pdf)$")
    lang: str = "zh"


def _ensure_dirs() -> None:
    PROJECTS.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)


def _path(pid: str) -> Path:
    safe = "".join(ch for ch in pid if ch.isalnum() or ch in "-_")
    if not safe:
        raise HTTPException(400, "bad id")
    return PROJECTS / f"{safe}.json"


def _load(pid: str) -> dict:
    path = _path(pid)
    if not path.exists():
        raise HTTPException(404, "project not found")
    return json.loads(path.read_text(encoding="utf-8"))


def _store(doc: dict) -> None:
    _ensure_dirs()
    _path(doc["id"]).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/brand/logo.png")
def brand_logo() -> Response:
    return Response(content=aio_logo_png(), media_type="image/png")


@app.get("/favicon.ico")
def favicon() -> Response:
    return Response(content=aio_logo_png(), media_type="image/png")


@app.get("/api/defaults")
def defaults() -> dict:
    _ensure_dirs()
    return {
        "version": APP_VERSION,
        "productZh": PRODUCT_ZH,
        "productEn": PRODUCT_EN,
        "dataDir": str(data_root()),
        "brand": "axioxmedia",
    }


@app.get("/api/schema")
def schema_route() -> dict:
    return public_schema()


@app.get("/api/projects")
def list_projects() -> dict:
    _ensure_dirs()
    items = []
    for path in sorted(PROJECTS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        data = doc.get("data") or {}
        items.append(
            {
                "id": doc.get("id"),
                "projectName": data.get("projectName") or doc.get("id"),
                "docType": data.get("docType") or "game",
                "updated": doc.get("updated"),
            }
        )
    return {"items": items}


@app.post("/api/project/new")
def new_project(body: NewBody) -> dict:
    _ensure_dirs()
    pid = time.strftime("%Y%m%d-") + uuid.uuid4().hex[:8]
    doc = {
        "id": pid,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "data": {
            "docType": body.docType if body.docType in ("game", "business") else "game",
            "projectName": body.projectName,
        },
    }
    _store(doc)
    return doc


@app.get("/api/project/{pid}")
def get_project(pid: str) -> dict:
    return _load(pid)


@app.put("/api/project/{pid}")
def save_project(pid: str, body: SaveBody) -> dict:
    try:
        doc = _load(pid)
    except HTTPException:
        doc = {"id": pid, "created": time.strftime("%Y-%m-%dT%H:%M:%S"), "data": {}}
    merged = dict(doc.get("data") or {})
    merged.update(body.data or {})
    doc["data"] = merged
    doc["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    doc["step"] = body.step
    doc["sub"] = body.sub
    doc["lang"] = body.lang
    _store(doc)
    return {"ok": True, "updated": doc["updated"], "id": pid}


def infer_doc_type(payload: dict) -> str | None:
    if not isinstance(payload, dict):
        return None
    if payload.get("docType") in ("game", "business"):
        return payload["docType"]
    inner = payload.get("data")
    if isinstance(inner, dict) and inner.get("docType") in ("game", "business"):
        return inner["docType"]
    blob = inner if isinstance(inner, dict) else payload
    bp_hits = sum(1 for k in blob if str(k).startswith("bp"))
    game_hits = sum(1 for k in ("coreLoop", "feelPrimary", "offlineRecall", "genre", "playShape") if k in blob)
    if bp_hits >= 2 and game_hits == 0:
        return "business"
    if game_hits >= 2 and bp_hits == 0:
        return "game"
    return None


def harvest_custom_options(data: dict) -> dict:
    custom = dict(data.get("__customOptions") or {})
    steps = steps_for(data.get("docType") or "game")
    fields: list[dict] = []
    for step in steps:
        fields.extend(step.get("fields") or [])
        for sub in step.get("subs") or []:
            fields.extend(sub.get("fields") or [])
    for item in fields:
        if item.get("kind") not in ("radio", "check", "select"):
            continue
        known = {o["id"] for o in item.get("options") or []}
        bucket = list(custom.get(item["key"]) or [])
        have = {o.get("id") for o in bucket}
        raw = data.get(item["key"])
        values = raw if isinstance(raw, list) else ([raw] if raw not in (None, "") else [])
        for vid in values:
            sid = str(vid)
            if not sid or sid in known or sid in have:
                continue
            bucket.append({"id": sid, "zh": sid, "en": sid})
            have.add(sid)
        if bucket:
            custom[item["key"]] = bucket
    if custom:
        data["__customOptions"] = custom
    return data


class ImportBody(BaseModel):
    payload: dict[str, Any]
    expected: str = "game"


@app.post("/api/project/{pid}/import")
def import_project(pid: str, body: ImportBody) -> dict:
    expected = body.expected if body.expected in ("game", "business") else "game"
    found = infer_doc_type(body.payload)
    if found is None:
        raise HTTPException(
            409,
            detail={"code": "unknown", "found": None, "expected": expected},
        )
    if found != expected:
        raise HTTPException(
            409,
            detail={"code": "mismatch", "found": found, "expected": expected},
        )
    doc = _load(pid)
    incoming = body.payload.get("data") if isinstance(body.payload.get("data"), dict) else body.payload
    merged = dict(doc.get("data") or {})
    for key, value in incoming.items():
        if key in ("id", "created", "updated"):
            continue
        merged[key] = value
    merged["docType"] = expected
    merged = harvest_custom_options(merged)
    doc["data"] = merged
    doc["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _store(doc)
    return {"ok": True, "id": pid, "data": merged}


@app.post("/api/project/{pid}/preset")
def apply_preset(pid: str, body: PresetBody) -> dict:
    doc = _load(pid)
    preset = PRESETS.get(body.genre)
    if not preset:
        raise HTTPException(404, "unknown genre")
    data = dict(doc.get("data") or {})
    data["genre"] = body.genre
    data.update(preset)
    doc["data"] = data
    doc["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _store(doc)
    return doc


def _build_export(body: ExportBody) -> tuple[bytes, str, str]:
    doc = _load(body.id)
    lang = "zh" if body.lang != "en" else "en"
    ext = body.format if body.format in ("json", "docx", "pdf") else "json"
    if ext == "json":
        if body.scope == "full":
            payload = to_json_bytes(doc)
        else:
            payload = to_json_bytes(
                {"id": doc["id"], "step": body.step, "sub": body.sub, "data": doc.get("data")}
            )
        mime = "application/json"
    elif ext == "docx":
        payload = to_docx_bytes(doc, body.scope, body.step or None, body.sub or None, lang)
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        payload = to_pdf_bytes(doc, body.scope, body.step or None, body.sub or None, lang)
        mime = "application/pdf"
    name = (doc.get("data") or {}).get("projectName") or PRODUCT_EN
    safe = "".join(ch for ch in str(name) if ch.isalnum() or ch in "-_ ")[:40].strip() or "brief"
    filename = f"{safe}-{body.scope}-{body.step or 'all'}.{ext}"
    return payload, mime, filename


def _store_export_blob(token: str, payload: bytes, mime: str, filename: str) -> None:
    _ensure_dirs()
    (EXPORTS / f"{token}.bin").write_bytes(payload)
    (EXPORTS / f"{token}.meta.json").write_text(
        json.dumps({"filename": filename, "mime": mime}, ensure_ascii=False),
        encoding="utf-8",
    )


@app.post("/api/export")
def export_project(body: ExportBody) -> dict:
    payload, mime, filename = _build_export(body)
    token = uuid.uuid4().hex[:12]
    _store_export_blob(token, payload, mime, filename)
    return {"token": token, "filename": filename, "mime": mime, "url": f"/api/export/file/{token}"}


class ExportSaveBody(BaseModel):
    token: str
    path: str


@app.post("/api/export/save")
def export_save(body: ExportSaveBody) -> dict:
    safe = "".join(ch for ch in body.token if ch.isalnum())
    blob = EXPORTS / f"{safe}.bin"
    if not blob.exists():
        raise HTTPException(404, "expired")
    dest = Path(body.path).expanduser()
    if dest.exists() and dest.is_dir():
        meta_path = EXPORTS / f"{safe}.meta.json"
        name = safe
        if meta_path.exists():
            name = json.loads(meta_path.read_text(encoding="utf-8")).get("filename") or name
        dest = dest / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob.read_bytes())
    return {"ok": True, "path": str(dest)}


@app.get("/api/export/file/{token}")
def export_file(token: str) -> FileResponse:
    safe = "".join(ch for ch in token if ch.isalnum())
    blob = EXPORTS / f"{safe}.bin"
    meta_path = EXPORTS / f"{safe}.meta.json"
    if not blob.exists():
        raise HTTPException(404, "expired")
    mime = "application/octet-stream"
    filename = safe
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        filename = meta.get("filename") or filename
        mime = meta.get("mime") or mime
    return FileResponse(blob, media_type=mime, filename=filename)


def _free_port(preferred: int = 8787) -> int:
    import socket

    for port in (preferred, 8788, 8789, 8790, 0):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", port))
            chosen = int(sock.getsockname()[1])
        except OSError:
            chosen = -1
        finally:
            sock.close()
        if chosen > 0:
            return chosen
    raise RuntimeError("no local port")


def ensure_stdio() -> None:
    if sys.stdout is None:
        sys.stdout = LOG_FILE.open("a", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = LOG_FILE.open("a", encoding="utf-8")


def run_server(host: str, port: int, reload: bool = False) -> None:
    import uvicorn

    ensure_stdio()
    if reload:
        uvicorn.run(app, host=host, port=port, reload=True, log_level="warning", log_config=None)
        return
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="warning",
        log_config=None,
        lifespan="on",
        access_log=False,
    )
    server = uvicorn.Server(config)
    server.install_signal_handlers = False
    server.run()


def wait_ready(url: str, server_error: list[str], timeout: float = 30.0) -> None:
    import httpx
    import time as _t

    deadline = _t.time() + timeout
    while _t.time() < deadline:
        if server_error:
            raise RuntimeError(server_error[0])
        try:
            with httpx.Client(timeout=0.8, trust_env=False) as http:
                if http.get(url).status_code < 500:
                    return
        except httpx.HTTPError:
            _t.sleep(0.2)
    extra = f"\n{server_error[0]}" if server_error else ""
    raise RuntimeError(f"timeout {url}{extra}\n{LOG_FILE}")


class DeskBridge:
    def pick_save(self, filename: str = "export.json") -> str:
        try:
            import webview
        except Exception:
            return ""
        if not webview.windows:
            return ""
        name = filename or "export.json"
        ext = Path(name).suffix.lower()
        if ext == ".json":
            types = ("JSON (*.json)", "All files (*.*)")
        elif ext == ".pdf":
            types = ("PDF (*.pdf)", "All files (*.*)")
        elif ext == ".docx":
            types = ("Word (*.docx)", "All files (*.*)")
        else:
            types = ("All files (*.*)",)
        result = webview.windows[0].create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=name,
            file_types=types,
        )
        if not result:
            return ""
        return result if isinstance(result, str) else result[0]


def run_desktop() -> None:
    import threading
    import traceback
    import webbrowser

    import httpx  # noqa: F401

    write_log(f"start frozen={getattr(sys, 'frozen', False)}")
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    write_log(f"bind {url}")
    server_error: list[str] = []

    def _serve() -> None:
        try:
            run_server("127.0.0.1", port, reload=False)
        except Exception:
            server_error.append(traceback.format_exc())
            write_log(server_error[-1])

    thread = threading.Thread(target=_serve, name="uvicorn", daemon=True)
    thread.start()
    wait_ready(f"{url}/api/defaults", server_error)

    try:
        import webview

        window = webview.create_window(
            title=axiox_window_title(PRODUCT_ZH, PRODUCT_EN),
            url=url,
            width=1520,
            height=960,
            min_size=(980, 700),
            background_color="#0b0d12",
            js_api=DeskBridge(),
        )

        def paint_chrome(_=None) -> None:
            if os.name != "nt":
                return
            try:
                import ctypes

                hwnd = int(window.native.Handle.ToInt32())
                apply_hwnd_icon(hwnd)
                value = ctypes.c_int(1)
                for attr in (20, 19):
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)
                    )
            except Exception as exc:
                write_log(f"chrome: {exc}")

        try:
            window.events.shown += paint_chrome
        except Exception:
            pass
        webview.start()
        return
    except Exception:
        write_log(traceback.format_exc())
        webbrowser.open(url)
        while thread.is_alive():
            thread.join(timeout=0.5)


if __name__ == "__main__":
    import multiprocessing
    import traceback

    multiprocessing.freeze_support()
    ensure_stdio()
    try:
        desktop = "--web" not in sys.argv and os.environ.get("DEPLOY_DESK_WEB") != "1"
        if desktop:
            run_desktop()
        else:
            run_server("127.0.0.1", _free_port(8787), reload=False)
    except Exception:
        show_error("start failed:\n\n" + traceback.format_exc() + f"\n\n{LOG_FILE}")
        raise
