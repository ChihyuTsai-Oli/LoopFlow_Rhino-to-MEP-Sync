"""樓層編列與物件掛層。純 Python，不 import Rhino。

編列：整棟指定 1F 與 RF；非整棟指定一層名稱與高程，其餘依框的 Z 連續編號。
掛層：依範圍盒底部 Z，區間下含上不含；最高層無上界。
平面：勾選圖層上的物件必須嚴格落在該層高程框內；碰到框線擋住；完全在外則跳過。
"""

from __future__ import annotations

import re
from collections import namedtuple

AssignResult = namedtuple("AssignResult", "name status")


class Storey(namedtuple("_Storey", "name fl polygon")):
    """polygon 是平面頂點 (x, y)；測試可省略。"""

    def __new__(cls, name, fl, polygon=()):
        return super(Storey, cls).__new__(cls, name, fl, tuple(polygon))

# 一個框一個樓層：id 是呼叫端自己的識別（Rhino 端傳 Guid），z 是框的高度。
Frame = namedtuple("Frame", "id z")
PlannedStorey = namedtuple("PlannedStorey", "id name fl")

STATUS_OK = "ok"
STATUS_NO_STOREYS = "no_storeys"
STATUS_DUPLICATE_FL = "duplicate_fl"
STATUS_BELOW = "below"

XY_INSIDE = "inside"
XY_OUTSIDE = "outside"
XY_TOUCH = "touch"

# 同一個 Z 視為同一層；單位是 Rhino 文件單位。
Z_EPSILON = 1e-6
# 平面嚴格在內：貼齊邊視為碰觸。
XY_EPSILON = 1e-9


class StoreyPlanError(Exception):
    """編列不成立。message 是英文，直接給使用者看。"""


def build_storey_plan(frames, first_index, roof_index, first_fl):
    """回傳依 Z 由低到高排序的 PlannedStorey。

    frames：Frame 序列，順序不拘。
    first_index／roof_index：1F 與 RF 在 frames 裡的索引。
    first_fl：1F 的高程，Rhino 文件單位。

    高程一律 `first_fl + (該框 z − 1F 框 z)`，不逐層詢問。
    名稱：1F 以下 B1、B2…；1F 與 RF 之間 2F、3F…；RF 之上 R2F、R3F…。
    """
    rows = list(frames or [])
    if not rows:
        raise StoreyPlanError("No storey frames selected.")
    if not 0 <= first_index < len(rows):
        raise StoreyPlanError("The 1F frame must be one of the selected frames.")
    if not 0 <= roof_index < len(rows):
        raise StoreyPlanError("The RF frame must be one of the selected frames.")

    first_z = float(rows[first_index].z)
    roof_z = float(rows[roof_index].z)
    if roof_z < first_z - Z_EPSILON:
        raise StoreyPlanError("The RF frame is below the 1F frame.")

    ordered = _ordered_unique_z(rows)
    first_pos = _position(ordered, rows[first_index].id)
    roof_pos = _position(ordered, rows[roof_index].id)

    names = [None] * len(ordered)
    names[roof_pos] = "RF"
    names[first_pos] = "1F"
    # 地下層由近而遠：緊鄰 1F 下方的是 B1。
    for step, pos in enumerate(range(first_pos - 1, -1, -1), start=1):
        names[pos] = "B%s" % step
    # 1F 與 RF 之間依序往上，RF 不參與編號。
    for step, pos in enumerate(range(first_pos + 1, roof_pos), start=2):
        names[pos] = "%sF" % step
    # RF 之上是屋凸。
    for step, pos in enumerate(range(roof_pos + 1, len(ordered)), start=2):
        names[pos] = "R%sF" % step

    if len(set(names)) != len(names):
        raise StoreyPlanError(
            "Storey naming produced duplicates: %s" % ", ".join(names)
        )

    base = float(first_fl)
    return [
        PlannedStorey(frame.id, names[pos], base + (float(frame.z) - first_z))
        for pos, frame in enumerate(ordered)
    ]


