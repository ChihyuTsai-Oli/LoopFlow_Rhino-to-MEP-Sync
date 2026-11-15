"""把套件內 IfcOpenShell 輪子插入 sys.path。不寫進 rhinocode site-packages。"""

from __future__ import annotations

import sys
from pathlib import Path


def python_tag(version_info=None) -> str:
    """Rhino 8 是 3.9，Rhino 9 是 3.13。其他版本仍用 py39。"""
    info = sys.version_info if version_info is None else version_info
    if int(info[0]) == 3 and int(info[1]) >= 13:
        return "py313"
    return "py39"


def vendor_dir(version_info=None):
    """開發期在 `wip/.vendor/py39` 或 `py313`；yak 在套件根 `vendor/`。"""
    tag = python_tag(version_info)
    package_root = Path(__file__).resolve().parents[2]
    for candidate in (
        package_root / "vendor" / tag,
        package_root / ".vendor" / tag,
    ):
        if candidate.is_dir():
            return candidate
    return package_root / ".vendor" / tag


def ensure_vendor():
    path = str(vendor_dir())
    if path not in sys.path:
        sys.path.insert(0, path)
    return path
