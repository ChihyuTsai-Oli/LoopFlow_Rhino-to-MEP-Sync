"""樓層編列與物件掛層。純 Python，不 import Rhino。

編列：使用者選全部高程框、指定 1F 與 RF，其餘由各框自身的 Z 推導。
掛層：依範圍盒底部 Z，區間下含上不含；最高層無上界。
"""

from __future__ import annotations

from collections import namedtuple

Storey = namedtuple("Storey", "name fl")
AssignResult = namedtuple("AssignResult", "name status")

# 一個框一個樓層：id 是呼叫端自己的識別（Rhino 端傳 Guid），z 是框的高度。
Frame = namedtuple("Frame", "id z")
PlannedStorey = namedtuple("PlannedStorey", "id name fl")

STATUS_OK = "ok"
STATUS_NO_STOREYS = "no_storeys"
STATUS_DUPLICATE_FL = "duplicate_fl"
STATUS_BELOW = "below"

# 同一個 Z 視為同一層；單位是 Rhino 文件單位。
Z_EPSILON = 1e-6


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

    ordered = sorted(rows, key=lambda item: float(item.z))
    for lower, upper in zip(ordered, ordered[1:]):
        if abs(float(upper.z) - float(lower.z)) <= Z_EPSILON:
            raise StoreyPlanError(
                "Two storey frames share the same height: %s" % float(lower.z)
            )

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
