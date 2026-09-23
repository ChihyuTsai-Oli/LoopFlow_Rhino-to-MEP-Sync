"""RMStorey：登記 R2M 高程框。

先選全部框，再彈窗選整棟或只做其中幾層。整棟：點 1F → 輸入 1F 高程 → 點 RF。
非整棟：點基準層 → 輸入名稱與高程，其餘依 Z 連續編號。
重跑會整批覆寫，包含手動改過的樓層名。
"""

from __future__ import annotations

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.logutil import append_log
from loopflow_r2m.names import STOREY_FL_KEY, STOREY_LAYER, STOREY_NAME_KEY
from loopflow_r2m.paths import config_paths
from loopflow_r2m.rhino.dialogs import (
    ask_number,
    ask_text,
    confirm_yes,
    pick_curves,
    pick_option,
)
from loopflow_r2m.rhino.layerutil import ensure_layer
from loopflow_r2m.storey import (
    Frame,
    StoreyPlanError,
    build_partial_storey_plan,
    build_storey_plan,
)

COMMAND = "RMStorey"
MODE_WHOLE = "WholeBuilding"
MODE_PARTIAL = "PartialStoreys"

# 框必須是水平平面：上下 Z 差在這個範圍內才算同一個高度。
FLATNESS_TOLERANCE = 1e-6


def _print(message):
    import Rhino

    Rhino.RhinoApp.WriteLine(message)


def _maybe_log(doc, level, message):
    path = doc.Path
    if not path:
        return
    append_log(config_paths(path)["log"], level, COMMAND, message)


def run_rmstorey(doc):
    """回傳結果 dict。取消或擋住時帶 ok=False。"""
    try:
        return _run(doc)
    except R2MStop as exc:
        _maybe_log(doc, "ERROR", exc.english_message)
        _print("RMStorey stopped: " + exc.english_message)
        return {"ok": False, "reason": exc.english_message}
    except StoreyPlanError as exc:
        _maybe_log(doc, "ERROR", str(exc))
        _print("RMStorey stopped: " + str(exc))
        return {"ok": False, "reason": str(exc)}


def _frame_z(doc, object_id):
    """回傳水平封閉曲線的高度。不合格則 R2MStop。"""
    obj = doc.Objects.FindId(object_id)
    if obj is None:
        raise R2MStop("A picked frame is no longer in the document.")
    geom = obj.Geometry
    if geom is None or not hasattr(geom, "IsClosed") or not geom.IsClosed:
        raise R2MStop("Storey frames must be closed curves.")
    box = geom.GetBoundingBox(True)
    if abs(box.Max.Z - box.Min.Z) > FLATNESS_TOLERANCE:
        raise R2MStop(
            "Storey frames must be flat and horizontal; one spans Z %s to %s."
            % (box.Min.Z, box.Max.Z)
        )
    return float(box.Min.Z)


def _run(doc):
    if not confirm_yes(
        "Storey frames must be closed, flat, and strictly larger than "
        "the objects you will publish. Objects that touch a frame will "
        "stop RMModels. Continue?",
        COMMAND,
    ):
        raise R2MStop("Cancelled.")

    # 先選框：預選的曲線可以直接 Enter。模式改彈窗，避免指令列 Enter 被當成取消。
    picked = pick_curves("Select all storey frames", True)
    if not picked:
        raise R2MStop("Cancelled.")

    frames = [Frame(oid, _frame_z(doc, oid)) for oid in picked]
    ids = [frame.id for frame in frames]
    _reject_duplicate_z(frames)
    _print(
        "Picked %s frames at Z: %s"
        % (len(frames), ", ".join(_fl_text(frame.z) for frame in sorted(frames, key=lambda item: item.z)))
    )

    mode = pick_option(
        "Whole building (1F and RF) or only the storeys in this model?",
        (MODE_WHOLE, MODE_PARTIAL),
        COMMAND,
    )
    if mode is None:
        raise R2MStop("Cancelled.")

    if mode == MODE_PARTIAL:
        planned = _plan_partial(frames, ids)
    else:
        planned = _plan_whole(frames, ids)

    return _write_plan(doc, planned)


def _reject_duplicate_z(frames):
    ordered = sorted(frames, key=lambda item: item.z)
    for lower, upper in zip(ordered, ordered[1:]):
        if abs(upper.z - lower.z) <= FLATNESS_TOLERANCE:
            raise R2MStop(
                "Two storey frames share the same height: %s. "
                "Move each frame to that storey's FL before running RMStorey."
                % _fl_text(lower.z)
            )


def _plan_whole(frames, ids):
    first = pick_curves("Select the 1F frame", False)
    if not first:
        raise R2MStop("Cancelled.")
    if first[0] not in ids:
        raise R2MStop("The 1F frame must be one of the selected frames.")

    first_fl = ask_number("1F elevation (document units)", COMMAND)
    if first_fl is None:
        raise R2MStop("Cancelled.")

    roof = pick_curves("Select the RF frame", False)
    if not roof:
        raise R2MStop("Cancelled.")
    if roof[0] not in ids:
        raise R2MStop("The RF frame must be one of the selected frames.")

    return build_storey_plan(
        frames, ids.index(first[0]), ids.index(roof[0]), first_fl
    )


def _plan_partial(frames, ids):
    picked = pick_curves("Select the reference storey frame", False)
    if not picked:
        raise R2MStop("Cancelled.")
    if picked[0] not in ids:
        raise R2MStop("The reference frame must be one of the selected frames.")

    name = ask_text("Name of that storey (for example 5F)", COMMAND)
    if name is None:
        raise R2MStop("Cancelled.")
    if not name:
        raise R2MStop("Storey name cannot be blank.")

    elevation = ask_number("Elevation of %s (document units)" % name, COMMAND)
    if elevation is None:
        raise R2MStop("Cancelled.")

    return build_partial_storey_plan(
        frames, ids.index(picked[0]), name, elevation
    )


def _write_plan(doc, planned):
    layer_index = ensure_layer(doc, STOREY_LAYER)
    for item in planned:
        obj = doc.Objects.FindId(item.id)
        # 必須用副本：把活的 Attributes 實例傳回 ModifyAttributes 會清掉既有 UserText。
        attr = obj.Attributes.Duplicate()
        attr.SetUserString(STOREY_NAME_KEY, item.name)
        attr.SetUserString(STOREY_FL_KEY, _fl_text(item.fl))
        attr.LayerIndex = layer_index
        doc.Objects.ModifyAttributes(obj, attr, True)
    doc.Views.Redraw()

    lines = ["%s  FL=%s" % (item.name, _fl_text(item.fl)) for item in planned]
    _print("RMStorey registered %s storeys on %s:" % (len(planned), STOREY_LAYER))
    for line in lines:
        _print("  " + line)
    _print("The top storey has no upper bound.")
    _maybe_log(doc, "INFO", "registered %s storeys" % len(planned))
    return {
        "ok": True,
        "layer": STOREY_LAYER,
        "storeys": [{"name": item.name, "fl": item.fl} for item in planned],
    }


def _fl_text(value):
    """去掉浮點尾數，讓 UserText 讀起來像使用者輸入的數字。"""
    text = "%.6f" % float(value)
    text = text.rstrip("0").rstrip(".")
    return text if text not in ("", "-") else "0"
