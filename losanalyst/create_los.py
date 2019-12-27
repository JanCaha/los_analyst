from osgeo import gdal, ogr, osr
import numbers
import warnings
from typing import Union
from gdalhelpers.classes.DEM import DEM
from gdalhelpers.helpers import geometry_helpers, layer_helpers, datasource_helpers
from gdalhelpers.checks import values_checks, layer_checks, datasource_checks, srs_checks
import losanalyst.functions.los_field_names as field_names
from losanalyst.functions import checks, helpers


def create_local_los(dsm: DEM,
                     observers_ds: gdal.ogr.DataSource,
                     targets_ds: gdal.ogr.DataSource,
                     sample_distance: float = None,
                     observer_id_field: str = None,
                     target_id_field: str = None,
                     observer_offset: Union[str, numbers.Number] = 1.5,
                     target_offset: Union[str, numbers.Number] = 0):

    return create_los(dsm=dsm,
                      observers_ds=observers_ds,
                      targets_ds=targets_ds,
                      sample_distance=sample_distance,
                      global_los=False,
                      los_without_target=False,
                      observer_id_field=observer_id_field,
                      target_id_field=target_id_field,
                      observer_offset=observer_offset,
                      target_offset=target_offset)


def create_global_los(dsm: DEM,
                      observers_ds: gdal.ogr.DataSource,
                      targets_ds: gdal.ogr.DataSource,
                      sample_distance: float = None,
                      observer_id_field: str = None,
                      target_id_field: str = None,
                      observer_offset: Union[str, numbers.Number] = 1.5,
                      target_offset: Union[str, numbers.Number] = 0):

    return create_los(dsm=dsm,
                      observers_ds=observers_ds,
                      targets_ds=targets_ds,
                      sample_distance=sample_distance,
                      global_los=True,
                      los_without_target=False,
                      observer_id_field=observer_id_field,
                      target_id_field=target_id_field,
                      observer_offset=observer_offset,
                      target_offset=target_offset)


def create_no_target_los(dsm: DEM,
                         observers_ds: gdal.ogr.DataSource,
                         targets_ds: gdal.ogr.DataSource,
                         sample_distance: float = None,
                         observer_id_field: str = None,
                         target_id_field: str = None,
                         observer_offset: Union[str, numbers.Number] = 1.5,
                         target_offset: Union[str, numbers.Number] = 0):

    return create_los(dsm=dsm,
                      observers_ds=observers_ds,
                      targets_ds=targets_ds,
                      sample_distance=sample_distance,
                      global_los=False,
                      los_without_target=True,
                      observer_id_field=observer_id_field,
                      target_id_field=target_id_field,
                      observer_offset=observer_offset,
                      target_offset=target_offset)


