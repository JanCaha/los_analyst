import math
from osgeo import ogr
from gdalhelpers.helpers import math_helpers
from typing import List


class LoS:

    def __init__(self,
                 points: List[List[float]],
                 is_global: bool = False,
                 is_without_target: bool = False,
                 observer_offset: float = 0,
                 target_offset: float = 0,
                 target_x: float = 0,
                 target_y: float = 0,
                 sampling_distance: float = None,
                 use_curvature_corrections: bool = True,
                 refraction_coefficient: float = 0.13):

        self.is_global: bool = is_global
        self.is_without_target: bool = is_without_target
        self.use_curvature_corrections: bool = use_curvature_corrections
        self.refraction_coefficient: float = refraction_coefficient
        self.observer_offset: float = observer_offset
        self.target_offset: float = target_offset
        self.target_x: float = target_x
        self.target_y: float = target_y
        self.target_index: int = None

        if sampling_distance is None:
            sampling_distance = math_helpers.distance(points[0][0], points[0][1], points[1][0], points[1][1])

        first_point_x = points[0][0]
        first_point_y = points[0][1]
        first_point_z = points[0][2] + observer_offset

        target_distance = math_helpers.distance(first_point_x, first_point_y, target_x, target_y)

        self.points: List = []
        self.previous_max_angle: List = []
        self.visible: List = []
        self.horizon: List = []

        max_angle_temp = -180

        for i in range(0, len(points)):
            point_x = points[i][0]
            point_y = points[i][1]
            point_z = points[i][2]

            distance = math_helpers.distance(first_point_x, first_point_y, point_x, point_y)

            if self.use_curvature_corrections:
                point_z = self.__curvature_corrections(point_z, distance, self.refraction_coefficient)
                target_offset = self.__curvature_corrections(target_offset, distance, self.refraction_coefficient)

            if i == 0:
                self.points.append([point_x, point_y, 0, first_point_z, -90])
            elif self.is_global and math.fabs(target_distance - distance) < sampling_distance / 2:
                self.points.append(
                    [point_x, point_y, distance, point_z + target_offset,
                     self.__angle_vertical(distance, point_z + target_offset - first_point_z)])
                self.target_index = i
            else:
                self.points.append([point_x, point_y, distance, point_z,
                                    self.__angle_vertical(distance, point_z - first_point_z)])

            # first store max angle before this point and then add new max angle
            self.previous_max_angle.append(max_angle_temp)

            if max_angle_temp < self.points[-1][4]:
                if self.is_global:
                    if i != self.target_index:
                        max_angle_temp = self.points[-1][4]
                else:
                    max_angle_temp = self.points[-1][4]

            # is visible is only valid if previous_max_angle is smaller then current angle
            if i == 0:
                self.visible.append(True)
            else:
                self.visible.append(self.previous_max_angle[i] < self.points[-1][4])

        for i in range(0, len(self.points)):
            if i == len(self.points) - 1:
                self.horizon.append(False)
            else:
                self.horizon.append((self.visible[i] is True) and (self.visible[i+1] is False))

        if self.is_global:
            self.limit_angle = self.points[self.target_index][4]
            self.is_visible = True

    def __str__(self):
        string = ""
        for i in range(0, len(self.points)):
            string += ("{} - {} {} {} (prev. {}) - vis. {} hor. {} \n".format(
                i,
                self.points[i][2],
                self.points[i][3],
                self.points[i][4],
                self.previous_max_angle[i],
                self.visible[i],
                self.horizon[i]
            ))
        return string

    @staticmethod
    def __angle_vertical(distance: float, elev_diff: float) -> float:
        return math.degrees(math.atan(elev_diff / distance))

    @staticmethod
    def __curvature_corrections(elev: float, dist: float, ref_coeff: float) -> float:
        earth_diameter = 12740000
        return elev - (math.pow(dist, 2) / earth_diameter) + ref_coeff * (math.pow(dist, 2) / earth_diameter)

    def _get_geom_at_index(self, index: int) -> ogr.Geometry:

        point = ogr.Geometry(ogr.wkbPoint25D)

        point.AddPoint(self.points[index][0],
                       self.points[index][1],
                       self.points[index][3])

        return point

    def get_horizons(self) -> List[ogr.Geometry]:

        points: List[ogr.Geometry] = []

        for i in range(0, len(self.horizon)):
            if self.horizon[i]:
                points.append(self._get_geom_at_index(i))

        return points
