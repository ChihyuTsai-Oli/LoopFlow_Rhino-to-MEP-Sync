"""讀入管線 IFC 的檢查與命名。不 import Rhino。"""

from __future__ import annotations

import hashlib

from .exceptions import R2MStop
from .ifc_validate import SPATIAL
from .names import INBOUND_LAYER_ROOT
from .vendor import ensure_vendor


def inbound_object_name(ifc_type, global_id):
    """物件名稱寫死 IfcType:GlobalId。"""
    return "%s:%s" % (ifc_type, global_id)


def inbound_layer_path(ifc_type):
    return "%s::%s" % (INBOUND_LAYER_ROOT, ifc_type)


def inbound_layer_color(ifc_type):
    """依類型穩定上色，避免過暗。"""
    digest = hashlib.md5(str(ifc_type).encode("utf-8")).digest()
    return (
        48 + digest[0] % 180,
        48 + digest[1] % 180,
        48 + digest[2] % 180,
    )


def should_warn_inbound_count(candidate_count, threshold):
    """門檻未填（None／空白／非正整數）則不警告。"""
    if threshold is None or threshold == "":
        return False
    try:
        limit = int(threshold)
    except (TypeError, ValueError):
        return False
    if limit <= 0:
        return False
    return int(candidate_count) > limit


def inspect_inbound_ifc(path):
    """開 IFC、確認 IFC4、統計來源／候選／無幾何。無可建幾何則停。"""
    ensure_vendor()
    try:
        import ifcopenshell
    except Exception as exc:
        raise R2MStop("Cannot load IfcOpenShell: %s" % exc) from exc

    try:
        ifc = ifcopenshell.open(str(path))
    except Exception as exc:
        raise R2MStop("Cannot open IFC: %s" % exc) from exc
    if ifc.schema != "IFC4":
        raise R2MStop("Schema is %s, expected IFC4." % ifc.schema)

    source = {}
    candidates = []
    no_geom = []
    for item in ifc.by_type("IfcProduct"):
        kind = item.is_a()
        if kind in SPATIAL:
            continue
        source[kind] = source.get(kind, 0) + 1
        row = {
            "ifc_type": kind,
            "global_id": getattr(item, "GlobalId", "") or "",
            "name": getattr(item, "Name", None),
        }
        if item.Representation:
            candidates.append(row)
        else:
            no_geom.append(row)
    if not candidates:
        raise R2MStop("No meshable products in this IFC.")
    return {
        "schema": ifc.schema,
        "source": source,
        "candidates": candidates,
        "no_geom": no_geom,
    }
