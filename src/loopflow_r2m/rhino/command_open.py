"""RMOpen：設定根英文摘要。"""

from __future__ import annotations

from pathlib import Path

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.health import health_lines
from loopflow_r2m.logutil import append_log
from loopflow_r2m.paths import config_paths
from loopflow_r2m.rhino.dialogs import show_open_health


COMMAND = "RMOpen"
REPO_DOCS = Path(__file__).resolve().parents[3] / "docs"


def _print(message):
    import Rhino

    Rhino.RhinoApp.WriteLine(message)


def run_rmopen(doc):
    try:
        return _run(doc)
    except R2MStop as exc:
        _print("RMOpen stopped: " + exc.english_message)
        return {"ok": False, "reason": exc.english_message}


def _run(doc):
    path = doc.Path
    if not path:
        raise R2MStop("Save the document before opening project settings.")
    paths = config_paths(path)
    append_log(paths["log"], "INFO", COMMAND, "start")
    lines = health_lines(paths)
    for line in lines:
        _print(line)
    folders = {
        "config": str(paths["root"]),
        "models": str(paths["models"]),
        "docs": str(REPO_DOCS),
    }
    paths["root"].mkdir(parents=True, exist_ok=True)
    paths["models"].mkdir(parents=True, exist_ok=True)
    show_open_health(lines, folders)
    append_log(paths["log"], "INFO", COMMAND, "ok")
    return {"ok": True, "lines": lines}
