"""RMInbound：把管線 IFC 建成鎖定網面。不寫檔、不掛載。"""

from __future__ import annotations

from pathlib import Path

from loopflow_r2m.config import load_config
from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.ifc_read import inspect_inbound_ifc, should_warn_inbound_count
from loopflow_r2m.logutil import append_log
from loopflow_r2m.names import INBOUND_COUNT_WARNING_KEY
from loopflow_r2m.paths import config_paths
from loopflow_r2m.rhino.dialogs import confirm_yes, pick_ifc_file
from loopflow_r2m.rhino.tessellate import tessellate_inbound


COMMAND = "RMInbound"


def _print(message):
    import Rhino

    Rhino.RhinoApp.WriteLine(message)


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
    built = tessellate_inbound(doc, ifc_path, metres_to_doc)
    msg = "built %s, failed %s, no geometry %s" % (
        built["success"],
        built["failed"],
        len(report["no_geom"]),
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
