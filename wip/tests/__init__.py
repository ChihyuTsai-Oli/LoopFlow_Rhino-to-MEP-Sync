"""把 wip/src 加進 path，讓測試不需安裝套件。"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
src_text = str(SRC)
if src_text not in sys.path:
    sys.path.insert(0, src_text)
