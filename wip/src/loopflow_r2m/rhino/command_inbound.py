"""RMInbound：把管線 IFC 建成鎖定網面。不寫檔、不掛載。"""

from __future__ import annotations

from pathlib import Path

from loopflow_r2m.config import ConfigError, load_config
from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.ifc_read import inspect_inbound_ifc, should_warn_inbound_count
from loopflow_r2m.logutil import append_log
from loopflow_r2m.names import ELEVATION_SHIFT_KEY, INBOUND_COUNT_WARNING_KEY
from loopflow_r2m.paths import config_paths
from loopflow_r2m.rhino.dialogs import confirm_yes, pick_config_file, pick_ifc_file
from loopflow_r2m.rhino.tessellate import tessellate_inbound


COMMAND = "RMInbound"


def _print(message):
    import Rhino

    Rhino.RhinoApp.WriteLine(message)


def _shift_from_config_path(path):
    """讀 elevation_shift。沒有欄位就停，不猜 0。"""
    try:
        data = load_config(path)
    except ConfigError as exc:
        raise R2MStop("Cannot read config.json: %s" % exc) from exc
    value = data.get(ELEVATION_SHIFT_KEY)
    if value is None or value == "":
        raise R2MStop(
            "config.json has no elevation_shift. Run RMModels on the working file first."
        )
    try:
        return float(value)
    except (TypeError, ValueError):
        raise R2MStop("elevation_shift must be a number.")


def _resolve_elevation_shift(doc):
    """已存檔且 config 有差值就用；否則請選工作檔的 config.json。"""
    if doc.Path:
        config_file = config_paths(doc.Path)["config"]
        if config_file.is_file():
            try:
                data = load_config(config_file)
            except ConfigError:
                data = None
            if data is not None:
                value = data.get(ELEVATION_SHIFT_KEY)
                if value is not None and value != "":
                    try:
                        return float(value)
                    except (TypeError, ValueError):
                        raise R2MStop("elevation_shift must be a number.")
    _print("Pick the working file's config.json (has elevation_shift).")
    chosen = pick_config_file()
    if not chosen:
        raise R2MStop("Cancelled.")
    return _shift_from_config_path(Path(chosen))


def _maybe_log(doc, level, message):
    path = doc.Path
    if not path:
        return
    append_log(config_paths(path)["log"], level, COMMAND, message)


def run_rminbound(doc):
    """回傳結果 dict。未存檔也可以跑。"""
    try:
        return _run(doc)
    except R2MStop as exc:
        _maybe_log(doc, "ERROR", exc.english_message)
        _print("RMInbound stopped: " + exc.english_message)
        return {"ok": False, "reason": exc.english_message}


def _run(doc):
    import Rhino

    _print("Document units: %s" % doc.ModelUnitSystem)
    if not confirm_yes(
        "Document units are %s. Continue?" % doc.ModelUnitSystem, COMMAND
    ):
        raise R2MStop("Cancelled.")

    existing = 0
    for _obj in doc.Objects:
        existing += 1
    if existing and not confirm_yes(
        "This document already has objects. Add inbound meshes anyway?", COMMAND
    ):
        raise R2MStop("Cancelled.")

    ifc_path = pick_ifc_file()
    if not ifc_path:
        raise R2MStop("Cancelled.")
    ifc_path = Path(ifc_path)
    if ifc_path.suffix.lower() != ".ifc":
        raise R2MStop("Pick an IFC file.")

    _maybe_log(doc, "INFO", "start")
    report = inspect_inbound_ifc(ifc_path)
    candidates = report["candidates"]
    _print("Source types:")
    for kind in sorted(report["source"]):
        _print("  %s  %s" % (kind, report["source"][kind]))
    _print("Candidates: %s" % len(candidates))
    _print("No geometry: %s" % len(report["no_geom"]))

    threshold = None
    if doc.Path:
        config_file = config_paths(doc.Path)["config"]
        if config_file.is_file():
            threshold = load_config(config_file).get(INBOUND_COUNT_WARNING_KEY)
    if should_warn_inbound_count(len(candidates), threshold):
        if not confirm_yes(
            "%s meshable products. Continue?" % len(candidates), COMMAND
        ):
            raise R2MStop("Cancelled.")

    metres_to_doc = 1.0 / Rhino.RhinoMath.UnitScale(
        doc.ModelUnitSystem, Rhino.UnitSystem.Meters
    )
    shift = _resolve_elevation_shift(doc)
    _print("Elevation shift (FL minus frame Z): %s" % shift)
    built = tessellate_inbound(doc, ifc_path, metres_to_doc, shift)
    msg = "built %s, failed %s, no geometry %s, elevation_shift %s" % (
        built["success"],
        built["failed"],
        len(report["no_geom"]),
        shift,
    )
    _maybe_log(doc, "INFO", msg)
    _print("RMInbound: " + msg)
    _print("Command does not save or attach a worksession.")
    return {
        "ok": True,
        "source": report["source"],
        "candidates": len(candidates),
        "success": built["success"],
        "failed": built["failed"],
        "no_geom": len(report["no_geom"]),
    }
