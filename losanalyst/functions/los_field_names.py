# default values for the algorithm
observer_id_field_name = "id_observer"
target_id_field_name = "id_target"
observer_offset_field_name = "observer_offset"
target_offset_field_name = "target_offset"
los_type_fn = "los_type"
# fields for global los
tp_x_field_name = "tp_x"
tp_y_field_name = "tp_y"
# field for los without target
#no_target_field_name = "no_target"
angle_field_name = "horizontal_angle"
# fields for los analysis
vertical_angle_fn = "max_vertical_angle"
horizontal_angle_fn = "horizontal_angle"
local_horizon_angle_fn = "max_local_horizon_angle"
local_horizon_distance_fn = "max_local_horizon_distance"
# field for local los analysis
visible_fn = "visible"
view_angle_fn = "view_angle"
elevation_difference_fn= "elevation_difference"
angle_difference_horizon_fn = "angle_difference_to_horizon"
elevation_difference_horizon_fn = "elevation_difference_to_horizon"
slope_difference_fn = "LOS_slope_difference_to_view_angle"
horizon_count_fn = "horizon_count"
local_horizont_distance_fn = "horizon_distance"
fuzzy_visibility_fn = "fuzzy_visibility"
# fields for global los analysis
angle_difference_global_horizon_fn = "angle_difference_to_global_horizon"
elevation_difference_global_horizon_fn = "elevation_difference_to_global_horizon"
horizon_count_behind_fn = "horizon_count_behind_target"
global_horizont_distance_fn = "global_horizon_distance"