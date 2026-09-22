# RMInbound — 開發期從 ScriptEditor 執行。
# 介面英文。不要求已存檔。不寫檔、不掛載。

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

# ScriptEditor 會快取已 import 的套件；每次跑都丟掉，才會讀到磁碟上的新碼。
for _name in list(sys.modules):
    if _name == "loopflow_r2m" or _name.startswith("loopflow_r2m."):
        del sys.modules[_name]

import scriptcontext as sc

from loopflow_r2m.rhino.command_inbound import run_rminbound

if sc.doc is None:
    raise SystemExit("Open a Rhino document first.")
result = run_rminbound(sc.doc)
print(result)
