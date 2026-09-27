#! python 3
# -*- coding: utf-8 -*-
"""G02 套件登錄的正式指令 RMInbound。開發期入口仍是 wip/commands/RMInbound.py。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PLUGIN_ID = "814a8439-9948-530a-ad43-69048e85ec1e"
PLUGIN_NAME = "LoopFlow_R2M"
YAK_PACKAGE = "loopflow-rhino-to-mep-sync"
DEV_SRC = Path(r"E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync") / "wip" / "src"


def _has_r2m(root):
    try:
        return (root / "loopflow_r2m" / "__init__.py").is_file()
    except Exception:
        return False


def _from_package_dir(package_dir):
    if package_dir is None:
        return None
    try:
        package_dir = Path(str(package_dir))
        if not package_dir.is_dir():
            return None
        package_dir = package_dir.resolve()
    except Exception:
        return None
    for candidate in (package_dir / "lib", package_dir / "src", package_dir):
        if _has_r2m(candidate):
            return candidate
    return None


def _from_rhp(rhp):
    if not rhp:
        return None
    try:
        path = Path(str(rhp))
        if path.is_file():
            return _from_package_dir(path.resolve().parent)
        return _from_package_dir(path)
    except Exception:
        return None


def _from_script(script_file):
    try:
        here = Path(str(script_file)).resolve()
    except Exception:
        return None
    for parent in here.parents:
        found = _from_package_dir(parent)
        if found:
            return found
        for folder in ("src", "lib"):
            if _has_r2m(parent / folder):
                return parent / folder
    return None


def _from_dev_repo():
    try:
        if _has_r2m(DEV_SRC):
            return DEV_SRC.resolve()
    except Exception:
        return None
    return None


def _version_key(name):
    parts = []
    for bit in name.split("."):
        try:
            parts.append((0, int(bit)))
        except ValueError:
            parts.append((1, bit))
    return parts


def _from_yak_install():
    roots = []
    for key in ("APPDATA", "LOCALAPPDATA"):
        base = str(os.environ.get(key) or "").strip()
        if base:
            roots.append(
                Path(base) / "McNeel" / "Rhinoceros" / "packages" / "8.0" / YAK_PACKAGE
            )
    found = []
    for root in roots:
        try:
            if not root.is_dir():
                continue
            for version_dir in root.iterdir():
                if not version_dir.is_dir():
                    continue
                hit = _from_package_dir(version_dir)
                if hit:
                    found.append((version_dir.name, hit))
        except Exception:
            continue
    if not found:
        return None
    found.sort(key=lambda item: _version_key(item[0]))
    return found[-1][1]


def _plugin_rhps():
    paths = []
    try:
        import Rhino
        from System import Guid
    except Exception:
        return paths
    try:
        paths.append(Rhino.PlugIns.PlugIn.PathFromId(Guid(PLUGIN_ID)))
    except Exception:
        pass
    try:
        paths.append(Rhino.PlugIns.PlugIn.PathFromName(PLUGIN_NAME))
    except Exception:
        pass
    return paths


def _r2m_src():
    hit = _from_script(__file__)
    if hit:
        return hit
    hit = _from_dev_repo()
    if hit:
        return hit
    for rhp in _plugin_rhps():
        hit = _from_rhp(rhp)
        if hit:
            return hit
    hit = _from_yak_install()
    if hit:
        return hit
    raise RuntimeError("找不到 loopflow_r2m 套件（src 或 lib）。")


_SRC = str(_r2m_src())
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

_pkg = Path(_SRC).parent
for _vendor in (_pkg / "vendor" / "py39", _pkg / ".vendor" / "py39"):
    if _vendor.is_dir():
        _vendor_s = str(_vendor)
        if _vendor_s not in sys.path:
            sys.path.insert(0, _vendor_s)
        break

for _name in list(sys.modules):
    if _name == "loopflow_r2m" or _name.startswith("loopflow_r2m."):
        del sys.modules[_name]

import scriptcontext as sc

from loopflow_r2m.rhino.command_inbound import run_rminbound  # noqa: E402

if sc.doc is None:
    raise SystemExit("Open a Rhino document first.")
run_rminbound(sc.doc)
