"""Rhino 文件單位 ↔ IFC 公尺。換算係數由呼叫端傳入（Rhino 的 UnitScale）。"""


def rhino_to_meters(value, scale_to_meters):
    """Rhino 長度乘上 UnitScale(..., Meters)。"""
    return float(value) * float(scale_to_meters)


def meters_to_rhino(value, scale_to_meters):
    """IFC 公尺乘上 UnitScale 的倒數。"""
    scale = float(scale_to_meters)
    if scale == 0:
        raise ValueError("單位換算係數不可為 0")
    return float(value) / scale
