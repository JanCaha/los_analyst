import unittest
from osgeo import gdal, ogr
from losanalyst.classes.los_global import LoSGlobal


class LoSGlobalClassTests(unittest.TestCase):

    def setUp(self):
        points = [[0, 0, 0],
                  [1, 0, 1],
                  [2, 0, 1.8],
                  [3, 0, 6],
                  [4, 0, 1],
                  [5, 0, 15],
                  [6, 0, 10]]
        self.simple_los = LoSGlobal(points,
                                    observer_offset=0.1,
                                    target_offset=0.05,
                                    target_x=3,
                                    target_y=0,
                                    sampling_distance=1,
                                    use_curvature_corrections=False)

    def TearDown(self):
        self.simple_los = None

    def test_get_global_horizon_index(self):
        self.assertEqual(self.simple_los._get_global_horizon_index(), 5)

    def test_get_visible(self):
        self.assertTrue(self.simple_los.get_visible())
        self.assertEqual(self.simple_los.get_visible(return_integer=True), 1)

    def test_get_angle_difference_global_horizon(self):
        self.assertAlmostEqual(self.simple_los.get_angle_difference_global_horizon(), -8.207086, places=5)

    def test_get_elevation_difference_global_horizon(self):
        self.assertAlmostEqual(self.simple_los.get_elevation_difference_global_horizon(), -2.99, places=5)

    def test_get_horizon_distance(self):
        self.assertEqual(self.simple_los.get_horizon_distance(), 5)

    def test_get_horizon_count(self):
        self.assertEqual(self.simple_los.get_horizon_count(), 1)

    def test_get_global_horizon(self):
        horizon = self.simple_los.get_global_horizon()

        point = ogr.Geometry(ogr.wkbPoint25D)
        point.AddPoint(5, 0, 15)

        self.assertEqual(horizon.ExportToWkt(), point.ExportToWkt())

    def test_get_max_local_horizon(self):
        horizon = self.simple_los.get_max_local_horizon()

        point = ogr.Geometry(ogr.wkbPoint25D)
        point.AddPoint(1, 0, 1)

        self.assertEqual(horizon.ExportToWkt(), point.ExportToWkt())