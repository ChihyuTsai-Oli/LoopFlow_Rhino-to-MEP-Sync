import unittest

from tests import SRC  # noqa: F401

from loopflow_r2m.layers import (
    filter_leaf_layer_rows,
    is_leaf_layer_path,
    is_r2m_system_layer_path,
    is_storey_layer_path,
    layer_is_excluded,
)


class LayerTests(unittest.TestCase):
    def test_default_token_excludes(self):
        self.assertTrue(layer_is_excluded("Project//Finish/Paint"))
        self.assertFalse(layer_is_excluded("Project/Wall"))

    def test_blank_token_never_excludes(self):
        self.assertFalse(layer_is_excluded("Project//Finish", ""))
        self.assertFalse(layer_is_excluded("Project//Finish", None))

    def test_custom_token(self):
        self.assertTrue(layer_is_excluded("A::Skip::B", "::Skip::"))
        self.assertFalse(layer_is_excluded("A::Keep::B", "::Skip::"))

    def test_whitespace_token_never_excludes(self):
        self.assertFalse(layer_is_excluded("Project//Finish", "  "))

    def test_storey_layer_path(self):
        self.assertTrue(is_storey_layer_path("R2M::Storey"))
        self.assertTrue(is_storey_layer_path("Default::R2M::Storey"))
        self.assertFalse(is_storey_layer_path("R2M::Storey_Extra"))
        self.assertFalse(is_storey_layer_path("R2M"))
        self.assertFalse(is_storey_layer_path("Wall"))

    def test_r2m_tree_never_exports(self):
        self.assertTrue(is_r2m_system_layer_path("R2M"))
        self.assertTrue(is_r2m_system_layer_path("R2M::Storey"))
        self.assertTrue(is_r2m_system_layer_path("R2M::Storey::Old"))
        self.assertFalse(is_r2m_system_layer_path("R2M_Inbound"))
        self.assertFalse(is_r2m_system_layer_path("Wall"))

    def test_leaf_layer_paths(self):
        paths = ["M2D", "M2D::Plan", "M2D::Plan::MP_2_A-WALL", "M2D::Plan::MP_2_CEILING"]
        self.assertFalse(is_leaf_layer_path("M2D", paths))
        self.assertFalse(is_leaf_layer_path("M2D::Plan", paths))
        self.assertTrue(is_leaf_layer_path("M2D::Plan::MP_2_A-WALL", paths))
        self.assertTrue(is_leaf_layer_path("Layout", ["Layout", "M2D"]))

    def test_filter_leaf_rows_drops_parents(self):
        rows = [
            {"path": "M2D", "count": 1},
            {"path": "M2D::Plan", "count": 0},
            {"path": "M2D::Plan::WALL", "count": 4},
        ]
        leaves = filter_leaf_layer_rows(rows)
        self.assertEqual([row["path"] for row in leaves], ["M2D::Plan::WALL"])


if __name__ == "__main__":
    unittest.main()
