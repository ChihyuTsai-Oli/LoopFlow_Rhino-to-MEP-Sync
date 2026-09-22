import tempfile
import unittest
from pathlib import Path

from tests import SRC  # noqa: F401

from loopflow_r2m.guid import compress_guid
from loopflow_r2m.ifc_validate import ValidateError, validate_models_ifc
from loopflow_r2m.ifc_write import (
    ExportMeta,
    ExportProduct,
    ExportStorey,
    ordered_storeys,
    relative_vertices,
)
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


class StoreyPlacementTests(unittest.TestCase):
    def test_relative_vertices_keeps_xy(self):
        out = relative_vertices([(1.0, 2.0, 5.0), (0.0, 0.0, 3.18)], 3.18)
        self.assertEqual(out[0][0], 1.0)
        self.assertEqual(out[0][1], 2.0)
        self.assertAlmostEqual(out[0][2], 1.82)
        self.assertAlmostEqual(out[1][2], 0.0)

    def test_export_storey_defaults_frame_to_fl(self):
        row = ExportStorey("1F", 3.2)
        self.assertAlmostEqual(row.elevation_m, 3.2)
        self.assertAlmostEqual(row.frame_z_m, 3.2)

    def test_ordered_storeys_low_to_high(self):
        rows = ordered_storeys(
            [
                ExportStorey("RF", 28.8),
                ExportStorey("B2", -6.4),
                ExportStorey("1F", 0.0),
            ]
        )
        self.assertEqual([item.name for item in rows], ["B2", "1F", "RF"])

    @unittest.skipIf(SKIP_IFC, SKIP_REASON)
    def test_storey_placement_z_matches_elevation(self):
        verts, faces = _triangle(3.2)
        products = [
            ExportProduct(
                "IfcSlab",
                compress_guid("cccccccccccccccccccccccccccccccc"),
                "slab",
                "2F",
                verts,
                faces,
            )
        ]
        meta = ExportMeta("R2M.ifc", "Tower", "Site", "Building", "0.0.0-dev")
        storeys = [
            ExportStorey("2F", 3.2, 3.2),
            ExportStorey("1F", 0.0, 0.0),
        ]
        with tempfile.TemporaryDirectory() as folder:
            pending = Path(folder) / "R2M.pending.ifc"
            last_good = Path(folder) / "R2M.ifc"
            publish_models(pending, last_good, meta, storeys, products)
            import ifcopenshell

            ifc = ifcopenshell.open(str(last_good))
            names = [item.Name for item in ifc.by_type("IfcBuildingStorey")]
            self.assertEqual(names, ["1F", "2F"])
            by_name = {item.Name: item for item in ifc.by_type("IfcBuildingStorey")}
            z2 = float(
                by_name["2F"].ObjectPlacement.RelativePlacement.Location.Coordinates[2]
            )
            self.assertAlmostEqual(z2, 3.2)
            self.assertAlmostEqual(float(by_name["2F"].Elevation), 3.2)
            zs = [
                float(pt[2])
                for listing in ifc.by_type("IfcCartesianPointList3D")
                for pt in listing.CoordList
            ]
            self.assertAlmostEqual(min(zs), 0.0)
            self.assertAlmostEqual(min(zs) + z2, 3.2)

    @unittest.skipIf(SKIP_IFC, SKIP_REASON)
    def test_partial_storey_fl_differs_from_frame_z(self):
        verts, faces = _triangle(2.98)
        products = [
            ExportProduct(
                "IfcWall",
                compress_guid("dddddddddddddddddddddddddddddddd"),
                "wall",
                "11F",
                verts,
                faces,
            )
        ]
        meta = ExportMeta("R2M.ifc", "Partial", "Site", "Building", "0.0.0-dev")
        storeys = [
            ExportStorey("12F", 38.38, 3.18),
            ExportStorey("11F", 35.2, 0.0),
        ]
        with tempfile.TemporaryDirectory() as folder:
            pending = Path(folder) / "R2M.pending.ifc"
            last_good = Path(folder) / "R2M.ifc"
            publish_models(pending, last_good, meta, storeys, products)
            import ifcopenshell

            ifc = ifcopenshell.open(str(last_good))
            by_name = {item.Name: item for item in ifc.by_type("IfcBuildingStorey")}
            names = [item.Name for item in ifc.by_type("IfcBuildingStorey")]
            self.assertEqual(names, ["11F", "12F"])
            z11 = float(
                by_name["11F"].ObjectPlacement.RelativePlacement.Location.Coordinates[2]
            )
            self.assertAlmostEqual(z11, 35.2)
            zs = [
                float(pt[2])
                for listing in ifc.by_type("IfcCartesianPointList3D")
                for pt in listing.CoordList
            ]
            self.assertAlmostEqual(min(zs), 2.98)
            self.assertAlmostEqual(min(zs) + z11, 38.18)


if __name__ == "__main__":
    unittest.main()
