# RMStorey — 開發期從 ScriptEditor 執行。
# 介面英文。未存檔也可以跑（只是不寫 log）。

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

VENDOR = ROOT / ".vendor" / "py39"
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

import scriptcontext as sc

from loopflow_r2m.rhino.command_storey import run_rmstorey

if sc.doc is None:
    raise SystemExit("Open a Rhino document first.")
result = run_rmstorey(sc.doc)
print(result)
