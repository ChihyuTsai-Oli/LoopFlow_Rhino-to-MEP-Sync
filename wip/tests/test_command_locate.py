"""command_locate、vendor、公開 docs 路徑。"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.paths import public_docs_dir
from loopflow_r2m.vendor import vendor_dir

PACKAGING = Path(__file__).resolve().parents[1] / "packaging"
if str(PACKAGING) not in sys.path:
    sys.path.insert(0, str(PACKAGING))

from command_locate import (  # noqa: E402
    COMMANDS,
    PLUGIN_ID,
    from_dev_repo,
    from_package_dir,
    resolve_r2m_src,
    wrapper_source,
)


class LocateTests(unittest.TestCase):
    def test_dev_repo_points_at_wip_src(self):
        found = from_dev_repo()
        self.assertIsNotNone(found)
        self.assertTrue((found / "loopflow_r2m" / "__init__.py").is_file())

    def test_resolve_prefers_script_then_dev(self):
        src = resolve_r2m_src(__file__)
        self.assertTrue((src / "loopflow_r2m" / "__init__.py").is_file())

    def test_from_package_dir_lib(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            lib = root / "lib" / "loopflow_r2m"
            lib.mkdir(parents=True)
            (lib / "__init__.py").write_text("", encoding="utf-8")
            hit = from_package_dir(root)
            self.assertEqual(hit, (root / "lib").resolve())

    def test_four_wrappers(self):
        self.assertEqual(len(COMMANDS), 4)
        names = [item[0] for item in COMMANDS]
        self.assertEqual(names, ["RMOpen", "RMStorey", "RMModels", "RMInbound"])
        text = wrapper_source("RMOpen", "command_open", "run_rmopen")
        self.assertIn(PLUGIN_ID, text)
        self.assertIn("run_rmopen", text)
        self.assertIn("#! python 3", text)


class VendorTests(unittest.TestCase):
    def test_vendor_dir_exists_in_dev(self):
        path = vendor_dir()
        self.assertTrue(path.is_dir(), path)
        self.assertEqual(path.name, "py39")


class PublicDocsTests(unittest.TestCase):
    def test_repo_docs_from_command_open_layout(self):
        repo = Path(__file__).resolve().parents[2]
        anchor = repo / "wip" / "src" / "loopflow_r2m" / "rhino" / "command_open.py"
        self.assertTrue(anchor.is_file())
        docs = public_docs_dir(anchor)
        self.assertEqual(docs, repo / "docs")
        self.assertTrue((docs / "README.md").is_file())

    def test_yak_docs_next_to_lib(self):
        with tempfile.TemporaryDirectory() as raw:
            pkg = Path(raw)
            anchor = pkg / "lib" / "loopflow_r2m" / "rhino" / "command_open.py"
            anchor.parent.mkdir(parents=True)
            anchor.write_text("", encoding="utf-8")
            docs = pkg / "docs"
            docs.mkdir()
            (docs / "README.md").write_text("ok", encoding="utf-8")
            self.assertEqual(public_docs_dir(anchor), docs)


if __name__ == "__main__":
    unittest.main()
