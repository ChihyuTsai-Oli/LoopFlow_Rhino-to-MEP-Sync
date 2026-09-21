#!/usr/bin/env python3
"""相容入口：只重產決策表 HTML（不改 Markdown）。

不帶參數時直接處理 `docs/前期規劃/資料生態決策表.md`。
要連同多數決一起重跑，請直接用 `fill_decision_table.py`。
"""
from pathlib import Path
import sys

from fill_decision_table import main

if __name__ == "__main__":
    if len(sys.argv) == 1:
        root = Path(__file__).resolve().parents[1]
        md = root / "docs" / "前期規劃" / "資料生態決策表.md"
        sys.argv = [sys.argv[0], str(md), "--html-only", "--title", "R2M 資料生態決策表"]
    elif "--html-only" not in sys.argv:
        sys.argv.append("--html-only")
    raise SystemExit(main())
