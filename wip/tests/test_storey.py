import unittest

from tests import SRC  # noqa: F401

from loopflow_r2m.storey import (
    STATUS_ABOVE,
    STATUS_BELOW,
    STATUS_DUPLICATE_FL,
    STATUS_INVALID_TOP,
    STATUS_MISSING_TOP,
    STATUS_NO_STOREYS,
    STATUS_OK,
    Storey,
    assign_storey,
)


class StoreyTests(unittest.TestCase):
    def test_single_storey_ceiling_and_wall(self):
        storeys = [Storey("L1", 0.0)]
        self.assertEqual(assign_storey(0.0, storeys, 290.0).name, "L1")
        self.assertEqual(assign_storey(280.0, storeys, 290.0).name, "L1")
        self.assertEqual(assign_storey(289.9, storeys, 290.0).status, STATUS_OK)

    def test_lower_inclusive_upper_exclusive(self):
        storeys = [Storey("L1", 0.0), Storey("L2", 300.0)]
        self.assertEqual(assign_storey(299.9, storeys, 600.0).name, "L1")
        self.assertEqual(assign_storey(300.0, storeys, 600.0).name, "L2")

    def test_below_and_above_are_not_guessed(self):
        storeys = [Storey("L1", 0.0)]
        self.assertEqual(assign_storey(-1.0, storeys, 290.0).status, STATUS_BELOW)
        self.assertEqual(assign_storey(290.0, storeys, 290.0).status, STATUS_ABOVE)

    def test_missing_or_invalid_bounds(self):
        self.assertEqual(assign_storey(10, [], 100).status, STATUS_NO_STOREYS)
        self.assertEqual(assign_storey(10, [Storey("L1", 0.0)], None).status, STATUS_MISSING_TOP)
        self.assertEqual(assign_storey(10, [Storey("L1", 0.0)], 0.0).status, STATUS_INVALID_TOP)
        dup = [Storey("A", 0.0), Storey("B", 0.0)]
        self.assertEqual(assign_storey(10, dup, 100.0).status, STATUS_DUPLICATE_FL)

    def test_slab_and_foundation(self):
        storeys = [Storey("L1", 0.0), Storey("L2", 300.0)]
        self.assertEqual(assign_storey(0.0, storeys, 600.0).name, "L1")
        self.assertEqual(assign_storey(299.0, storeys, 600.0).name, "L1")
        self.assertEqual(assign_storey(-50.0, storeys, 600.0).status, STATUS_BELOW)

    def test_tall_wall_uses_bottom(self):
        storeys = [Storey("L1", 0.0), Storey("L2", 300.0)]
        self.assertEqual(assign_storey(0.0, storeys, 600.0).name, "L1")

    def test_highest_storey_uses_top_bound(self):
        storeys = [Storey("L1", 0.0), Storey("L2", 300.0)]
        self.assertEqual(assign_storey(300.0, storeys, 600.0).name, "L2")
        self.assertEqual(assign_storey(599.9, storeys, 600.0).name, "L2")
        self.assertEqual(assign_storey(600.0, storeys, 600.0).status, STATUS_ABOVE)


if __name__ == "__main__":
    unittest.main()
