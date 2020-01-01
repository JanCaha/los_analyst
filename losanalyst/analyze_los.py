from osgeo import ogr
from gdalhelpers.helpers import geometry_helpers, layer_helpers, datasource_helpers
from gdalhelpers.checks import values_checks, layer_checks, datasource_checks
import losanalyst.functions.los_field_names as field_names
from losanalyst.functions import checks, helpers
from losanalyst.classes.los_local import LoSLocal
from losanalyst.classes.los_without_target import LoSWithoutTarget
from losanalyst.classes.los_global import LoSGlobal


def analyze_local_los(los_ds: ogr.DataSource,
                      use_curvature_corrections: bool = True,
                      refraction_coefficient: float = 0.13):
    """
    Analyze local LoS.

    Parameters
    ----------
    los_ds : ogr.DataSource
        Data source containing layer with LoS to analyze.

    use_curvature_corrections : bool, optional
        Calculate Earth curvature corrections while analyzing LoS. Default value is `True`.

    refraction_coefficient : float, optional
        Refraction coefficient. Default value is `0.13`.

    Returns
    -------
    nothing
        Fields are added to `los_ds`, nothing is returned from the function.
    """

    datasource_checks.check_is_ogr_datasource(los_ds, "los_ds")

    los_layer = los_ds.GetLayer()

    checks.check_los_layer(los_layer)

    if checks.is_global_los_layer(los_layer) or checks.is_los_without_target(los_layer):
        raise TypeError("`los_ds` is not a local line-of-sight. Cannot analyze it like local LoS.")

    helpers.create_local_los_analyze_fields(los_layer)

    for feature_los in los_layer:

        geom = feature_los.GetGeometryRef()
        points = helpers.wkt_to_list(geom.ExportToWkt())

        o_offset = feature_los.GetField(field_names.observer_offset_field_name)
        t_offset = feature_los.GetField(field_names.target_offset_field_name)

        los = LoSLocal(points,
                       observer_offset=o_offset,
                       target_offset=t_offset,
                       use_curvature_corrections=use_curvature_corrections,
                       refraction_coefficient=refraction_coefficient)

        los_layer.SetFeature(feature_los)

        fields_values = {field_names.visible_fn: los.get_visible(),
                         field_names.view_angle_fn: los.get_view_angle(),
                         field_names.elevation_difference_fn: los.get_elevation_difference(),
                         field_names.angle_difference_horizon_fn: los.get_angle_difference_local_horizon(),
                         field_names.elevation_difference_horizon_fn: los.get_elevation_difference_local_horizon(),
                         field_names.slope_difference_fn: los.get_los_slope_difference(),
                         field_names.horizon_count_fn: los.get_local_horizon_count(),
                         field_names.local_horizon_distance_fn: los.get_local_horizon_distance(),
                         field_names.fuzzy_visibility_fn: los.get_fuzzy_visibility()}

        layer_helpers.add_values_from_dict(feature_los, fields_values)

        los_layer.SetFeature(feature_los)


