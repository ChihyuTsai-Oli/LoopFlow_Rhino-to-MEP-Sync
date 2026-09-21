import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.ifc_read import (
    inbound_layer_color,
    inbound_layer_path,
    inbound_object_name,
    inspect_inbound_ifc,
    should_warn_inbound_count,
)
from loopflow_r2m.names import INBOUND_LAYER_ROOT
from loopflow_r2m.vendor import ensure_vendor

PIPE = Path(__file__).resolve().parents[1] / "fixtures" / "spike" / "R2M_spike_pipe.ifc"


def _load_ifcopenshell():
    try:
        ensure_vendor()
        import ifcopenshell  # noqa: F401

        return True
    except Exception:
        return False


SKIP_IFC = not _load_ifcopenshell()
SKIP_REASON = "IfcOpenShell／numpy 無法在系統 Python 載入（預期；Rhino 內有 numpy）"


class InboundReadTests(unittest.TestCase):
    def test_object_name_and_layer(self):
        self.assertEqual(
            inbound_object_name("IfcPipeSegment", "abc"), "IfcPipeSegment:abc"
        )
        self.assertEqual(
            inbound_layer_path("IfcPipeSegment"),
            "%s::IfcPipeSegment" % INBOUND_LAYER_ROOT,
        )
        color = inbound_layer_color("IfcPipeSegment")
        self.assertEqual(len(color), 3)
        self.assertEqual(inbound_layer_color("IfcPipeSegment"), color)
        self.assertNotEqual(color, inbound_layer_color("IfcDuctSegment"))

    def test_count_warning_unset(self):
        self.assertFalse(should_warn_inbound_count(5000, None))
        self.assertFalse(should_warn_inbound_count(5000, ""))
        self.assertFalse(should_warn_inbound_count(10, 0))
        self.assertFalse(should_warn_inbound_count(10, 10))
        self.assertTrue(should_warn_inbound_count(11, 10))

    @unittest.skipIf(SKIP_IFC, SKIP_REASON)
    def test_inspect_spike_pipe(self):
        report = inspect_inbound_ifc(PIPE)
        self.assertEqual(report["schema"], "IFC4")
        self.assertGreaterEqual(len(report["candidates"]), 1)
        self.assertIn("IfcPipeSegment", report["source"])

    def test_missing_file_stops(self):
        if SKIP_IFC:
            self.skipTest(SKIP_REASON)
        with tempfile.TemporaryDirectory() as folder:
            missing = Path(folder) / "no.ifc"
            with self.assertRaises(R2MStop):
                inspect_inbound_ifc(missing)


if __name__ == "__main__":
    unittest.main()
