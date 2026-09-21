import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.logutil import append_log
from loopflow_r2m.publish import atomic_replace


class PublishTests(unittest.TestCase):
    def test_atomic_replace_overwrites_last_good(self):
        with tempfile.TemporaryDirectory() as folder:
            pending = Path(folder) / "R2M.pending.ifc"
            last_good = Path(folder) / "R2M.ifc"
            pending.write_text("NEW", encoding="utf-8")
            last_good.write_text("OLD", encoding="utf-8")
            atomic_replace(pending, last_good)
            self.assertEqual(last_good.read_text(encoding="utf-8"), "NEW")
            self.assertFalse(pending.exists())

    def test_missing_pending_leaves_last_good(self):
        with tempfile.TemporaryDirectory() as folder:
            pending = Path(folder) / "R2M.pending.ifc"
            last_good = Path(folder) / "R2M.ifc"
            last_good.write_text("OLD", encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                atomic_replace(pending, last_good)
            self.assertEqual(last_good.read_text(encoding="utf-8"), "OLD")

    def test_append_log_writes_utf8_line(self):
        with tempfile.TemporaryDirectory() as folder:
            log_path = Path(folder) / "r2m.log"
            append_log(log_path, "INFO", "RMModels", "start")
            text = log_path.read_text(encoding="utf-8")
            self.assertIn("INFO | RMModels | start", text)


if __name__ == "__main__":
    unittest.main()
