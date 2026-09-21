# RMModels — 開發期從 ScriptEditor 執行。
# 介面英文。未存檔則停。

from __future__ import annotations

import sys
from pathlib import Path

WIP = Path(__file__).resolve().parents[1]
SRC = WIP / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

VENDOR = WIP / ".vendor" / "py39"
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

import scriptcontext as sc

from loopflow_r2m.rhino.command_models import run_rmmodels

if sc.doc is None:
    raise SystemExit("Open a saved Rhino document first.")
result = run_rmmodels(sc.doc)
print(result)
