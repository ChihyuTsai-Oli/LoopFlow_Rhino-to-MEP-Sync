"""RMModels：建築殼 IFC 發布鏈。"""

from __future__ import annotations

from datetime import datetime, timezone
from os.path import basename

from loopflow_r2m.config import ConfigError, default_config, load_config, save_config
from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.guid import compress_guid
from loopflow_r2m.ifc_validate import ValidateError
from loopflow_r2m.ifc_write import ExportMeta, ExportProduct, ExportStorey
from loopflow_r2m.layers import layer_is_excluded
from loopflow_r2m.logutil import append_log
from loopflow_r2m.names import (
    DEFAULT_EXCLUDE_TOKEN,
    DEFAULT_MESH_DENSITY,
    PRODUCT_VERSION,
    STOREY_FL_TOP_KEY,
)
from loopflow_r2m.paths import config_paths
from loopflow_r2m.publish import publish_models
from loopflow_r2m.rhino.collect import collect_objects, default_geom_enabled, layer_rows
from loopflow_r2m.rhino.dialogs import show_models_dialog
from loopflow_r2m.rhino.meshutil import geometry_to_mesh, mesh_to_meters, meshing_parameters
from loopflow_r2m.rhino.storeys import read_storeys
from loopflow_r2m.storey import STATUS_OK, assign_storey
from loopflow_r2m.units import rhino_to_meters


COMMAND = "RMModels"


class _Restore(object):
    def __init__(self, doc):
        self.doc = doc
        self.modified = bool(doc.Modified)
        self.selected = [obj.Id for obj in doc.Objects if obj.IsSelected]
        self.hidden = []
        self.locked = []

    def reveal(self, obj):
        if obj.IsHidden:
            self.hidden.append(obj.Id)
            self.doc.Objects.Show(obj.Id, True)
        if obj.IsLocked:
            self.locked.append(obj.Id)
            self.doc.Objects.Unlock(obj.Id, True)

    def restore(self):
        for oid in self.hidden:
            self.doc.Objects.Hide(oid, True)
        for oid in self.locked:
            self.doc.Objects.Lock(oid, True)
        self.doc.Objects.UnselectAll()
        for oid in self.selected:
            self.doc.Objects.Select(oid)
        self.doc.Modified = self.modified


def _print(message):
    import Rhino

    Rhino.RhinoApp.WriteLine(message)


def run_rmmodels(doc):
    """回傳結果 dict。取消或擋住時帶 ok=False。"""
    restore = _Restore(doc)
    ctx = {"paths": None}
    try:
        return _run(doc, restore, ctx)
    except R2MStop as exc:
        paths = ctx["paths"]
        if paths:
            append_log(paths["log"], "ERROR", COMMAND, exc.english_message)
        _print("RMModels stopped: " + exc.english_message)
        return {"ok": False, "reason": exc.english_message}
    except ValidateError as exc:
        paths = ctx["paths"]
        if paths:
            append_log(paths["log"], "ERROR", COMMAND, str(exc))
        _print("RMModels validation failed: " + str(exc))
        return {"ok": False, "reason": str(exc)}
    except ConfigError as exc:
        _print("RMModels config error: " + str(exc))
        return {"ok": False, "reason": str(exc)}
    finally:
        restore.restore()


