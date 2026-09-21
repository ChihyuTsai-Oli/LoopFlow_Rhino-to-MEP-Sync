"""依範圍盒底部 Z 判斷物件掛哪一層。區間下含上不含。"""

from __future__ import annotations

from collections import namedtuple

Storey = namedtuple("Storey", "name fl")
AssignResult = namedtuple("AssignResult", "name status")

STATUS_OK = "ok"
STATUS_NO_STOREYS = "no_storeys"
STATUS_MISSING_TOP = "missing_top"
STATUS_INVALID_TOP = "invalid_top"
STATUS_DUPLICATE_FL = "duplicate_fl"
STATUS_BELOW = "below"
STATUS_ABOVE = "above"


def assign_storey(bottom_z, storeys, top_bound):
    """回傳 AssignResult。status 不是 ok 時不得靜默猜測，也不得移動幾何。

    storeys：可迭代的 Storey（name、fl，文件單位）。
    top_bound：最高層上界，與 fl 同一單位。
    """
    rows = list(storeys or [])
    if not rows:
        return AssignResult(None, STATUS_NO_STOREYS)
    if top_bound is None:
        return AssignResult(None, STATUS_MISSING_TOP)

    ordered = sorted(rows, key=lambda item: item.fl)
    fls = [item.fl for item in ordered]
    if len(set(fls)) != len(fls):
        return AssignResult(None, STATUS_DUPLICATE_FL)
    if float(top_bound) <= ordered[-1].fl:
        return AssignResult(None, STATUS_INVALID_TOP)

    z = float(bottom_z)
    if z < ordered[0].fl:
        return AssignResult(None, STATUS_BELOW)
    if z >= float(top_bound):
        return AssignResult(None, STATUS_ABOVE)

    for index, storey in enumerate(ordered):
        upper = ordered[index + 1].fl if index + 1 < len(ordered) else float(top_bound)
        if storey.fl <= z < upper:
            return AssignResult(storey.name, STATUS_OK)
    return AssignResult(None, STATUS_ABOVE)
