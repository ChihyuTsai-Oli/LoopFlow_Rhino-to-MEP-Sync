import unittest

from tests import SRC  # noqa: F401

from loopflow_r2m.storey import (
    STATUS_BELOW,
    STATUS_DUPLICATE_FL,
    STATUS_NO_STOREYS,
    STATUS_OK,
    Frame,
    Storey,
    StoreyPlanError,
    assign_storey,
    build_storey_plan,
)


class AssignStoreyTests(unittest.TestCase):
    def test_single_storey_ceiling_and_wall(self):
        storeys = [Storey("1F", 0.0)]
        self.assertEqual(assign_storey(0.0, storeys).name, "1F")
        self.assertEqual(assign_storey(280.0, storeys).name, "1F")

    def test_lower_inclusive_upper_exclusive(self):
        storeys = [Storey("1F", 0.0), Storey("2F", 300.0)]
        self.assertEqual(assign_storey(299.9, storeys).name, "1F")
        self.assertEqual(assign_storey(300.0, storeys).name, "2F")

    def test_below_lowest_is_not_guessed(self):
        storeys = [Storey("1F", 0.0)]
        self.assertEqual(assign_storey(-1.0, storeys).status, STATUS_BELOW)

    def test_top_storey_has_no_upper_bound(self):
        storeys = [Storey("1F", 0.0), Storey("RF", 300.0)]
        self.assertEqual(assign_storey(300.0, storeys).name, "RF")
        self.assertEqual(assign_storey(99999.0, storeys).name, "RF")

    def test_missing_or_duplicate(self):
        self.assertEqual(assign_storey(10, []).status, STATUS_NO_STOREYS)
        dup = [Storey("A", 0.0), Storey("B", 0.0)]
        self.assertEqual(assign_storey(10, dup).status, STATUS_DUPLICATE_FL)

    def test_slab_and_foundation(self):
        storeys = [Storey("1F", 0.0), Storey("2F", 300.0)]
        self.assertEqual(assign_storey(0.0, storeys).name, "1F")
        self.assertEqual(assign_storey(299.0, storeys).name, "1F")
        self.assertEqual(assign_storey(-50.0, storeys).status, STATUS_BELOW)

    def test_tall_wall_uses_bottom(self):
        storeys = [Storey("1F", 0.0), Storey("2F", 300.0)]
        self.assertEqual(assign_storey(0.0, storeys).status, STATUS_OK)
        self.assertEqual(assign_storey(0.0, storeys).name, "1F")


class BuildStoreyPlanTests(unittest.TestCase):
    def plan(self, zs, first, roof, first_fl=0.0):
        frames = [Frame("f%s" % i, z) for i, z in enumerate(zs)]
        return build_storey_plan(frames, first, roof, first_fl)

    def test_no_basement_no_penthouse(self):
        # 1F 2F 3F RF，RF 就是最高的框。
        rows = self.plan([0, 300, 600, 900], 0, 3)
        self.assertEqual([r.name for r in rows], ["1F", "2F", "3F", "RF"])
        self.assertEqual([r.fl for r in rows], [0, 300, 600, 900])

    def test_basement_and_penthouse(self):
        rows = self.plan([-600, -300, 0, 300, 600, 900], 2, 4)
        self.assertEqual(
            [r.name for r in rows], ["B2", "B1", "1F", "2F", "RF", "R2F"]
        )

    def test_basement_numbering_is_nearest_first(self):
        rows = self.plan([-900, -600, -300, 0, 300], 3, 4)
        self.assertEqual([r.name for r in rows], ["B3", "B2", "B1", "1F", "RF"])

    def test_two_penthouse_levels(self):
        rows = self.plan([0, 300, 600, 900], 0, 1)
        self.assertEqual([r.name for r in rows], ["1F", "RF", "R2F", "R3F"])

    def test_first_fl_offsets_everything(self):
        rows = self.plan([0, 300, 600], 0, 2, first_fl=50.0)
        self.assertEqual([r.fl for r in rows], [50.0, 350.0, 650.0])

    def test_input_order_does_not_matter(self):
        frames = [Frame("rf", 600), Frame("one", 0), Frame("two", 300)]
        rows = build_storey_plan(frames, 1, 0, 0.0)
        self.assertEqual([r.name for r in rows], ["1F", "2F", "RF"])

    def test_single_frame_is_both_first_and_roof(self):
        rows = self.plan([0], 0, 0)
        self.assertEqual([r.name for r in rows], ["1F"])

    def test_same_height_frames_are_blocked(self):
        with self.assertRaises(StoreyPlanError):
            self.plan([0, 0, 300], 0, 2)

    def test_roof_below_first_is_blocked(self):
        with self.assertRaises(StoreyPlanError):
            self.plan([0, 300], 1, 0)

    def test_empty_selection_is_blocked(self):
        with self.assertRaises(StoreyPlanError):
            build_storey_plan([], 0, 0, 0.0)

    def test_index_outside_selection_is_blocked(self):
        with self.assertRaises(StoreyPlanError):
            self.plan([0, 300], 0, 5)


if __name__ == "__main__":
    unittest.main()
