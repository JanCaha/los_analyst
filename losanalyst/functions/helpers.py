from osgeo import ogr
from typing import List
from gdalhelpers.helpers import layer_helpers
from gdalhelpers.checks import geometry_checks
import losanalyst.functions.los_field_names as field_names


def wkt_to_list(wkt: str) -> List[List[float]]:
    """
    Extract list of list of coordinates from WKT.

    For `LINESTRING` the outcome is `[[P1X, P1Y, P1Z], [P2X, P2Y, P3Z], ..., [PNX, PNY, PNZ]]`.

    Parameters
    ----------
    wkt : str
        String representing geometry in WKT. Currently only implemented for `LINESTRING` type.

    Returns
    -------
    list of list of float
    """

    geometry_checks.check_is_wkt_geometry(wkt, "wkt")

    if "LINESTRING" in wkt:
        array = wkt.replace("LINESTRING ", "").replace("(", "").replace(")", "").split(",")
    else:
        raise NotImplementedError("This type `{0}` of WKT type is not yet implemented, only `LINESTRING`".
                                  format(wkt))

    array_result: List[List[float]] = []

    for element in array:
        coords = element.split(" ")
        array_result.append([float(coords[0]), float(coords[1]), float(coords[2])])

    return array_result


def get_los_type(los_layer: ogr.Layer) -> str:
    """
    Obtain type of LoS from the field.

    Parameters
    ----------
    los_layer : ogr.Layer
        Layer to extract type from.

    Returns
    -------
    str
        Possible values are: `"local"`, `"global"` or `"without target"`.

    """
    los_types = []
    for element in los_layer:
        los_types.append(element.GetField(field_names.los_type_fn))

    los_types_set = set(los_types)

    if len(los_types_set) == 1:
        return list(los_types_set)[0]
    else:
        raise ValueError("More than one type of LoS find in the layer. Cannot work with mixed types of LoS."
                         "Types found: {}.".format("".join(map(str, list(los_types_set)))))


def create_basic_los_fields(los_layer: ogr.Layer) -> None:
    """
    Functions that adds fields to LoS while creating the LoS.

    Parameters
    ----------
    los_layer : ogr.Layer
        Layer to add the the fields to.

    Returns
    -------
    Nothing
    """

    fields_definition = {field_names.observer_id_field_name: ogr.OFTInteger,
                         field_names.target_id_field_name: ogr.OFTInteger,
                         field_names.observer_offset_field_name: ogr.OFTReal,
                         field_names.target_offset_field_name: ogr.OFTReal,
                         field_names.los_type_fn: ogr.OFTString}

    layer_helpers.add_fields_from_dict(los_layer, fields_definition)


def create_global_los_fields(los_layer: ogr.Layer) -> None:
    """
    Functions that adds fields to global LoS while creating the LoS.

    Parameters
    ----------
    los_layer : ogr.Layer
        Layer to add the the fields to.

    Returns
    -------
    Nothing
    """

    fields_definition = {field_names.tp_x_field_name: ogr.OFTReal,
                         field_names.tp_y_field_name: ogr.OFTReal}

    layer_helpers.add_fields_from_dict(los_layer, fields_definition)


def create_notarget_los_fields(los_layer: ogr.Layer) -> None:
    """
    Functions that adds fields to LoS without target while creating the LoS.

    Parameters
    ----------
    los_layer : ogr.Layer
        Layer to add the the fields to.

    Returns
    -------
    Nothing
    """

    fields_definition = {field_names.angle_field_name: ogr.OFTReal}

    layer_helpers.add_fields_from_dict(los_layer, fields_definition)


def create_notarget_los_analyze_fields(los_layer: ogr.Layer) -> None:
    """
    Functions that adds fields to LoS without target for its analysis.

    Parameters
    ----------
    los_layer : ogr.Layer
        Layer to add the the fields to.

    Returns
    -------
    Nothing
    """

    fields_definition = {field_names.vertical_angle_fn: ogr.OFTReal,
                         field_names.local_horizon_angle_fn: ogr.OFTReal,
                         field_names.local_horizon_distance_fn: ogr.OFTReal,
                         field_names.global_horizont_distance_fn: ogr.OFTReal}

    layer_helpers.add_fields_from_dict(los_layer, fields_definition)


def create_global_los_analyze_fields(los_layer: ogr.Layer) -> None:
    """
    Functions that adds fields to global LoS for its analysis.

    Parameters
    ----------
    los_layer : ogr.Layer
        Layer to add the the fields to.

    Returns
    -------
    Nothing
    """

    fields_definition = {field_names.visible_fn: ogr.OFTInteger,
                         field_names.angle_difference_global_horizon_fn: ogr.OFTReal,
                         field_names.elevation_difference_global_horizon_fn: ogr.OFTReal,
                         field_names.horizon_count_behind_fn: ogr.OFTInteger,
                         field_names.global_horizont_distance_fn: ogr.OFTReal}

    layer_helpers.add_fields_from_dict(los_layer, fields_definition)


def create_local_los_analyze_fields(los_layer: ogr.Layer) -> None:
    """
    Functions that adds fields to local LoS for its analysis.

    Parameters
    ----------
    los_layer : ogr.Layer
        Layer to add the the fields to.

    Returns
    -------
    Nothing
    """

    fields_definition = {field_names.visible_fn: ogr.OFTInteger,
                         field_names.view_angle_fn: ogr.OFTReal,
                         field_names.elevation_difference_fn: ogr.OFTReal,
                         field_names.angle_difference_horizon_fn: ogr.OFTReal,
                         field_names.elevation_difference_horizon_fn: ogr.OFTReal,
                         field_names.slope_difference_fn: ogr.OFTReal,
                         field_names.horizon_count_fn: ogr.OFTInteger,
                         field_names.local_horizon_distance_fn: ogr.OFTReal,
                         field_names.fuzzy_visibility_fn: ogr.OFTReal}

    layer_helpers.add_fields_from_dict(los_layer, fields_definition)
