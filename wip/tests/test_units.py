import unittest

from tests import SRC  # noqa: F401  先插入 path

from loopflow_r2m.units import inbound_vertex_z, meters_to_rhino, rhino_to_meters


class UnitsTests(unittest.TestCase):
    def test_centimetre_roundtrip(self):
        scale = 0.01
        metres = rhino_to_meters(280, scale)
        self.assertAlmostEqual(metres, 2.8)
        self.assertAlmostEqual(meters_to_rhino(metres, scale), 280)

    def test_metre_identity(self):
        self.assertEqual(rhino_to_meters(2.8, 1.0), 2.8)
        self.assertEqual(meters_to_rhino(2.8, 1.0), 2.8)

    def test_zero_scale_rejected(self):
        with self.assertRaises(ValueError):
            meters_to_rhino(1.0, 0)

    def test_inbound_z_undoes_fl_offset(self):
        metres_to_doc = 100.0
        self.assertAlmostEqual(inbound_vertex_z(8.5, metres_to_doc, 850.0), 0.0)
        self.assertAlmostEqual(inbound_vertex_z(8.5, metres_to_doc, 903.0), -53.0)

    def test_inbound_z_zero_shift(self):
        self.assertAlmostEqual(inbound_vertex_z(2.8, 100.0, 0.0), 280.0)


if __name__ == "__main__":
    unittest.main()
