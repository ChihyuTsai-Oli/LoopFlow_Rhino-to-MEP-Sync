# -*- coding: utf-8 -*-
"""找出 loopflow_r2m（wip/src 或 yak lib）。

RhinoCode 執行 yak 指令時，會把腳本拷到 `%USERPROFILE%\\.rhinocode\\stage\\`，
`__file__` 不再位於套件目錄。因此還要搜本機 repo 與 Package Manager 安裝位置。
指令 `.py` 必須內嵌同一份邏輯，不能在執行期 import 本檔。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Mapping, Optional

PLUGIN_ID = "814a8439-9948-530a-ad43-69048e85ec1e"
PLUGIN_NAME = "LoopFlow_R2M"
YAK_PACKAGE = "loopflow-r2m"
DEV_SRC = Path(r"E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync") / "wip" / "src"

COMMANDS = (
    ("RMOpen", "command_open", "run_rmopen"),
    ("RMStorey", "command_storey", "run_rmstorey"),
    ("RMModels", "command_models", "run_rmmodels"),
    ("RMInbound", "command_inbound", "run_rminbound"),
)


def has_r2m(root: Path) -> bool:
    try:
        return (root / "loopflow_r2m" / "__init__.py").is_file()
    except Exception:
        return False


def from_package_dir(package_dir: Optional[Path]) -> Optional[Path]:
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
        if has_r2m(candidate):
            return candidate
    return None


def from_rhp(rhp: object) -> Optional[Path]:
    if not rhp:
        return None
    try:
        path = Path(str(rhp))
        if path.is_file():
            return from_package_dir(path.resolve().parent)
        return from_package_dir(path)
    except Exception:
        return None


def from_script(script_file: str) -> Optional[Path]:
    try:
        here = Path(str(script_file)).resolve()
    except Exception:
        return None
    for parent in here.parents:
        found = from_package_dir(parent)
        if found:
            return found
        for folder in ("src", "lib"):
            if has_r2m(parent / folder):
                return parent / folder
    return None


def from_dev_repo() -> Optional[Path]:
    try:
        if has_r2m(DEV_SRC):
            return DEV_SRC.resolve()
    except Exception:
        return None
    return None


def _version_key(name: str):
    parts = []
    for bit in name.split("."):
        try:
            parts.append((0, int(bit)))
        except ValueError:
            parts.append((1, bit))
    return parts


def from_yak_install(environ: Optional[Mapping[str, str]] = None) -> Optional[Path]:
    env = environ if environ is not None else os.environ
    roots = []
    for key in ("APPDATA", "LOCALAPPDATA"):
        base = str(env.get(key) or "").strip()
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
                hit = from_package_dir(version_dir)
                if hit:
                    found.append((version_dir.name, hit))
        except Exception:
            continue
    if not found:
        return None
    found.sort(key=lambda item: _version_key(item[0]))
    return found[-1][1]


def resolve_r2m_src(
    script_file: str,
    environ: Optional[Mapping[str, str]] = None,
    plugin_rhps: Iterable[object] = (),
) -> Path:
    hit = from_script(script_file)
    if hit:
        return hit
    hit = from_dev_repo()
    if hit:
        return hit
    for rhp in plugin_rhps:
        hit = from_rhp(rhp)
        if hit:
            return hit
    hit = from_yak_install(environ)
    if hit:
        return hit
    raise RuntimeError("找不到 loopflow_r2m 套件（src 或 lib）。")


def wrapper_source(official: str, module: str, runner: str) -> str:
    """內嵌查找邏輯的正式指令腳本。RhinoCode 執行時不會帶上本模組。"""
    return '''#! python 3
# -*- coding: utf-8 -*-
"""G02 套件登錄的正式指令 %s。開發期入口仍是 wip/commands/%s.py。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PLUGIN_ID = "814a8439-9948-530a-ad43-69048e85ec1e"
PLUGIN_NAME = "LoopFlow_R2M"
YAK_PACKAGE = "loopflow-r2m"
DEV_SRC = Path(r"E:\\_GitHub\\LoopFlow_Rhino-to-MEP-Sync") / "wip" / "src"


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

from loopflow_r2m.rhino.%s import %s  # noqa: E402

if sc.doc is None:
    raise SystemExit("Open a Rhino document first.")
%s(sc.doc)
''' % (official, official, module, runner, runner)
