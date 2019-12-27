from osgeo import ogr
import math
from losanalyst.classes.los import LoS


class LoSLocal(LoS):

    def __init__(self,
                 points: list,
                 observer_offset: float = 0,
                 target_offset: float = 0,
                 sampling_distance: float = None,
                 use_curvature_corrections: bool = True,
                 refraction_coefficient: float = 0.13):

        super().__init__(points,
                         observer_offset=observer_offset,
                         target_offset=target_offset,
                         sampling_distance=sampling_distance,
                         use_curvature_corrections=use_curvature_corrections,
                         refraction_coefficient=refraction_coefficient)

        self.target_angle = self.points[-1][4]
        self.highest_local_horizon_index = None

    def get_visible(self, return_integer: bool = False):

        if return_integer:
            return int(self.visible[-1])
        else:
            return self.visible[-1]

    def get_view_angle(self) -> float:
        return self.target_angle

    def get_elevation_difference(self) -> float:
        return self.points[0][3] - self.points[-1][3]

    def __get_max_local_horizon_index(self) -> int:

        if self.highest_local_horizon_index is not None:
            return self.highest_local_horizon_index
        else:
            horizon_index = 0
            for i in range(1, len(self.points) - 1):
                if self.horizon[i]:
                    horizon_index = i
            self.highest_local_horizon_index = horizon_index
            return self.highest_local_horizon_index

    def get_max_local_horizon(self) -> ogr.Geometry:

        index = self.__get_max_local_horizon_index()

        if index is None:
            index = 0

        return self._get_geom_at_index(index)

    def get_angle_difference_local_horizon(self) -> float:
        return self.target_angle - self.points[self.__get_max_local_horizon_index()][4]

    def get_elevation_difference_local_horizon(self) -> float:
        return self.points[-1][3] - self.points[0][3] - \
               math.tan(math.radians(self.points[self.__get_max_local_horizon_index()][4])) * self.points[-1][2]

    def get_los_slope_difference(self) -> float:
        los_slope = math.degrees(math.atan((self.points[-1][3] - self.points[-2][3]) /
                                           (self.points[-1][2] - self.points[-2][2])))
        return los_slope - self.target_angle

    def get_local_horizon_distance(self) -> float:
        return self.points[self.__get_max_local_horizon_index()][2]

    def get_local_horizon_count(self) -> float:
        return math.fsum(self.horizon)

    def get_fuzzy_visibility(self,
                             object_size: float = 10,
                             recognition_acuinty: float = 0.017,
                             clear_visibility_distance: float = 500) -> float:

        b1 = clear_visibility_distance
        h = object_size
        beta = recognition_acuinty

        b2 = h / (2 * math.tan(beta / 2))

        if self.points[-1][2] < b1:
            return 1
        else:
            return 1 / (1 + math.pow((self.points[-1][2] - b1) / b2, 2))

    def __get_max_local_horizon_index(self) -> int:

        index = None

        for i in range(len(self.points) - 1, -1, -1):
            if self.horizon[i]:
                index = i
                break

        return index

    def get_max_local_horizon(self) -> ogr.Geometry:

        index = self.__get_max_local_horizon_index()

        if index is None:
            index = self.target_index

        return self._get_geom_at_index(index)
