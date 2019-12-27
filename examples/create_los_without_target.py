from osgeo import ogr
import os
from gdalhelpers.classes.DEM import DEM
from gdalhelpers.functions.create_points_at_angles_distance_in_direction import create_points_at_angles_distance_in_direction
from losanalyst.create_los import create_no_target_los
from losanalyst.analyze_los import analyze_no_target_los

PATH_TO_DATA = os.path.join(os.path.dirname(__file__), "..", "tests", "test_data")
PATH_TO_RESULTS = os.path.join(PATH_TO_DATA, "results")

dsm = DEM(os.path.join(PATH_TO_DATA, "dsm.tif"))

observers = ogr.Open(os.path.join(PATH_TO_DATA,  "points.gpkg"))
target = ogr.Open(os.path.join(PATH_TO_DATA, "single_point.gpkg"))

targets = create_points_at_angles_distance_in_direction(start_points=observers,
                                                        main_direction_point=target,
                                                        distance=30,
                                                        angle_offset=10,
                                                        angle_density=1)
no_target_los = create_no_target_los(dsm,
                                     observers,
                                     targets,
                                     sample_distance=1,
                                     observer_offset=1.75,
                                     target_offset=0)

ds_los = ogr.GetDriverByName("GPKG").CreateDataSource(os.path.join(PATH_TO_RESULTS, "no_target_los.gpkg"))
ds_los.CopyLayer(no_target_los.GetLayer(), "los", ["OVERWRITE=YES"])

ds_los = analyze_no_target_los(ds_los, use_curvature_corrections=True, refraction_coefficient=0.13)

ds_los = None
