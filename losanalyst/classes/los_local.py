from osgeo import ogr
import math
from losanalyst.classes.los import LoS


class LoSLocal(LoS):
    """
    Class representing local LoS.

    See Also
    --------
    LoS : the basic class for representation of LoS
    """

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

    def is_target_visible(self, return_integer: bool = False):
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
            return int(self.visible[-1])
        else:
            return self.visible[-1]

    def get_view_angle(self) -> float:
        """
        Get view angle from observer to target.

        Returns
        -------
        float
            Angle.
        """
        return self.target_angle

    def get_elevation_difference(self) -> float:
        """
        Get elevation difference between observer and target.

        Returns
        -------
        float
            Elevation difference.
        """
        return self.points[0][3] - self.points[-1][3]

    def get_max_local_horizon(self) -> ogr.Geometry:
        """
        Get maximal local horizon from LoS as `ogr.Geometry` point.

        Returns
        -------
        ogr.Geometry
        """
        index = self._get_max_local_horizon_index()

        if index is None:
            index = 0

        return self._get_geom_at_index(index)

    def get_angle_difference_local_horizon(self) -> float:
        """
        Get angle difference between target point and local horizon. Positive value means that target is higher then
        horizon, negative value indicates that horizon is higher.

        Returns
        -------
        float
            Angle difference.
        """
        return self.target_angle - self.points[self._get_max_local_horizon_index()][4]

    def get_elevation_difference_local_horizon(self) -> float:
        """
        Get elevation difference between target point and local horizon. Positive value means that target is higher then
        horizon, negative value indicates that horizon is higher.

        Returns
        -------
        float
            Elevation difference.

        """
        return self.points[-1][3] - self.points[0][3] - \
               math.tan(math.radians(self.points[self._get_max_local_horizon_index()][4])) * self.points[-1][2]

    def get_los_slope_difference(self) -> float:
        """
        Get difference between LoS slope and view angle to target.

        Returns
        -------
        float
            Angle difference.
        """
        los_slope = math.degrees(math.atan((self.points[-1][3] - self.points[-2][3]) /
                                           (self.points[-1][2] - self.points[-2][2])))
        return los_slope - self.target_angle

    def get_local_horizon_distance(self) -> float:
        """
        Get distance of maximal local horizon from observer.

        Returns
        -------
        float
            Distance.
        """
        return self.points[self._get_max_local_horizon_index()][2]

    def get_local_horizon_count(self) -> int:
        """
        Get number of horizons between observer and target.

        Returns
        -------
        int
            Horizon count.
        """
        return math.fsum(self.horizon)

    def get_fuzzy_visibility(self,
                             object_size: float = 10,
                             recognition_acuinty: float = 0.017,
                             clear_visibility_distance: float = 500) -> float:
        """
        Calculates fuzzy visibility between observer and target.

        Parameters
        ----------
        object_size : float, optional
            Size of the theoretical object to be recognized. Default values is `10`.

        recognition_acuinty : float, optional
            Smallest size (in anglular units) that the observer can see. Default is `0.017`.

        clear_visibility_distance : float, optional
            The distance at which the observer can still perfectly see the `object_size` without problems.

        Returns
        -------
        float
            Value of fuzzy visibility, where `1` means perfect visibility and `0` means no visibility.
        """

        b1 = clear_visibility_distance
        h = object_size
        beta = recognition_acuinty

        b2 = h / (2 * math.tan(beta / 2))

        if self.points[-1][2] < b1:
            return 1
        else:
            return 1 / (1 + math.pow((self.points[-1][2] - b1) / b2, 2))

    def _get_max_local_horizon_index(self) -> int:
        """
        Get index of maximal local horizon.

        Returns
        -------
        int
        """

        index = None

        for i in range(len(self.points) - 1, -1, -1):
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

        index = self._get_max_local_horizon_index()

        if index is None:
            index = self.target_index

        return self._get_geom_at_index(index)
