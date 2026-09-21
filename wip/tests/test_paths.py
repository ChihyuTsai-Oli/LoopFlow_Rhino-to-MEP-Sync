import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.names import CONFIG_FOLDER, CONFIG_PRODUCT, MODELS_IFC_NAME, PENDING_IFC_NAME
from loopflow_r2m.paths import config_paths, config_root


class PathTests(unittest.TestCase):
    def test_config_root_sits_beside_the_document(self):
        with tempfile.TemporaryDirectory() as folder:
            document = Path(folder) / "Tower_rev03.3dm"
            root = config_root(document)
            self.assertEqual(root, Path(folder) / CONFIG_FOLDER / CONFIG_PRODUCT)
            paths = config_paths(document)
            self.assertEqual(paths["ifc"].name, MODELS_IFC_NAME)
            self.assertEqual(paths["pending"].name, PENDING_IFC_NAME)
            self.assertEqual(paths["ifc"].parent, paths["pending"].parent)
            self.assertEqual(paths["config"].parent, root)


if __name__ == "__main__":
    unittest.main()
