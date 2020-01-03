import unittest
from osgeo import gdal, ogr
from losanalyst.classes.los_local import LoSLocal


class LoSLocalClassTests(unittest.TestCase):

    def setUp(self):
        points = [[0, 0, 0],
                  [1, 0, 1],
                  [2, 0, 2],
                  [3, 0, 6],
                  [4, 0, 1],
                  [5, 0, 15]]
        self.simple_los = LoSLocal(points,
                                   observer_offset=0.1,
                                   target_offset=0.05,
                                   sampling_distance=1,
                                   use_curvature_corrections=False)

    def TearDown(self):
        self.simple_los = None

    def test_is_target_visible(self):
        self.assertTrue(self.simple_los.is_target_visible())
        self.assertTrue(self.simple_los.is_target_visible(return_integer=True))

    def test_get_view_angle(self):
        self.assertAlmostEqual(self.simple_los.get_view_angle(), 71.45, places=2)

    def test_get_elevation_difference(self):
        self.assertEqual(self.simple_los.get_elevation_difference(), -14.9)

    def test_get_max_local_horizon_index(self):
        self.assertEqual(self.simple_los._get_max_local_horizon_index(), 3)
