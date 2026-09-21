import unittest

from tests import SRC  # noqa: F401

from loopflow_r2m.rhino.collect import default_geom_enabled


class CollectDefaultsTests(unittest.TestCase):
    def test_point_and_curve_off_by_default(self):
        enabled = default_geom_enabled()
        self.assertFalse(enabled["point"])
        self.assertFalse(enabled["curve"])
        self.assertTrue(enabled["brep"])
        self.assertTrue(enabled["mesh"])

    def test_saved_geom_overrides_defaults(self):
        enabled = default_geom_enabled({"curve": True, "brep": False})
        self.assertTrue(enabled["curve"])
        self.assertFalse(enabled["brep"])
        self.assertTrue(enabled["mesh"])


if __name__ == "__main__":
    unittest.main()
