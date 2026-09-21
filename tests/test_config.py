import json
import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.config import ConfigError, default_config, load_config, save_config
from loopflow_r2m.names import PRODUCER, SCHEMA_VERSION


class ConfigTests(unittest.TestCase):
    def test_default_names_follow_filename(self):
        data = default_config("Tower_rev03.3dm")
        self.assertEqual(data["schema_version"], SCHEMA_VERSION)
        self.assertEqual(data["producer"], PRODUCER)
        self.assertEqual(data["project_name"], "Tower_rev03")
        self.assertEqual(data["site_name"], "Tower_rev03")
        self.assertEqual(data["building_name"], "Tower_rev03")
        self.assertEqual(data["mesh_density"], "medium")
        self.assertIsNone(data["last_export"])
        self.assertIsNone(data["inbound_count_warning"])

    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            original = default_config("A.3dm", product_version="0.0.0-dev")
            original["project_name"] = "A Tower"
            save_config(path, original)
            loaded = load_config(path)
            self.assertEqual(loaded["project_name"], "A Tower")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["producer"], PRODUCER)

    def test_unknown_schema_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text('{"schema_version": "99"}\n', encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
