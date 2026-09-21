import importlib.util
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.guid import compress_guid, expand_guid

VENDOR_GUID = (
    Path(__file__).resolve().parents[1] / ".vendor" / "py39" / "ifcopenshell" / "guid.py"
)


class GuidTests(unittest.TestCase):
    def test_n_format_length_and_roundtrip(self):
        hex32 = "2e87ad0f8b4d4c8e9f1a0a1b2c3d4e5f"
        guid = compress_guid(hex32)
        self.assertEqual(len(guid), 22)
        self.assertEqual(expand_guid(guid), hex32)

    def test_accepts_hyphenated_uuid(self):
        dotted = "2E87AD0F-8B4D-4C8E-9F1A-0A1B2C3D4E5F"
        compact = "2e87ad0f8b4d4c8e9f1a0a1b2c3d4e5f"
        self.assertEqual(compress_guid(dotted), compress_guid(compact))

    def test_rejects_bad_length(self):
        with self.assertRaises(ValueError):
            compress_guid("abc")
        with self.assertRaises(ValueError):
            expand_guid("short")

    def test_matches_ifcopenshell_guid_module(self):
        if not VENDOR_GUID.is_file():
            self.skipTest("尚未重建 .vendor/")
        spec = importlib.util.spec_from_file_location("r2m_vendor_guid", VENDOR_GUID)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        hex32 = "0123456789abcdef0123456789abcdef"
        self.assertEqual(compress_guid(hex32), module.compress(hex32))
        self.assertEqual(expand_guid(compress_guid(hex32)), module.expand(module.compress(hex32)))


if __name__ == "__main__":
    unittest.main()
