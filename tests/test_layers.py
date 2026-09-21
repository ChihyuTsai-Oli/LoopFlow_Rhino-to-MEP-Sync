import unittest

from tests import SRC  # noqa: F401

from loopflow_r2m.layers import is_storey_layer_path, layer_is_excluded


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
        self.assertTrue(is_storey_layer_path("R2M_Storey"))
        self.assertTrue(is_storey_layer_path("Default::R2M_Storey"))
        self.assertFalse(is_storey_layer_path("R2M_Storey_Extra"))
        self.assertFalse(is_storey_layer_path("Wall"))


if __name__ == "__main__":
    unittest.main()
