"""把套件內 IfcOpenShell 輪子插入 sys.path。不寫進 rhinocode site-packages。"""

from __future__ import annotations

import sys
from pathlib import Path


def vendor_dir():
    return Path(__file__).resolve().parents[2] / ".vendor" / "py39"


def ensure_vendor():
    path = str(vendor_dir())
    if path not in sys.path:
        sys.path.insert(0, path)
    return path
