import unittest

from tests import SRC  # noqa: F401

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.names import (
    DEFAULT_IFC_TYPE,
    LEGACY_DEFAULT_IFC_TYPE,
    ifc_type_choices,
)
from loopflow_r2m.rhino.dialogs import (
    _collect_choice,
    _placeholder,
    _resolve_layer_type,
    _snapshot_choice,
    _type_index,
)


class ResolveLayerTypeTests(unittest.TestCase):
    def test_blank_and_placeholder_are_plate(self):
        self.assertEqual(DEFAULT_IFC_TYPE, "IfcPlate")
        self.assertEqual(_resolve_layer_type(None), DEFAULT_IFC_TYPE)
        self.assertEqual(_resolve_layer_type(""), DEFAULT_IFC_TYPE)
        self.assertEqual(_resolve_layer_type(_placeholder()), DEFAULT_IFC_TYPE)

    def test_explicit_wall_and_covering_kept(self):
        self.assertEqual(_resolve_layer_type("IfcWall"), "IfcWall")
        self.assertEqual(_resolve_layer_type("IfcCovering"), "IfcCovering")

    def test_explicit_proxy_kept(self):
        self.assertEqual(_resolve_layer_type(LEGACY_DEFAULT_IFC_TYPE), LEGACY_DEFAULT_IFC_TYPE)

    def test_unknown_type_stops(self):
        with self.assertRaises(R2MStop):
            _resolve_layer_type("IfcBogus")


class TypeChoiceTests(unittest.TestCase):
    def test_dropdown_starts_with_plate(self):
        choices = ifc_type_choices()
        self.assertEqual(choices[0], DEFAULT_IFC_TYPE)
        self.assertEqual(choices[0], "IfcPlate")
        self.assertNotIn("(reference)", choices)
        self.assertIn(LEGACY_DEFAULT_IFC_TYPE, choices)
        self.assertEqual(_type_index(choices, None), 0)
        self.assertEqual(_type_index(choices, _placeholder()), 0)
        self.assertEqual(_type_index(choices, LEGACY_DEFAULT_IFC_TYPE), 0)
        self.assertEqual(_type_index(choices, "IfcWall"), choices.index("IfcWall"))
        self.assertEqual(_type_index(choices, "IfcCovering"), choices.index("IfcCovering"))


class CollectChoiceTests(unittest.TestCase):
    def test_checked_blank_type_is_plate(self):
        result = _collect_choice(
            "",
            [("Wall", True, _placeholder())],
            {"brep": True},
            "medium",
        )
        self.assertEqual(result["layer_paths"], ["Wall"])
        self.assertEqual(result["layer_type_map"]["Wall"], DEFAULT_IFC_TYPE)

    def test_checked_wall_keeps_type(self):
        result = _collect_choice(
            "",
            [("Wall", True, "IfcWall")],
            {"brep": True},
            "medium",
        )
        self.assertEqual(result["layer_type_map"]["Wall"], "IfcWall")

    def test_checked_proxy_keeps_type(self):
        result = _collect_choice(
            "",
            [("Misc", True, LEGACY_DEFAULT_IFC_TYPE)],
            {"brep": True},
            "medium",
        )
        self.assertEqual(result["layer_type_map"]["Misc"], LEGACY_DEFAULT_IFC_TYPE)

    def test_unchecked_not_exported(self):
        with self.assertRaises(R2MStop):
            _collect_choice("", [("Wall", False, "IfcWall")], {"brep": True}, "medium")

    def test_snapshot_keeps_unchecked_types(self):
        result = _snapshot_choice(
            "//",
            [("Wall", False, "IfcWall"), ("Slab", True, None)],
            {"brep": False},
            "fine",
        )
        self.assertEqual(result["layer_paths"], ["Slab"])
        self.assertEqual(result["layer_type_map"]["Wall"], "IfcWall")
        self.assertEqual(result["layer_type_map"]["Slab"], DEFAULT_IFC_TYPE)
        self.assertEqual(result["mesh_density"], "fine")


if __name__ == "__main__":
    unittest.main()