def build_partial_storey_plan(frames, ref_index, ref_name, ref_fl):
    """非整棟：指定一層名稱與高程，其餘依 Z 連續編號，不產生 RF／R2F。"""
    rows = list(frames or [])
    if not rows:
        raise StoreyPlanError("No storey frames selected.")
    if not 0 <= ref_index < len(rows):
        raise StoreyPlanError("The reference frame must be one of the selected frames.")

    ref_ordinal = parse_storey_ordinal(ref_name)
    ordered = _ordered_unique_z(rows)
    ref_pos = _position(ordered, rows[ref_index].id)
    ref_z = float(rows[ref_index].z)
    base = float(ref_fl)

    planned = []
    for pos, frame in enumerate(ordered):
        ordinal = shift_storey_ordinal(ref_ordinal, pos - ref_pos)
        planned.append(
            PlannedStorey(
                frame.id,
                name_from_ordinal(ordinal),
                base + (float(frame.z) - ref_z),
            )
        )
    names = [item.name for item in planned]
    if len(set(names)) != len(names):
        raise StoreyPlanError(
            "Storey naming produced duplicates: %s" % ", ".join(names)
        )
    return planned


def parse_storey_ordinal(name):
    """1F／5／B1 → 整數序號。1F=1、B1=-1。0 與 RF 不合法。"""
    text = str(name or "").strip().upper().replace(" ", "")
    match = re.match(r"^B(\d+)$", text)
    if match:
        number = int(match.group(1))
        if number < 1:
            raise StoreyPlanError("Storey name %s is not a floor number." % name)
        return -number
    match = re.match(r"^(\d+)F?$", text)
    if match:
        number = int(match.group(1))
        if number < 1:
            raise StoreyPlanError("Storey name %s is not a floor number." % name)
        return number
    raise StoreyPlanError(
        "Partial storeys need a name like 5F or B1, not %s. "
        "Use WholeBuilding if this project has 1F and RF."
        % name
    )


def name_from_ordinal(ordinal):
    if ordinal >= 1:
        return "%sF" % ordinal
    if ordinal <= -1:
        return "B%s" % (-ordinal)
    raise StoreyPlanError("Storey numbering produced floor 0.")


def shift_storey_ordinal(base, delta):
    """移動 delta 層，跳過 0（B1 上一層是 1F）。"""
    step = 1 if delta > 0 else -1
    current = int(base)
    for _ in range(abs(int(delta))):
        current += step
        if current == 0:
            current += step
    return current


def _ordered_unique_z(rows):
    ordered = sorted(rows, key=lambda item: float(item.z))
    for lower, upper in zip(ordered, ordered[1:]):
        if abs(float(upper.z) - float(lower.z)) <= Z_EPSILON:
            raise StoreyPlanError(
                "Two storey frames share the same height: %s" % float(lower.z)
            )
    return ordered


def _position(ordered, frame_id):
    for index, frame in enumerate(ordered):
        if frame.id == frame_id:
            return index
    raise StoreyPlanError("Picked frame is not among the selected frames.")


def assign_storey(bottom_z, storeys):
    """回傳 AssignResult。status 不是 ok 時不得靜默猜測，也不得移動幾何。

    storeys：可迭代的 Storey（name、fl，文件單位）。
    最高層無上界；比它高的物件一律掛它。低於最低層則擋住。
    """
    rows = list(storeys or [])
    if not rows:
        return AssignResult(None, STATUS_NO_STOREYS)

    ordered = sorted(rows, key=lambda item: item.fl)
    fls = [item.fl for item in ordered]
    if len(set(fls)) != len(fls):
        return AssignResult(None, STATUS_DUPLICATE_FL)

    z = float(bottom_z)
    if z < ordered[0].fl:
        return AssignResult(None, STATUS_BELOW)

    for index, storey in enumerate(ordered):
        if index + 1 == len(ordered):
            return AssignResult(storey.name, STATUS_OK)
        if storey.fl <= z < ordered[index + 1].fl:
            return AssignResult(storey.name, STATUS_OK)
    return AssignResult(None, STATUS_BELOW)


