# -*- coding: utf-8 -*-
"""寫出內嵌查找邏輯的四支正式指令腳本。"""
from __future__ import annotations

from pathlib import Path

from command_locate import COMMANDS, wrapper_source

HERE = Path(__file__).resolve().parent
OUT = HERE / "commands"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for official, module, runner in COMMANDS:
        path = OUT / f"{official}.py"
        path.write_text(
            wrapper_source(official, module, runner),
            encoding="utf-8",
            newline="\n",
        )
        print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