def create_los(dsm: DEM,
               observers_ds: gdal.ogr.DataSource,
               targets_ds: gdal.ogr.DataSource,
               sample_distance: float = None,
               global_los: bool = False,
               los_without_target: bool = False,
               observer_id_field: str = None,
               target_id_field: str = None,
               observer_offset: Union[str, numbers.Number] = 1.5,
               target_offset: Union[str, numbers.Number] = 0):

    # create temp datasource to return
    los_ds = datasource_helpers.create_temp_gpkg_datasource()

    # check datasources
    datasource_checks.check_is_ogr_datasource(los_ds, "los_ds")
    datasource_checks.check_is_ogr_datasource(observers_ds, "observers_ds")
    datasource_checks.check_is_ogr_datasource(targets_ds, "targets_ds")

    # check DEM
    if not isinstance(dsm, DEM):
        raise TypeError("`dsm` must be of class `DEM`. dsm is of type `{0}`."
                        .format(type(dsm)))

    # check sample distance
    sample_distance = checks.check_return_sampling_distance(sample_distance, dsm)

    # get layers and srs for point layers
    observers_layer = observers_ds.GetLayer()
    observers_srs = observers_layer.GetSpatialRef()
    targets_layer = targets_ds.GetLayer()
    targets_srs = targets_layer.GetSpatialRef()

    # check ID field names
    observer_id_field = checks.check_return_id_field(observers_layer, "observers_ds", observer_id_field)
    target_id_field = checks.check_return_id_field(targets_layer, "targets_ds", target_id_field)

    # check offsets
    observer_offset = checks.check_return_set_offset(observer_offset, "observer_offset",
                                                     observers_layer, "observers_ds",
                                                     default_offset=1.5)

    target_offset = checks.check_return_set_offset(target_offset, "target_offset",
                                                   targets_layer, "targets_ds",
                                                   default_offset=0)

    # check if SRS are projected
    srs_checks.check_srs_projected(observers_srs, "observers")
    srs_checks.check_srs_projected(targets_srs, "targets")

    # check if SRS are the same
    srs_checks.check_srs_are_same(observers_srs, targets_srs)

    # prepare output layer
    los_layer = layer_helpers.create_layer_lines_25d(los_ds, observers_srs, "los")

    # add basic los fields
    helpers.create_basic_los_fields(los_layer)

    if global_los:
        helpers.create_global_los_fields(los_layer)

    if los_without_target:
        helpers.create_notarget_los_fields(los_layer)

    # get los feature defintion
    los_feature_defn = los_layer.GetLayerDefn()

    # load dsm as numpy array
    dsm.load_array()

    for observer_feature in observers_layer:

        for target_feature in targets_layer:

            # set offsets to add to Z
            if isinstance(observer_offset, str):
                o_offset = observer_feature.GetField(observer_offset)
            else:
                o_offset = observer_offset

            if isinstance(target_offset, str):
                t_offset = target_feature.GetField(target_offset)
            else:
                t_offset = target_offset

            # create geometry of los, more complex for global los
            if global_los:
                o_point = observer_feature.GetGeometryRef()
                t_point = target_feature.GetGeometryRef()
                angle = geometry_helpers.angle_points(o_point, t_point)
                e_point = geometry_helpers.point_at_angle_distance(o_point, dsm.get_diagonal_size(), angle)
                line = geometry_helpers.line_create_3_points(o_point, t_point, e_point, sample_distance)
                line = geometry_helpers.line_assign_z_to_vertexes(line, dsm)

            elif los_without_target:

                if observer_feature.GetFID() == target_feature.GetField("input_point_FID"):
                    o_point = observer_feature.GetGeometryRef()
                    t_point = target_feature.GetGeometryRef()
                    angle = geometry_helpers.angle_points(o_point, t_point)
                    e_point = geometry_helpers.point_at_angle_distance(o_point, dsm.get_diagonal_size(), angle)
                    line = geometry_helpers.line_create_2_points(o_point, e_point, sample_distance)
                    line = geometry_helpers.line_assign_z_to_vertexes(line, dsm)

            else:
                line = geometry_helpers.line_create_2_points(observer_feature.GetGeometryRef(),
                                                             target_feature.GetGeometryRef(),
                                                             sample_distance)
                line = geometry_helpers.line_assign_z_to_vertexes(line, dsm)

            # create the feature with geometry
            los_feature = ogr.Feature(los_feature_defn)
            los_feature.SetGeometry(line)

            field_values = {field_names.los_type_fn: "local"}

            # add attributes to los
            if global_los:

                field_values.update({field_names.los_type_fn: "global"})

                field_values.update({field_names.tp_x_field_name: t_point.GetX(),
                                     field_names.tp_y_field_name: t_point.GetY()})

            if los_without_target:
                field_values.update({field_names.los_type_fn: "without target"})

                field_values.update({field_names.angle_field_name: angle})

            # fields ids
            if observer_id_field is not None:
                field_values.update({field_names.observer_id_field_name: observer_feature.GetField(observer_id_field)})
            else:
                field_values.update({field_names.observer_id_field_name: observer_feature.GetFID()})

            if target_id_field is not None:
                field_values.update({field_names.target_id_field_name: target_feature.GetField(target_id_field)})
            else:
                field_values.update({field_names.target_id_field_name: target_feature.GetFID()})

            # fields offsets
            field_values.update({field_names.observer_offset_field_name: o_offset,
                                 field_names.target_offset_field_name: t_offset})

            # add all combinations of fields and values
            layer_helpers.add_values_from_dict(los_feature, field_values)

            if los_without_target:
                if observer_feature.GetFID() == target_feature.GetField("input_point_FID"):
                    los_layer.CreateFeature(los_feature)
            else:
                # add the feature to layer
                los_layer.CreateFeature(los_feature)

            los_feature = None

        targets_layer.ResetReading()

    # remove numpy array from DEM so it does not take too much RAM
    dsm.destroy_array()

    return los_ds