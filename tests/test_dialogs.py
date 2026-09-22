import unittest

from tests import SRC  # noqa: F401

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.rhino.dialogs import _collect_choice, _placeholder, _resolve_layer_type


class ResolveLayerTypeTests(unittest.TestCase):
    def test_blank_and_placeholder_are_proxy(self):
        self.assertEqual(_resolve_layer_type(None), "IfcBuildingElementProxy")
        self.assertEqual(_resolve_layer_type(""), "IfcBuildingElementProxy")
        self.assertEqual(_resolve_layer_type(_placeholder()), "IfcBuildingElementProxy")

    def test_explicit_wall(self):
        self.assertEqual(_resolve_layer_type("IfcWall"), "IfcWall")

    def test_unknown_type_stops(self):
        with self.assertRaises(R2MStop):
            _resolve_layer_type("IfcBogus")


class CollectChoiceTests(unittest.TestCase):
    def test_checked_blank_type_is_proxy(self):
        result = _collect_choice(
            "",
            [("Wall", True, _placeholder())],
            {"brep": True},
            "medium",
        )
        self.assertEqual(result["layer_paths"], ["Wall"])
        self.assertEqual(result["layer_type_map"]["Wall"], "IfcBuildingElementProxy")

    def test_checked_wall_keeps_type(self):
        result = _collect_choice(
            "",
            [("Wall", True, "IfcWall")],
            {"brep": True},
            "medium",
        )
        self.assertEqual(result["layer_type_map"]["Wall"], "IfcWall")

    def test_unchecked_not_exported(self):
        with self.assertRaises(R2MStop):
            _collect_choice("", [("Wall", False, "IfcWall")], {"brep": True}, "medium")


if __name__ == "__main__":
    unittest.main()
