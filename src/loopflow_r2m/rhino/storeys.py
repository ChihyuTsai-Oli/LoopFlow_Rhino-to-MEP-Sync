"""讀 R2M 高程框。高程由 RMStorey 寫入，這裡只讀與驗算。"""

from __future__ import annotations

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.layers import is_storey_layer_path
from loopflow_r2m.names import STOREY_FL_KEY, STOREY_LAYER, STOREY_NAME_KEY
from loopflow_r2m.storey import Storey

# 高程與框的 Z 是同一個文件單位；只擋明顯被手改的值，不追浮點尾數。
FL_CONSISTENCY_TOLERANCE = 1e-4


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
    """回傳 storeys。缺少、衝突或高程被手改則 R2MStop。

    最高層無上界，所以不回傳上界值。
    """
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
                "Storey frames need %s and %s. Run RMStorey."
                % (STOREY_NAME_KEY, STOREY_FL_KEY)
            )
        polygon = _xy_polygon(geom)
        if len(polygon) < 3:
            raise R2MStop(
                "Storey frame %s is not a usable planar outline. Run RMStorey."
                % name
            )
        found.append(
            (Storey(name, fl, polygon), float(geom.GetBoundingBox(True).Min.Z))
        )
    if not found:
        raise R2MStop(
            "No storey frames on layer %s. Run RMStorey." % STOREY_LAYER
        )
    names = [item[0].name for item in found]
    if len(set(names)) != len(names):
        raise R2MStop("Duplicate storey names.")
    fls = [item[0].fl for item in found]
    if len(set(fls)) != len(fls):
        raise R2MStop("Duplicate storey FL values.")
    _check_against_frame_height(found)
    return [item[0] for item in found]


def _check_against_frame_height(found):
    """高程差必須等於框的 Z 差，否則是有人手動改過 UserText。"""
    base_storey, base_z = found[0]
    for storey, z in found[1:]:
        expected = base_storey.fl + (z - base_z)
        if abs(storey.fl - expected) > FL_CONSISTENCY_TOLERANCE:
            raise R2MStop(
                "Storey %s has %s=%s but its frame sits at %s. "
                "%s is written by RMStorey; run RMStorey again."
                % (storey.name, STOREY_FL_KEY, storey.fl, expected, STOREY_FL_KEY)
            )


def _xy_polygon(geom):
    """高程框的世界 XY 頂點。至少三點才算可用。"""
    pts = _polyline_xy(geom)
    if len(pts) < 3:
        pts = _segment_xy(geom)
    if len(pts) < 3:
        pts = _sampled_xy(geom)
    return _unique_xy(pts)


def _polyline_xy(geom):
    try:
        result = geom.TryGetPolyline()
    except TypeError:
        return ()
    polyline = _unpack_polyline(result)
    if polyline is None:
        return ()
    return tuple((pt.X, pt.Y) for pt in polyline)


def _unpack_polyline(result):
    if result is None or result is False:
        return None
    if result is True:
        return None
    if hasattr(result, "Count"):
        return result
    if isinstance(result, tuple) and len(result) == 2:
        ok, polyline = result
        return polyline if ok else None
    return None


def _segment_xy(geom):
    try:
        segs = geom.DuplicateSegments()
    except Exception:
        return ()
    if not segs:
        return ()
    return tuple((seg.PointAtStart.X, seg.PointAtStart.Y) for seg in segs)


def _sampled_xy(geom):
    try:
        ts = geom.DivideByCount(32, True)
    except Exception:
        return ()
    if not ts:
        return ()
    return tuple((geom.PointAt(t).X, geom.PointAt(t).Y) for t in ts)


def _unique_xy(pts):
    if not pts:
        return ()
    cleaned = [pts[0]]
    for pt in pts[1:]:
        prev = cleaned[-1]
        if abs(pt[0] - prev[0]) > 1e-9 or abs(pt[1] - prev[1]) > 1e-9:
            cleaned.append(pt)
    if len(cleaned) >= 2:
        first = cleaned[0]
        last = cleaned[-1]
        if abs(first[0] - last[0]) <= 1e-9 and abs(first[1] - last[1]) <= 1e-9:
            cleaned.pop()
    return tuple(cleaned)
