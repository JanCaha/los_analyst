from osgeo import ogr
import numbers
import warnings
from typing import Union
from gdalhelpers.checks import layer_checks, values_checks
from gdalhelpers.classes.DEM import DEM
import losanalyst.functions.los_field_names as field_names
from losanalyst.functions import helpers


def check_los_layer(layer: ogr.Layer) -> None:
    if not is_los_layer(layer):
        raise ValueError("The provided LoS layer does not provide the necessary attributes. "
                         "It cannot be correctly processed.")


def is_los_layer(layer: ogr.Layer) -> bool:
    result1 = layer_checks.does_field_exist(layer, field_names.observer_id_field_name) and \
              layer_checks.does_field_exist(layer, field_names.target_id_field_name)
    result2 = layer_checks.does_field_exist(layer, field_names.observer_offset_field_name) and \
              layer_checks.does_field_exist(layer, field_names.target_offset_field_name)
    return result1 and result2


def is_global_los_layer(layer: ogr.Layer) -> bool:
    is_global = helpers.get_los_type(layer) == "global"

    result = layer_checks.does_field_exist(layer, field_names.tp_x_field_name) and \
             layer_checks.does_field_exist(layer, field_names.tp_y_field_name) and \
             is_global

    return result


def is_los_without_target(layer: ogr.Layer) -> bool:
    if helpers.get_los_type(layer) == "without target":
        return True
    else:
        return False


def check_return_sampling_distance(sampling_distance: numbers.Number, dsm: DEM):
    if sampling_distance is not None:
        values_checks.check_value_is_zero_or_positive(sampling_distance, "sampling_distance")
        return sampling_distance
    else:
        sampling_distance = dsm.get_min_pixel_size()
        return sampling_distance


def check_return_id_field(layer: ogr.Layer,
                          layer_name: str,
                          field_name: str):

    if field_name is not None:
        if not layer_checks.does_field_exist(layer, field_name):
            warnings.warn(
                "The field `{0}` does not exist in `{1}`, the default gdal FID will be used instead."
                    .format(field_name, layer_name)
            )
            field_name = None
        elif not layer_checks.is_field_of_type(layer, field_name, ogr.OFTInteger):
            warnings.warn(
                "The field `{0}` in observers is not an `Integer` type, the default gdal FID will be used instead."
                    .format(field_name)
            )
            field_name = None

    return field_name


def check_return_set_offset(offset: Union[str, numbers.Number],
                            offset_name: str,
                            layer: ogr.Layer,
                            layer_name: str,
                            default_offset: float = 1.5):

    if not isinstance(default_offset, numbers.Number):
        raise ValueError("The `default_offset` variable is not either string or number. It is: `{0}`."
                         .format(type(offset_name).__name__))

    if isinstance(offset, str):
        if not layer_checks.does_field_exist(layer, offset):
            warnings.warn(
                "`{0}` `{1}` does not exist in `{2}` layer, the default value of offset `{3}` will be used."
                    .format(offset_name, offset, layer_name, default_offset)
            )
            return default_offset

        elif not (layer_checks.is_field_of_type(layer, offset, ogr.OFTInteger) or
                  layer_checks.is_field_of_type(layer, offset, ogr.OFTReal)):
            warnings.warn(
                "`{0}` field `{1}` is not either `Integer` or `Real` in `{2}` layer, "
                "the default value of offset `{3}` will be used."
                    .format(offset_name, offset, layer_name, default_offset)
            )
            return default_offset

    elif isinstance(offset, numbers.Number):
        return offset

    else:
        raise ValueError("The `{0}` is not either string or number.".format(offset_name))