def analyze_global_los(los_ds: ogr.DataSource,
                      use_curvature_corrections: bool = True,
                      refraction_coefficient: float = 0.13):
    """
    Analyze global LoS.

    Parameters
    ----------
    los_ds : ogr.DataSource
        Data source containing layer with LoS to analyze.

    use_curvature_corrections : bool, optional
        Calculate Earth curvature corrections while analyzing LoS. Default value is `True`.

    refraction_coefficient : float, optional
        Refraction coefficient. Default value is `0.13`.

    Returns
    -------
    nothing
        Fields are added to `los_ds`, nothing is returned from the function.
    """

    datasource_checks.check_is_ogr_datasource(los_ds, "los_ds")

    los_layer = los_ds.GetLayer()

    checks.check_los_layer(los_layer)

    if not checks.is_global_los_layer(los_layer) :
        raise TypeError("`los_ds` is not a global line-of-sight. Cannot analyze it like global LoS.")

    helpers.create_global_los_analyze_fields(los_layer)

    for feature_los in los_layer:

        geom = feature_los.GetGeometryRef()
        points = helpers.wkt_to_list(geom.ExportToWkt())

        o_offset = feature_los.GetField(field_names.observer_offset_field_name)
        t_offset = feature_los.GetField(field_names.target_offset_field_name)

        tx = feature_los.GetField(field_names.tp_x_field_name)
        ty = feature_los.GetField(field_names.tp_y_field_name)
        los = LoSGlobal(points,
                        observer_offset=o_offset,
                        target_offset=t_offset,
                        target_x=tx,
                        target_y=ty,
                        use_curvature_corrections=use_curvature_corrections,
                        refraction_coefficient=refraction_coefficient)

        los_layer.SetFeature(feature_los)

        fields_values = {field_names.visible_fn: los.get_visible(),
                         field_names.angle_difference_global_horizon_fn: los.get_angle_difference_global_horizon(),
                         field_names.elevation_difference_global_horizon_fn: los.get_elevation_difference_global_horizon(),
                         field_names.horizon_count_behind_fn: los.get_horizon_count()}

        layer_helpers.add_values_from_dict(feature_los, fields_values)

        los_layer.SetFeature(feature_los)


def analyze_no_target_los(los_ds: ogr.DataSource,
                          use_curvature_corrections: bool = True,
                          refraction_coefficient: float = 0.13):
    """
    Analyze LoS without target.

    Parameters
    ----------
    los_ds : ogr.DataSource
        Data source containing layer with LoS to analyze.

    use_curvature_corrections : bool, optional
        Calculate Earth curvature corrections while analyzing LoS. Default value is `True`.

    refraction_coefficient : float, optional
        Refraction coefficient. Default value is `0.13`.

    Returns
    -------
    nothing
        Fields are added to `los_ds`, nothing is returned from the function.
    """

    datasource_checks.check_is_ogr_datasource(los_ds, "los_ds")

    los_layer = los_ds.GetLayer()

    checks.check_los_layer(los_layer)

    if not checks.is_los_without_target(los_layer):
        raise TypeError("`los_ds` is not line-of-sight without target. Cannot analyze it like LoS without targer.")

    helpers.create_notarget_los_analyze_fields(los_layer)

    for feature_los in los_layer:

        geom = feature_los.GetGeometryRef()
        points = helpers.wkt_to_list(geom.ExportToWkt())

        o_offset = feature_los.GetField(field_names.observer_offset_field_name)

        los = LoSWithoutTarget(points,
                               observer_offset=o_offset,
                               use_curvature_corrections=use_curvature_corrections,
                               refraction_coefficient=refraction_coefficient)

        los_layer.SetFeature(feature_los)

        fields_values = {field_names.global_horizont_distance_fn: los.get_global_horizon_distance(),
                         field_names.vertical_angle_fn: los.get_maximal_vertical_angle(),
                         field_names.local_horizon_angle_fn: los.get_max_local_horizon_angle(),
                         field_names.local_horizon_distance_fn: los.get_local_horizon_distance()}

        layer_helpers.add_values_from_dict(feature_los, fields_values)

        los_layer.SetFeature(feature_los)


def analyze_los_type(los_ds: ogr.DataSource,
                     use_curvature_corrections: bool = True,
                     refraction_coefficient: float = 0.13):

    datasource_checks.check_is_ogr_datasource(los_ds, "los_ds")

    los_layer = los_ds.GetLayer()

    checks.check_is_los_layer(los_layer)

    # check type of the layer
    los_global = checks.is_global_los_layer(los_layer)
    los_without_target = checks.is_los_without_target(los_layer)

    if los_global:
        analyze_global_los(los_ds,
                           use_curvature_corrections=use_curvature_corrections,
                           refraction_coefficient=refraction_coefficient)
    elif los_without_target:
        analyze_no_target_los(los_ds,
                              use_curvature_corrections=use_curvature_corrections,
                              refraction_coefficient=refraction_coefficient)
    else:
        analyze_local_los(los_ds,
                          use_curvature_corrections=use_curvature_corrections,
                          refraction_coefficient=refraction_coefficient)
