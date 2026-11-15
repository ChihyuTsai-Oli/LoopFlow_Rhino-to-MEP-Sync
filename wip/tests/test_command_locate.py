"""command_locate、vendor、公開 docs 路徑。"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.paths import PUBLIC_DOCS_URL
from loopflow_r2m.vendor import python_tag, vendor_dir

PACKAGING = Path(__file__).resolve().parents[1] / "packaging"
if str(PACKAGING) not in sys.path:
    sys.path.insert(0, str(PACKAGING))

from command_locate import (  # noqa: E402
    COMMANDS,
    PLUGIN_ID,
    YAK_PACKAGE,
    from_dev_repo,
    from_package_dir,
    from_yak_install,
    package_folders,
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
        self.assertIn(YAK_PACKAGE, text)
        self.assertIn("_rhino_major", text)
        self.assertIn('"9.0"', text)
        self.assertNotIn('packages" / "8.0"', text)

    def _installed_src(self, version_dir: Path) -> Path:
        src = version_dir / "src"
        pkg = src / "loopflow_r2m"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        return src

    def test_package_folders_prefer_running_major(self):
        self.assertEqual(package_folders(9), ("9.0", "8.0"))
        self.assertEqual(package_folders(8), ("8.0", "9.0"))

    def test_yak_install_prefers_running_rhino(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            env = {"APPDATA": str(tmp), "LOCALAPPDATA": str(tmp)}
            base = tmp / "McNeel" / "Rhinoceros" / "packages"
            src8 = self._installed_src(base / "8.0" / YAK_PACKAGE / "1.1.0")
            src9 = self._installed_src(base / "9.0" / YAK_PACKAGE / "1.1.0")
            hit9 = from_yak_install(env, preferred_major=9)
            hit8 = from_yak_install(env, preferred_major=8)
            self.assertEqual(hit9.resolve(), src9.resolve())
            self.assertEqual(hit8.resolve(), src8.resolve())


class VendorTests(unittest.TestCase):
    def test_python_tag_follows_rhino(self):
        self.assertEqual(python_tag((3, 9)), "py39")
        self.assertEqual(python_tag((3, 13)), "py313")
        self.assertEqual(python_tag((3, 11)), "py39")

    def test_vendor_dir_exists_in_dev(self):
        path = vendor_dir((3, 9))
        self.assertTrue(path.is_dir(), path)
        self.assertEqual(path.name, "py39")
        py313 = vendor_dir((3, 13))
        self.assertEqual(py313.name, "py313")
        if py313.is_dir():
            self.assertTrue((py313 / "numpy" / "__init__.py").is_file(), py313)
            self.assertTrue((py313 / "numpy.libs").is_dir(), py313)


class PublicDocsTests(unittest.TestCase):
    def test_open_docs_is_github_repo(self):
        self.assertEqual(
            PUBLIC_DOCS_URL,
            "https://github.com/ChihyuTsai-Oli/LoopFlow_Rhino-to-MEP-Sync",
        )
        self.assertTrue(PUBLIC_DOCS_URL.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
