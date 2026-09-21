"""依圖層與幾何類別收集物件，排除外參。"""

from __future__ import annotations

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.layers import is_storey_layer_path, layer_is_excluded
from loopflow_r2m.names import GEOM_CLASSES


def _object_class_key(obj):
    import Rhino

    ot = obj.ObjectType
    mapping = {
        Rhino.DocObjects.ObjectType.Brep: "brep",
        Rhino.DocObjects.ObjectType.Extrusion: "extrusion",
        Rhino.DocObjects.ObjectType.Mesh: "mesh",
        Rhino.DocObjects.ObjectType.SubD: "subd",
        Rhino.DocObjects.ObjectType.Surface: "surface",
        Rhino.DocObjects.ObjectType.Hatch: "hatch",
        Rhino.DocObjects.ObjectType.Curve: "curve",
        Rhino.DocObjects.ObjectType.Point: "point",
        Rhino.DocObjects.ObjectType.PointSet: "point",
    }
    return mapping.get(ot)


def layer_rows(doc, exclude_token):
    """列出可匯出圖層與目前件數（不含外參、不含排除記號）。"""
    counts = {}
    for obj in doc.Objects:
        if obj.IsReference:
            continue
        layer = doc.Layers[obj.Attributes.LayerIndex]
        path = layer.FullPath
        if layer_is_excluded(path, exclude_token):
            continue
        counts[path] = counts.get(path, 0) + 1
    rows = []
    for layer in doc.Layers:
        if layer.IsDeleted:
            continue
        path = layer.FullPath
        if is_storey_layer_path(path) or layer_is_excluded(path, exclude_token):
            continue
        rows.append({"path": path, "count": counts.get(path, 0)})
    return rows


def collect_objects(doc, selected_paths, geom_enabled):
    """selected_paths 必須精準符合物件圖層，不繼承父層。"""
    wanted = set(selected_paths)
    enabled = set(key for key, on in geom_enabled.items() if on)
    picked = []
    skipped_block = 0
    for obj in doc.Objects:
        if obj.IsReference:
            continue
        layer = doc.Layers[obj.Attributes.LayerIndex]
        if layer.FullPath not in wanted:
            continue
        import Rhino

        if obj.ObjectType == Rhino.DocObjects.ObjectType.InstanceReference:
            skipped_block += 1
            continue
        key = _object_class_key(obj)
        if key is None or key not in enabled:
            continue
        picked.append(obj)
    if skipped_block:
        # 第一版不炸塊，只報告。
        pass
    if not picked:
        raise R2MStop("No objects match the selected layers and geometry types.")
    return picked, skipped_block


def default_geom_enabled(saved=None):
    enabled = {key: default for key, _label, default in GEOM_CLASSES}
    if saved:
        for key, value in saved.items():
            if key in enabled:
                enabled[key] = bool(value)
    return enabled
