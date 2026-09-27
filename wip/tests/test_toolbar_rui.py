"""開發期 LoopFlow_R2M.rui 契約：有分組、四顆按鈕、腳本路徑存在。"""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUI = REPO / "wip" / "docs" / "toolbar" / "LoopFlow_R2M.rui"
COMMANDS = REPO / "wip" / "commands"
EXPECTED = (
    "RMOpen.py",
    "RMStorey.py",
    "RMModels.py",
    "RMInbound.py",
)


class ToolbarRuiTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(RUI.is_file(), f"missing {RUI}")
        text = RUI.read_bytes().decode("utf-8-sig")
        self.root = ET.fromstring(text.encode("utf-8"))

    def test_has_toolbar_group(self):
        groups = self.root.find("tool_bar_groups")
        self.assertIsNotNone(groups)
        group = groups.find("tool_bar_group")
        self.assertIsNotNone(group)
        self.assertNotEqual(group.tag, None)
        self.assertIsNone(groups.find("tool_bar_groups"))
        xml = ET.tostring(groups, encoding="unicode")
        self.assertNotIn("<tool_bar_groups />", xml.replace(" ", ""))
        self.assertIn("tool_bar_group", xml)

    def test_four_command_scripts(self):
        scripts = [
            (m.find("script").text or "")
            for m in self.root.find("macros")
        ]
        self.assertEqual(len(scripts), 4)
        joined = "\n".join(scripts)
        for name in EXPECTED:
            self.assertIn(name, joined)
            self.assertTrue((COMMANDS / name).is_file(), name)
            self.assertIn("ScriptEditor", joined)

    def test_product_command_names_not_registered_yet(self):
        scripts = "\n".join(
            (m.find("script").text or "") for m in self.root.find("macros")
        )
        self.assertNotIn("_RMOpen", scripts)
        self.assertIn("RMOpen.py", scripts)

    def test_group_title(self):
        text = self.root.find("tool_bar_groups").find("tool_bar_group").find("text")
        self.assertEqual(text.find("locale_1033").text, "LoopFlow R2M")


if __name__ == "__main__":
    unittest.main()
