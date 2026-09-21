import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.guid import compress_guid
from loopflow_r2m.ifc_validate import ValidateError, validate_models_ifc
from loopflow_r2m.ifc_write import ExportMeta, ExportProduct, ExportStorey
from loopflow_r2m.publish import publish_models
from loopflow_r2m.vendor import ensure_vendor


def _load_ifcopenshell():
    try:
        ensure_vendor()
        import ifcopenshell  # noqa: F401
        import ifcopenshell.template  # noqa: F401
        return True
    except Exception:
        return False


SKIP_IFC = not _load_ifcopenshell()
SKIP_REASON = "IfcOpenShell／numpy 無法在系統 Python 載入（預期；Rhino 內有 numpy）"


def _triangle(z=0.0):
    return (
        [(0.0, 0.0, z), (4.0, 0.0, z), (0.0, 4.0, z)],
        [(0, 1, 2)],
    )


class IfcPublishTests(unittest.TestCase):
    @unittest.skipIf(SKIP_IFC, SKIP_REASON)
    def test_write_validate_and_replace(self):
        verts, faces = _triangle(0.0)
        ceiling, ceiling_faces = _triangle(2.8)
        products = [
            ExportProduct(
                "IfcWall",
                compress_guid("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"),
                "wall",
                "L1",
                verts,
                faces,
            ),
            ExportProduct(
                "IfcCovering",
                compress_guid("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"),
                "cover",
                "L1",
                ceiling,
                ceiling_faces,
            ),
        ]
        meta = ExportMeta("R2M.ifc", "Tower", "Site", "Building", "0.0.0-dev")
        storeys = [ExportStorey("L1", 0.0)]
        with tempfile.TemporaryDirectory() as folder:
            pending = Path(folder) / "R2M.pending.ifc"
            last_good = Path(folder) / "R2M.ifc"
            last_good.write_text("OLD", encoding="utf-8")
            report = publish_models(pending, last_good, meta, storeys, products)
            self.assertFalse(pending.exists())
            self.assertTrue(last_good.is_file())
            self.assertNotEqual(last_good.read_text(encoding="utf-8"), "OLD")
            self.assertEqual(report["schema"], "IFC4")
            self.assertEqual(report["elements"], 2)
            self.assertEqual(report["storeys"], 1)

    @unittest.skipIf(SKIP_IFC, SKIP_REASON)
    def test_invalid_pending_keeps_last_good(self):
        with tempfile.TemporaryDirectory() as folder:
            pending = Path(folder) / "R2M.pending.ifc"
            last_good = Path(folder) / "R2M.ifc"
            last_good.write_text("OLD", encoding="utf-8")
            pending.write_text("NOT IFC", encoding="utf-8")
            with self.assertRaises(ValidateError):
                validate_models_ifc(pending, 1)
            self.assertEqual(last_good.read_text(encoding="utf-8"), "OLD")
            self.assertTrue(pending.exists())


if __name__ == "__main__":
    unittest.main()
