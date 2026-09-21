import unittest

from tests import SRC  # noqa: F401

from loopflow_r2m.layers import layer_is_excluded


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


if __name__ == "__main__":
    unittest.main()
