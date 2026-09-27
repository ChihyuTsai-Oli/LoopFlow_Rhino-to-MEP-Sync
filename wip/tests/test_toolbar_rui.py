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

    def test_user_icons_embedded(self):
        xml = ET.tostring(self.root.find("icons"), encoding="unicode")
        self.assertEqual(len(list(self.root.find("icons"))), 5)
        self.assertIn("1769.854,1409.23", xml)
        self.assertIn("M15,7L4,7C3.451,7", xml)
        self.assertIn("M17.858,89.747", xml)
        self.assertIn("M2.292,2.112L4.535,2.112", xml)
        self.assertIn("M5.612,5.687L1.215,5.687", xml)
        bar = self.root.find("tool_bars").find("tool_bar")
        self.assertTrue((bar.get("bitmap_id") or "").strip())

    def test_no_spacers(self):
        items = list(self.root.find("tool_bars").find("tool_bar"))
        buttons = [el for el in items if el.tag == "tool_bar_item"]
        self.assertEqual(len(buttons), 4)
        self.assertFalse(any(el.get("button_style") == "spacer" for el in buttons))

    def test_group_title(self):
        text = self.root.find("tool_bar_groups").find("tool_bar_group").find("text")
        self.assertEqual(text.find("locale_1033").text, "LoopFlow R2M")

    def test_source_svgs_not_kept(self):
        folder = RUI.parent
        leftover = [
            name
            for name in (
                "LoopFlow_R2M.svg",
                "R2M_Open.svg",
                "R2M_Storey.svg",
                "R2M_Models.svg",
                "R2M_Inbound.svg",
            )
            if (folder / name).exists()
        ]
        self.assertEqual(leftover, [])


if __name__ == "__main__":
    unittest.main()
