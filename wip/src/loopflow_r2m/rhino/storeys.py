"""讀 R2M 高程框。"""

from __future__ import annotations

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.layers import is_storey_layer_path
from loopflow_r2m.names import (
    STOREY_FL_KEY,
    STOREY_FL_TOP_KEY,
    STOREY_LAYER,
    STOREY_NAME_KEY,
)
from loopflow_r2m.storey import Storey


def _user_text(obj, key):
    value = obj.Attributes.GetUserString(key)
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _parse_number(text, label):
    if text is None:
        return None
    try:
        return float(str(text).replace(",", "."))
    except ValueError:
        raise R2MStop("Storey %s is not a number: %s" % (label, text))


def read_storeys(doc):
    """回傳 (storeys, top_bound)。缺少或衝突則 R2MStop。"""
    found = []
    for obj in doc.Objects:
        if obj.IsReference:
            continue
        layer = doc.Layers[obj.Attributes.LayerIndex]
        if not is_storey_layer_path(layer.FullPath):
            continue
        geom = obj.Geometry
        if geom is None or not hasattr(geom, "IsClosed"):
            continue
        if not geom.IsClosed:
            raise R2MStop("Storey frame on %s is not closed." % STOREY_LAYER)
        name = _user_text(obj, STOREY_NAME_KEY)
        fl = _parse_number(_user_text(obj, STOREY_FL_KEY), STOREY_FL_KEY)
        if not name or fl is None:
            raise R2MStop(
                "Storey frames need %s and %s." % (STOREY_NAME_KEY, STOREY_FL_KEY)
            )
        top = _parse_number(_user_text(obj, STOREY_FL_TOP_KEY), STOREY_FL_TOP_KEY)
        found.append((Storey(name, fl), top))
    if not found:
        raise R2MStop("No storey frames on layer %s." % STOREY_LAYER)
    names = [item[0].name for item in found]
    if len(set(names)) != len(names):
        raise R2MStop("Duplicate storey names.")
    fls = [item[0].fl for item in found]
    if len(set(fls)) != len(fls):
        raise R2MStop("Duplicate storey FL values.")
    storeys = [item[0] for item in found]
    highest = max(storeys, key=lambda item: item.fl)
    top_bound = None
    for storey, top in found:
        if storey.name == highest.name:
            top_bound = top
    if top_bound is None:
        raise R2MStop(
            "Highest storey needs %s as the top bound." % STOREY_FL_TOP_KEY
        )
    if top_bound <= highest.fl:
        raise R2MStop("%s must be above the highest FL." % STOREY_FL_TOP_KEY)
    return storeys, top_bound
