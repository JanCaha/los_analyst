from osgeo import ogr
from gdalhelpers.helpers import datasource_helpers, layer_helpers
from gdalhelpers.checks import layer_checks, datasource_checks
from losanalyst.functions import checks, helpers
import losanalyst.functions.los_field_names as field_names
from losanalyst.classes.los_local import LoSLocal
from losanalyst.classes.los_without_target import LoSWithoutTarget
from losanalyst.classes.los_global import LoSGlobal


def extract_horizons(los_ds: ogr.DataSource,
                     use_curvature_corrections: bool = True,
                     refraction_coefficient: float = 0.13) -> ogr.DataSource:

    horizons_ds = datasource_helpers.create_temp_gpkg_datasource()

    datasource_checks.check_is_ogr_datasource(los_ds, "los_ds")

    los_layer = los_ds.GetLayer()

    checks.check_los_layer(los_layer)

    # check type of the layer
    los_global = checks.is_global_los_layer(los_layer)
    los_without_target = checks.is_los_without_target(los_layer)

    layer_helpers.create_layer_points_25d(horizons_ds, los_layer.GetSpatialRef(), "horizons")
    horizons_layer = horizons_ds.GetLayer()

    fields_types = {field_names.observer_id_field_name: ogr.OFTInteger,
                    field_names.target_id_field_name: ogr.OFTInteger}

    layer_helpers.add_fields_from_dict(horizons_layer, fields_types)

    horizon_feature_defn = horizons_layer.GetLayerDefn()

    for feature_los in los_layer:

        los_geom = feature_los.GetGeometryRef()
        los_points = helpers.wkt_to_list(los_geom.ExportToWkt())

        o_offset = feature_los.GetField(field_names.observer_offset_field_name)
        t_offset = feature_los.GetField(field_names.target_offset_field_name)

        o_id = feature_los.GetField(field_names.observer_id_field_name)
        t_id = feature_los.GetField(field_names.target_id_field_name)

        if los_without_target:
            los = LoSWithoutTarget(los_points,
                                   observer_offset=o_offset,
                                   use_curvature_corrections=use_curvature_corrections,
                                   refraction_coefficient=refraction_coefficient)
        elif los_global:
            t_x = feature_los.GetField(field_names.tp_x_field_name)
            t_y = feature_los.GetField(field_names.tp_y_field_name)
            los = LoSGlobal(los_points,
                            observer_offset=o_offset,
                            target_offset=t_offset,
                            target_x=t_x,
                            target_y=t_y,
                            use_curvature_corrections=use_curvature_corrections,
                            refraction_coefficient=refraction_coefficient)
        else:
            los = LoSLocal(los_points,
                           observer_offset=o_offset,
                           target_offset=t_offset,
                           use_curvature_corrections=use_curvature_corrections,
                           refraction_coefficient=refraction_coefficient)

        geoms = los.get_horizons()

        if 0 < len(geoms):
            for geom in geoms:

                horizon_feature = ogr.Feature(horizon_feature_defn)

                horizon_feature.SetGeometry(geom)

                fields_values = {field_names.observer_id_field_name: o_id,
                                 field_names.target_id_field_name: t_id}

                layer_helpers.add_values_from_dict(horizon_feature, fields_values)

                horizons_layer.CreateFeature(horizon_feature)

                horizon_feature = None

    return horizons_ds


def extract_global_horizon(los_ds: ogr.DataSource,
                           use_curvature_corrections: bool = True,
                           refraction_coefficient: float = 0.13) -> ogr.DataSource:

    horizons_ds = datasource_helpers.create_temp_gpkg_datasource()

    datasource_checks.check_is_ogr_datasource(los_ds, "los_ds")

    los_layer = los_ds.GetLayer()

    checks.check_los_layer(los_layer)

    # check type of the layer
    los_global = checks.is_global_los_layer(los_layer)
    los_without_target = checks.is_los_without_target(los_layer)

    layer_helpers.create_layer_points_25d(horizons_ds, los_layer.GetSpatialRef(), "horizons")
    horizons_layer = horizons_ds.GetLayer()

    fields_types = {field_names.observer_id_field_name: ogr.OFTInteger,
                    field_names.target_id_field_name: ogr.OFTInteger}

    layer_helpers.add_fields_from_dict(horizons_layer, fields_types)

    horizon_feature_defn = horizons_layer.GetLayerDefn()

    for feature_los in los_layer:

        los_geom = feature_los.GetGeometryRef()
        los_points = helpers.wkt_to_list(los_geom.ExportToWkt())

        o_offset = feature_los.GetField(field_names.observer_offset_field_name)
        t_offset = feature_los.GetField(field_names.target_offset_field_name)

        o_id = feature_los.GetField(field_names.observer_id_field_name)
        t_id = feature_los.GetField(field_names.target_id_field_name)

        if los_without_target:
            los = LoSWithoutTarget(los_points,
                                   observer_offset=o_offset,
                                   use_curvature_corrections=use_curvature_corrections,
                                   refraction_coefficient=refraction_coefficient)
        elif los_global:
            t_x = feature_los.GetField(field_names.tp_x_field_name)
            t_y = feature_los.GetField(field_names.tp_y_field_name)
            los = LoSGlobal(los_points,
                            observer_offset=o_offset,
                            target_offset=t_offset,
                            target_x=t_x,
                            target_y=t_y,
                            use_curvature_corrections=use_curvature_corrections,
                            refraction_coefficient=refraction_coefficient)
        else:
            raise ValueError("Cannot get global horizon for local LOS.")

        horizon_feature = ogr.Feature(horizon_feature_defn)

        geom = los.get_global_horizon()

        horizon_feature.SetGeometry(geom)

        fields_values = {field_names.observer_id_field_name: o_id,
                         field_names.target_id_field_name: t_id}

        layer_helpers.add_values_from_dict(horizon_feature, fields_values)

        horizons_layer.CreateFeature(horizon_feature)

        horizon_feature = None

    return horizons_ds
