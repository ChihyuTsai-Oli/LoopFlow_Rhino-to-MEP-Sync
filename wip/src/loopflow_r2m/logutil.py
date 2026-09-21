"""r2m.log：ISO8601 | 等級 | 指令 | 訊息。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def append_log(log_path, level, command, message):
    """append 一行 UTF-8。"""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")
    line = "%s | %s | %s | %s\n" % (stamp, level, command, message)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
