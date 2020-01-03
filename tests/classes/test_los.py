import unittest
from osgeo import gdal, ogr
from losanalyst.classes.los import LoS


class LoSClassTests(unittest.TestCase):

    def setUp(self):
        points = [[0, 0, 0],
                  [1, 0, 1],
                  [2, 0, 2],
                  [3, 0, 6],
                  [4, 0, 1],
                  [5, 0, 15]]
        self.simple_los = LoS(points,
                              sampling_distance=1,
                              use_curvature_corrections=False)

    def TearDown(self):
        self.simple_los = None

    def test_angle_vertical(self):
        self.assertAlmostEqual(LoS._angle_vertical(0, 1), 90)
        self.assertAlmostEqual(LoS._angle_vertical(1, 1), 45)
        self.assertAlmostEqual(LoS._angle_vertical(1, 0), 0)

    def test_max_previous_angle(self):
        max_previous_angles = [-180, -90, 45.0, 45.0, 63.43494882292201, 63.43494882292201]
        for i in range(0, len(max_previous_angles)):
            self.assertAlmostEqual(max_previous_angles[i], self.simple_los.previous_max_angle[i])

    def test_visibility(self):
        visibility = [True, True, False, True, False, True]
        self.assertListEqual(visibility, self.simple_los.visible)

    def test_get_geom(self):
        geom = self.simple_los._get_geom_at_index(3)

        point = ogr.Geometry(ogr.wkbPoint25D)
        point.AddPoint(3, 0, 6)

        self.assertEqual(geom.ExportToWkt(), point.ExportToWkt())

    def test_get_horizons(self):
        p1 = ogr.Geometry(ogr.wkbPoint25D)
        p1.AddPoint(1, 0, 1)
        p2 = ogr.Geometry(ogr.wkbPoint25D)
        p2.AddPoint(3, 0, 6)
        points = [p1, p2]

        self.assertEqual(points[0].ExportToWkt(), self.simple_los.get_horizons()[0].ExportToWkt())
        self.assertEqual(points[1].ExportToWkt(), self.simple_los.get_horizons()[1].ExportToWkt())
