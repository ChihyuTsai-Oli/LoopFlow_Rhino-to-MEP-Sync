import json
import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.config import (
    ConfigError,
    default_config,
    has_saved_panel,
    load_config,
    panel_for,
    save_config,
    set_panel,
)
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
        self.assertEqual(data["panels"], {})
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
            self.assertFalse((Path(folder) / "config.json.tmp").exists())

    def test_unknown_schema_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text('{"schema_version": "99"}\n', encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)

    def test_panels_isolated_by_filename(self):
        data = default_config("A.3dm")
        set_panel(
            data,
            "A.3dm",
            {
                "exclude_token": "//",
                "layer_paths": ["WALL"],
                "layer_type_map": {"WALL": "IfcWall", "CEILING": "IfcCovering"},
                "geom": {"brep": True},
                "mesh_density": "fine",
            },
        )
        set_panel(
            data,
            "B.3dm",
            {
                "exclude_token": "",
                "layer_paths": ["SLAB"],
                "layer_type_map": {"SLAB": "IfcSlab"},
                "geom": {"mesh": False},
                "mesh_density": "coarse",
            },
        )
        a = panel_for(data, "A.3dm")
        b = panel_for(data, "B.3dm")
        self.assertEqual(a["layer_paths"], ["WALL"])
        self.assertEqual(a["layer_type_map"]["WALL"], "IfcWall")
        self.assertEqual(a["mesh_density"], "fine")
        self.assertEqual(b["layer_paths"], ["SLAB"])
        self.assertEqual(b["layer_type_map"]["SLAB"], "IfcSlab")
        self.assertEqual(b["mesh_density"], "coarse")
        self.assertEqual(data["document_name"], "B.3dm")
        self.assertEqual(data["layer_type_map"]["SLAB"], "IfcSlab")

    def test_load_missing_panel_for_other_file(self):
        data = default_config("A.3dm")
        set_panel(
            data,
            "A.3dm",
            {
                "layer_paths": ["WALL"],
                "layer_type_map": {"WALL": "IfcWall"},
            },
        )
        self.assertTrue(has_saved_panel(data, "A.3dm"))
        self.assertFalse(has_saved_panel(data, "B.3dm"))
        empty = panel_for(data, "B.3dm")
        self.assertEqual(empty["layer_paths"], [])
        self.assertEqual(empty["layer_type_map"], {})

    def test_legacy_top_level_only_matches_same_filename(self):
        data = default_config("A.3dm")
        data["layer_selection"] = {
            "exclude_token": "//",
            "layer_paths": ["WALL"],
            "geom": {"brep": True},
        }
        data["layer_type_map"] = {"WALL": "IfcWall"}
        self.assertTrue(has_saved_panel(data, "A.3dm"))
        self.assertFalse(has_saved_panel(data, "B.3dm"))
        self.assertEqual(panel_for(data, "A.3dm")["layer_paths"], ["WALL"])
        self.assertEqual(panel_for(data, "B.3dm")["layer_paths"], [])

    def test_missing_panels_key_loads(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            data = default_config("A.3dm")
            del data["panels"]
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            loaded = load_config(path)
            self.assertEqual(loaded["panels"], {})


if __name__ == "__main__":
    unittest.main()
