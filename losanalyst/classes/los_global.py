from osgeo import ogr
from typing import Union
import math
from losanalyst.classes.los import LoS


class LoSGlobal(LoS):
    """
    Class representing global LoS.

    See Also
    --------
    LoS : the basic class for representation of LoS
    """

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

    def get_visible(self, return_integer: bool = False) -> Union[bool, int]:
        """
        Is the target point visible?

        Parameters
        ----------
        return_integer : bool, optional
            If the value is `True` returns values `0` or `1`. If it is `False` returns `True` or `False`.

        Returns
        -------
        bool or int
            Visibility of target point.
        """

        if return_integer:
            return int(self.visible[self.target_index])
        else:
            return self.visible[self.target_index]

    def _get_global_horizon_index(self) -> int:
        """
        Returns index of global horizon from list of points.

        Returns
        -------
        int
            Index of global horizon in `points`. If `0` then no global horizon is found.
        """

        if self.global_horizon_index is not None:
            return self.global_horizon_index
        else:
            horizon_index = 0
            for i in range(1, len(self.points) - 1):
                if self.horizon[i] and i != self.target_index:
                    horizon_index = i
            self.global_horizon_index = horizon_index
            return self.global_horizon_index

    def get_angle_difference_global_horizon(self) -> float:
        """
        Get angle difference between target point and horizon angle. Positive value means that horizon is lower than
        target point, negative value means that horizon is higher then target point.

        Returns
        -------
        float
            Value of angle difference.
        """

        horizon_angle = -90
        if self._get_global_horizon_index() != 0:
            horizon_angle = self.points[self._get_global_horizon_index()][4]
        return self.points[self.target_index][4] - horizon_angle

    def get_elevation_difference_global_horizon(self) -> float:
        """
        Get elevation difference between target point and horizon angle. Positive value means that horizon is lower than
        target point and the resulting value have to be added to target point to hide the horizon. Negative value
        means that horizon is higher then target point and it would need to lower by resulting value not to hide the
        horizon.

        Returns
        -------
        float
        """

        elev_difference_horizon = self.points[self.target_index][3] - (
                    self.points[0][3] + math.tan(math.radians(self.points[self._get_global_horizon_index()][4])) *
                    self.points[self.target_index][2])
        return elev_difference_horizon

    def get_horizon_distance(self) -> float:
        """
        Get distance of the global horizon from observer.

        Returns
        -------
        float
            Distance.
        """
        return self.points[self._get_global_horizon_index()][2]

    def get_horizon_count(self) -> int:
        """
        Get the number of horizons on LoS.

        Returns
        -------
        int
        """
        return math.fsum(self.horizon[self.target_index+1:])

    def __get_global_horizon_index(self) -> int:
        """
        Find the global horizon in `horizon`.

        Returns
        -------
        int
            Index in list.
        """

        index = None

        for i in range(len(self.points) - 1, -1, -1):
            if self.horizon[i]:
                index = i
                break

        return index

    def get_global_horizon(self) -> ogr.Geometry:
        """
        Get global horizon from LoS as `ogr.Geometry` point.

        Returns
        -------
        ogr.Geometry
        """
        index = self.__get_global_horizon_index()

        if index is None:
            index = -1

        return self._get_geom_at_index(index)

    def __get_max_local_horizon_index(self) -> int:
        """
        Get index of maximal local horizon (between observer and target) from `horizon`.

        Returns
        -------
        int or None
            If the result is `None`, there is no local horizon.
        """

        index = None

        for i in range(self.target_index-1, -1, -1):
            if self.horizon[i]:
                index = i
                break

        return index

    def get_max_local_horizon(self) -> ogr.Geometry:
        """
        Get maximal local horizon from LoS as `ogr.Geometry` point.

        Returns
        -------
        ogr.Geometry
        """
        index = self.__get_max_local_horizon_index()

        if index is None:
            index = self.target_index

        return self._get_geom_at_index(index)
