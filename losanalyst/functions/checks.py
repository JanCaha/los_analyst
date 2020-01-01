from osgeo import ogr
import warnings
from typing import Union
from gdalhelpers.checks import layer_checks, values_checks
from gdalhelpers.classes.DEM import DEM
import losanalyst.functions.los_field_names as field_names
from losanalyst.functions import helpers


def check_los_layer(layer: ogr.Layer) -> None:
    """
    Checks that the `layer` is LoS layer.

    Parameters
    ----------
    layer : ogr.Layer
        Layer to perform the check on.

    Raises
    ------
    ValueError
        If the `layer` is not LoS.
    """
    if not is_los_layer(layer):
        raise ValueError("The provided LoS layer does not provide the necessary attributes. "
                         "It cannot be correctly processed.")


def is_los_layer(layer: ogr.Layer) -> bool:
    """
    Verify, based on presence of specific fields, that the given `layer` contains LoS data.

    Parameters
    ----------
    layer : ogr.Layer
        Layer to perform the check on.

    Returns
    -------
    bool
    """
    result1 = layer_checks.does_field_exist(layer, field_names.observer_id_field_name) and \
              layer_checks.does_field_exist(layer, field_names.target_id_field_name)
    result2 = layer_checks.does_field_exist(layer, field_names.observer_offset_field_name) and \
              layer_checks.does_field_exist(layer, field_names.target_offset_field_name)
    return result1 and result2


def is_global_los_layer(layer: ogr.Layer) -> bool:
    """
    Verify that the given `layer` contain global LoS data.

    Parameters
    ----------
    layer : ogr.Layer
        Layer to perform the check on.

    Returns
    -------
    bool
    """
    is_global = helpers.get_los_type(layer) == "global"

    result = layer_checks.does_field_exist(layer, field_names.tp_x_field_name) and \
             layer_checks.does_field_exist(layer, field_names.tp_y_field_name) and \
             is_global

    return result


def is_los_without_target(layer: ogr.Layer) -> bool:
    """
    Verify that the given `layer` contain LoS without target data.

    Parameters
    ----------
    layer : ogr.Layer
        Layer to perform the check on.

    Returns
    -------
    bool
    """
    if helpers.get_los_type(layer) == "without target":
        return True
    else:
        return False


def check_return_sampling_distance(sampling_distance: Union[int, float], dsm: DEM) -> float:
    """
    Checks that the provided sampling distance value is valid one, if it is `None` then estimates it based on pixel size
    of `dsm`.

    Parameters
    ----------
    sampling_distance : int or float
        Value of LoS sampling distance. Should be positive number.

    dsm : DEM
        If the `sampling_distance` is not provided, it is estimated as pixel size of `dsm`.

    Returns
    -------
    float
        Sampling distance.
    """

    if sampling_distance is not None:
        values_checks.check_value_is_zero_or_positive(sampling_distance, "sampling_distance")
        return float(sampling_distance)
    else:
        sampling_distance = dsm.get_min_pixel_size()
        return sampling_distance


def check_return_id_field(layer: ogr.Layer,
                          layer_name: str,
                          field_name: str) -> str:
    """
    Checks if the provided field (`field_name`) exists in `layer`. If it does not or it is not `Integer` data type
    outputs warning and sets return value as `None`.

    Parameters
    ----------
    layer : ogr.Layer
        Layer to verify.

    layer_name : str
        Layer name for warning messages.

    field_name : str
        Name of the field to look for.

    Returns
    -------
    str
        Either the name of the field or value `None` if does not exists or if it is of incorrect type.

    Warns
    -------
    UserWarning
        If the field does not exist or if it is not Integer type.
    """

    if field_name is not None:
        if not layer_checks.does_field_exist(layer, field_name):
            warnings.warn(
                "The field `{0}` does not exist in `{1}`, the default gdal FID will be used instead."
                    .format(field_name, layer_name),
                UserWarning
            )
            field_name = None
        elif not layer_checks.is_field_of_type(layer, field_name, ogr.OFTInteger):
            warnings.warn(
                "The field `{0}` in observers is not an `Integer` type, the default gdal FID will be used instead."
                    .format(field_name),
                UserWarning
            )
            field_name = None

    return field_name


def check_return_set_offset(offset: Union[str, int, float],
                            offset_name: str,
                            layer: ogr.Layer,
                            layer_name: str,
                            default_offset: float = 1.75):
    """
    Checks that `offset` is usable. The `offset` is either `str`, which specifies field name in `layer` from which the
    value is obtained, or `float` and `int` which are used directly.

    Parameters
    ----------
    offset : str or int or float
        Either numerical value or string specifying field name of `layer`.

    offset_name : str
        Name of the offset for warning messages.

    layer : ogr.Layer
        Layer to work with.

    layer_name : str
        Name of the layer for warning messages.

    default_offset : float, optional
        Offset value to use if the field does not exist. Default value is `1.75`.

    Returns
    -------
    str or float
        Either verified name of the field from `layer` or numerical value.

    Raises
    ------
    ValueError
        If some of the values is not valid.

    Warns
    -------
    UserWarning
        If the field does not exist or if it is of non-numerical type.
    """

    if not isinstance(default_offset, (float, int)):
        raise ValueError("The `default_offset` variable is not either `int` or `float`. It is: `{0}`."
                         .format(type(default_offset).__name__))

    if isinstance(offset, str):
        if not layer_checks.does_field_exist(layer, offset):
            warnings.warn(
                "`{0}` `{1}` does not exist in `{2}` layer, the default value of offset `{3}` will be used."
                    .format(offset_name, offset, layer_name, default_offset),
                UserWarning
            )
            return default_offset

        elif not (layer_checks.is_field_of_type(layer, offset, ogr.OFTInteger) or
                  layer_checks.is_field_of_type(layer, offset, ogr.OFTReal)):
            warnings.warn(
                "`{0}` field `{1}` is not either `Integer` or `Real` in `{2}` layer, "
                "the default value of offset `{3}` will be used."
                    .format(offset_name, offset, layer_name, default_offset),
                UserWarning
            )
            return default_offset
        else:
            return offset

    elif isinstance(offset, (int, float)):
        return offset

    else:
        raise ValueError("The `{0}` is not either string or number.".format(offset_name))