def _run(doc, restore, ctx):
    import Rhino

    path = doc.Path
    if not path:
        raise R2MStop("Save the document before publishing.")
    paths = config_paths(path)
    ctx["paths"] = paths
    paths["root"].mkdir(parents=True, exist_ok=True)
    paths["models"].mkdir(parents=True, exist_ok=True)
    append_log(paths["log"], "INFO", COMMAND, "start")

    document_name = basename(path)
    if paths["config"].is_file():
        config = load_config(paths["config"])
        config["document_name"] = document_name
    else:
        config = default_config(document_name, PRODUCT_VERSION)

    storeys, top_bound = read_storeys(doc)
    lines = ["%s  FL=%s" % (item.name, item.fl) for item in storeys]
    lines.append("%s=%s" % (STOREY_FL_TOP_KEY, top_bound))
    _print("Storeys:")
    for line in lines:
        _print("  " + line)

    saved_sel = config.get("layer_selection") or {}
    dialog_saved = {
        "exclude_token": saved_sel.get("exclude_token", DEFAULT_EXCLUDE_TOKEN),
        "layer_paths": saved_sel.get("layer_paths") or [],
        "layer_type_map": config.get("layer_type_map") or {},
        "geom": saved_sel.get("geom") or {},
        "mesh_density": config.get("mesh_density", DEFAULT_MESH_DENSITY),
    }
    choice = show_models_dialog(lines, layer_rows(doc, ""), dialog_saved)
    if choice is None:
        raise R2MStop("Cancelled.")

    exclude_token = choice["exclude_token"]
    selected = [
        path_
        for path_ in choice["layer_paths"]
        if not layer_is_excluded(path_, exclude_token)
    ]
    if not selected:
        raise R2MStop("No layers left after exclude token.")
    types = choice["layer_type_map"]
    missing = [path_ for path_ in selected if path_ not in types]
    if missing:
        raise R2MStop("Select an IFC type for layer: %s" % missing[0])

    geom_enabled = default_geom_enabled(choice["geom"])
    density = choice["mesh_density"]
    objects, skipped_block = collect_objects(doc, selected, geom_enabled)
    for obj in objects:
        restore.reveal(obj)

    scale = Rhino.RhinoMath.UnitScale(doc.ModelUnitSystem, Rhino.UnitSystem.Meters)
    mp = meshing_parameters(density, scale)
    products = []
    problems = []
    for obj in objects:
        mesh = geometry_to_mesh(obj.Geometry, mp)
        if mesh is None:
            problems.append("%s: no mesh" % obj.Id)
            continue
        bbox = mesh.GetBoundingBox(True)
        hit = assign_storey(bbox.Min.Z, storeys, top_bound)
        if hit.status != STATUS_OK:
            problems.append("%s: storey %s" % (obj.Id, hit.status))
            continue
        layer = doc.Layers[obj.Attributes.LayerIndex]
        vertices, faces = mesh_to_meters(mesh, scale)
        products.append(
            ExportProduct(
                ifc_type=types[layer.FullPath],
                global_id=compress_guid(str(obj.Id).replace("-", "")),
                name=str(obj.Id),
                storey_name=hit.name,
                vertices=vertices,
                faces=faces,
            )
        )
    if problems:
        raise R2MStop("Cannot publish: " + "; ".join(problems[:8]))
    if not products:
        raise R2MStop("No meshable objects.")

    export_storeys = [
        ExportStorey(item.name, rhino_to_meters(item.fl, scale)) for item in storeys
    ]
    meta = ExportMeta(
        filename=paths["ifc"].name,
        project_name=config.get("project_name") or paths["ifc"].stem,
        site_name=config.get("site_name") or config.get("project_name") or "Site",
        building_name=config.get("building_name") or config.get("project_name") or "Building",
        product_version=PRODUCT_VERSION,
    )
    report = publish_models(
        paths["pending"], paths["ifc"], meta, export_storeys, products
    )

    config["product_version"] = PRODUCT_VERSION
    config["layer_selection"] = {
        "exclude_token": exclude_token,
        "layer_paths": selected,
        "geom": geom_enabled,
    }
    config["layer_type_map"] = {path_: types[path_] for path_ in selected}
    config["mesh_density"] = density
    config["last_export"] = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ifc_path": "models/" + paths["ifc"].name,
        "object_count": len(products),
        "storey_count": len(storeys),
    }
    save_config(paths["config"], config)
    msg = "published %s objects, %s storeys" % (len(products), len(storeys))
    if skipped_block:
        msg += "; skipped %s blocks" % skipped_block
    append_log(paths["log"], "INFO", COMMAND, msg)
    _print("RMModels: " + msg)
    report["ok"] = True
    report["path"] = str(paths["ifc"])
    report["skipped_block"] = skipped_block
    return report
