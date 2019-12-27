from osgeo import ogr
from losanalyst.classes.los import LoS
from gdalhelpers.helpers import math_helpers


class LoSWithoutTarget(LoS):

    def __init__(self,
                 points: list,
                 observer_offset: float = 0,
                 sampling_distance: float = None,
                 use_curvature_corrections: bool = True,
                 refraction_coefficient: float = 0.13):

        super().__init__(points=points,
                         is_without_target=True,
                         observer_offset=observer_offset,
                         sampling_distance=sampling_distance,
                         use_curvature_corrections=use_curvature_corrections,
                         refraction_coefficient=refraction_coefficient)

    def get_horizontal_angle(self) -> float:
        return math_helpers.horizontal_angle(self.points[0][0], self.points[0][1],
                                             self.points[-1][0], self.points[-1][1])

    def get_maximal_vertical_angle(self) -> float:
        angles = [row[4] for row in self.points]
        return max(angles)

    def __get_max_local_horizon_index(self) -> int:

        index_visible = None
        index_horizon = None

        for i in range(len(self.points) - 1, -1, -1):
            if self.visible[i]:
                index_visible = i
                break

        if 0 < index_visible:
            for i in range(index_visible - 1, -1, -1):
                if self.horizon[i]:
                    index_horizon = i
                    break

        return index_horizon

    def get_max_local_horizon_angle(self) -> float:

        index_horizon = self.__get_max_local_horizon_index()

        if index_horizon is not None:
            return self.points[index_horizon][4]
        else:
            return -180

    def get_local_horizon_distance(self) -> float:

        index_horizon = self.__get_max_local_horizon_index()

        if index_horizon is not None:
            return self.points[index_horizon][2]
        else:
            return 0

    def get_max_local_horizon(self) -> ogr.Geometry:

        index = self.__get_max_local_horizon_index()

        if index is None:
            index = 0

        return self._get_geom_at_index(index)

    def __get_global_horizon_index(self) -> int:

        index = None

        for i in range(len(self.points)-1, -1, -1):
            if self.horizon[i]:
                index = i
                break

        return index

    def get_global_horizon_distance(self) -> float:

        index = self.__get_global_horizon_index()

        if index is not None:
            return self.points[index][2]
        else:
            return 0

    def get_global_horizon(self) -> ogr.Geometry:

        index = self.__get_global_horizon_index()

        if index is None:
            index = -1

        return self._get_geom_at_index(index)