def classify_bbox_xy(bbox_xy, polygon, epsilon=XY_EPSILON):
    """範圍盒平面相對封閉多邊形：嚴格在內／完全在外／碰觸。

    bbox_xy：(xmin, ymin, xmax, ymax)。polygon：至少三個 (x, y)。
    貼齊邊、跨邊、或範圍盒把框包住，都算碰觸。
    """
    ring = _closed_ring(polygon)
    if len(ring) < 4:
        raise ValueError("Storey frame polygon needs at least 3 vertices.")
    xmin, ymin, xmax, ymax = [float(v) for v in bbox_xy]
    if xmax < xmin:
        xmin, xmax = xmax, xmin
    if ymax < ymin:
        ymin, ymax = ymax, ymin
    corners = (
        (xmin, ymin),
        (xmax, ymin),
        (xmax, ymax),
        (xmin, ymax),
    )
    box_edges = (
        (corners[0], corners[1]),
        (corners[1], corners[2]),
        (corners[2], corners[3]),
        (corners[3], corners[0]),
    )
    poly_edges = tuple((ring[i], ring[i + 1]) for i in range(len(ring) - 1))

    for a0, a1 in box_edges:
        for b0, b1 in poly_edges:
            if _segments_touch(a0, a1, b0, b1, epsilon):
                return XY_TOUCH

    corner_hits = [_point_in_ring(pt, ring, epsilon) for pt in corners]
    if any(hit == "on" for hit in corner_hits):
        return XY_TOUCH
    if all(hit == "in" for hit in corner_hits):
        return XY_INSIDE

    for vertex in ring[:-1]:
        if _point_in_rect(vertex, xmin, ymin, xmax, ymax, epsilon) != "out":
            return XY_TOUCH
    return XY_OUTSIDE


def _closed_ring(polygon):
    pts = [(float(pt[0]), float(pt[1])) for pt in polygon]
    if not pts:
        return ()
    cleaned = [pts[0]]
    for pt in pts[1:]:
        prev = cleaned[-1]
        if abs(pt[0] - prev[0]) > XY_EPSILON or abs(pt[1] - prev[1]) > XY_EPSILON:
            cleaned.append(pt)
    if len(cleaned) >= 2:
        first = cleaned[0]
        last = cleaned[-1]
        if abs(first[0] - last[0]) > XY_EPSILON or abs(first[1] - last[1]) > XY_EPSILON:
            cleaned.append(first)
    elif cleaned:
        cleaned.append(cleaned[0])
    return tuple(cleaned)


def _point_in_rect(pt, xmin, ymin, xmax, ymax, epsilon):
    x, y = pt
    if (
        x < xmin - epsilon
        or x > xmax + epsilon
        or y < ymin - epsilon
        or y > ymax + epsilon
    ):
        return "out"
    if (
        abs(x - xmin) <= epsilon
        or abs(x - xmax) <= epsilon
        or abs(y - ymin) <= epsilon
        or abs(y - ymax) <= epsilon
    ):
        return "on"
    return "in"


def _point_in_ring(pt, ring, epsilon):
    """射線法。在邊上回 on，嚴格內部回 in。"""
    for i in range(len(ring) - 1):
        if _point_on_segment(pt, ring[i], ring[i + 1], epsilon):
            return "on"
    x, y = pt
    inside = False
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        if (y1 > y) != (y2 > y):
            at_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < at_x - epsilon:
                inside = not inside
            elif abs(x - at_x) <= epsilon:
                return "on"
    return "in" if inside else "out"


def _point_on_segment(pt, a, b, epsilon):
    if _cross(a, b, pt) > epsilon:
        return False
    dot = (pt[0] - a[0]) * (b[0] - a[0]) + (pt[1] - a[1]) * (b[1] - a[1])
    if dot < -epsilon:
        return False
    length = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
    return dot <= length + epsilon


def _cross(a, b, c):
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


def _segments_touch(a0, a1, b0, b1, epsilon):
    o1 = _orient(a0, a1, b0)
    o2 = _orient(a0, a1, b1)
    o3 = _orient(b0, b1, a0)
    o4 = _orient(b0, b1, a1)
    if o1 * o2 < -epsilon and o3 * o4 < -epsilon:
        return True
    if abs(o1) <= epsilon and _point_on_segment(b0, a0, a1, epsilon):
        return True
    if abs(o2) <= epsilon and _point_on_segment(b1, a0, a1, epsilon):
        return True
    if abs(o3) <= epsilon and _point_on_segment(a0, b0, b1, epsilon):
        return True
    if abs(o4) <= epsilon and _point_on_segment(a1, b0, b1, epsilon):
        return True
    return False


def _orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
