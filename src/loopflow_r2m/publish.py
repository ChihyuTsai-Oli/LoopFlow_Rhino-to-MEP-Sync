"""pending → atomic 取代 last-good。失敗不碰 last-good。"""

from __future__ import annotations

import os
from pathlib import Path


def atomic_replace(pending_path, last_good_path):
    """同一磁碟上以 os.replace 覆寫 last-good。"""
    pending = Path(pending_path)
    last_good = Path(last_good_path)
    if not pending.is_file():
        raise FileNotFoundError("pending IFC 不存在")
    last_good.parent.mkdir(parents=True, exist_ok=True)
    os.replace(str(pending), str(last_good))
    return last_good


def publish_models(pending_path, last_good_path, meta, storeys, products):
    """寫 pending、驗證、atomic。驗證失敗則不碰 last-good。"""
    from .ifc_validate import validate_models_ifc
    from .ifc_write import write_models_ifc
    from .vendor import ensure_vendor

    ensure_vendor()
    pending = Path(pending_path)
    pending.parent.mkdir(parents=True, exist_ok=True)
    write_models_ifc(str(pending), meta, storeys, products)
    report = validate_models_ifc(str(pending), len(products))
    atomic_replace(pending, last_good_path)
    return report
