import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.config import default_config, save_config
from loopflow_r2m.health import health_lines
from loopflow_r2m.paths import config_paths


class HealthTests(unittest.TestCase):
    def test_missing_sidecar(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = config_paths(Path(folder) / "A.3dm")
            lines = "\n".join(health_lines(paths))
            self.assertIn("config.json: missing", lines)
            self.assertIn("last-good IFC: missing", lines)

    def test_last_export_summary(self):
        with tempfile.TemporaryDirectory() as folder:
            document = Path(folder) / "A.3dm"
            paths = config_paths(document)
            data = default_config("A.3dm")
            data["last_export"] = {
                "timestamp": "2026-09-21T00:00:00+00:00",
                "ifc_path": "models/R2M.ifc",
                "object_count": 2,
                "storey_count": 1,
            }
            save_config(paths["config"], data)
            paths["ifc"].parent.mkdir(parents=True, exist_ok=True)
            paths["ifc"].write_text("IFC", encoding="utf-8")
            lines = "\n".join(health_lines(paths))
            self.assertIn("last export: 2 objects, 1 storeys", lines)
            self.assertIn("ifc size:", lines)


if __name__ == "__main__":
    unittest.main()
