from osgeo import ogr
import math
from losanalyst.classes.los import LoS


class LoSGlobal(LoS):

    def __init__(self,
                 points: list,
                 observer_offset: float = 0,
                 target_offset: float = 0,
                 target_x: float = 0,
                 target_y: float = 0,
                 sampling_distance: float = None,
                 use_curvature_corrections: bool = True,
                 refraction_coefficient: float = 0.13):

        super().__init__(points,
                         is_global=True,
                         observer_offset=observer_offset,
                         target_offset=target_offset,
                         target_x=target_x,
                         target_y=target_y,
                         sampling_distance=sampling_distance,
                         use_curvature_corrections=use_curvature_corrections,
                         refraction_coefficient=refraction_coefficient)

        self.global_horizon_index = None

    def get_visible(self, return_integer: bool = False):

        if return_integer:
            return int(self.visible[self.target_index])
        else:
            return self.visible[self.target_index]

    def _get_global_horizon_index(self):

        if self.global_horizon_index is not None:
            return self.global_horizon_index
        else:
            horizon_index = 0
            for i in range(1, len(self.points) - 1):
                if self.horizon[i] and i != self.target_index:
                    horizon_index = i
            self.global_horizon_index = horizon_index
            return self.global_horizon_index

    def get_angle_difference_global_horizon(self):
        horizon_angle = -90
        if self._get_global_horizon_index() != 0:
            horizon_angle = self.points[self._get_global_horizon_index()][4]
        return self.points[self.target_index][4] - horizon_angle

    def get_elevation_difference_global_horizon(self):
        elev_difference_horizon = self.points[self.target_index][3] - (
                    self.points[0][3] + math.tan(math.radians(self.points[self._get_global_horizon_index()][4])) *
                    self.points[self.target_index][2])
        return elev_difference_horizon

    def get_horizon_distance(self):
        return self.points[self._get_global_horizon_index()][2]

    def get_horizon_count(self):
        return math.fsum(self.horizon[self.target_index+1:])

    def __get_global_horizon_index(self):

        index = None

        for i in range(len(self.points) - 1, -1, -1):
            if self.horizon[i]:
                index = i
                break

        return index

    def get_global_horizon(self) -> ogr.Geometry:

        index = self.__get_global_horizon_index()

        if index is None:
            index = -1

        return self._get_geom_at_index(index)

    def __get_max_local_horizon_index(self) -> int:

        index = None

        for i in range(self.target_index-1, -1, -1):
            if self.horizon[i]:
                index = i
                break

        return index

    def get_max_local_horizon(self) -> ogr.Geometry:

        index = self.__get_max_local_horizon_index()

        if index is None:
            index = self.target_index

        return self._get_geom_at_index(index)
