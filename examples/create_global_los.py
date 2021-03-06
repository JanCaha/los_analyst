from osgeo import ogr
import os
from gdalhelpers.classes.DEM import DEM
from losanalyst import create_global_los
from losanalyst import analyze_global_los
from losanalyst import extract_horizons, extract_global_horizon

PATH_TO_DATA = os.path.join(os.path.dirname(__file__), "..", "tests", "test_data")
PATH_TO_RESULTS = os.path.join(PATH_TO_DATA, "results")

dsm = DEM(os.path.join(PATH_TO_DATA, "dsm.tif"))

observers = ogr.Open(os.path.join(PATH_TO_DATA,  "points.gpkg"))
target = ogr.Open(os.path.join(PATH_TO_DATA, "single_point.gpkg"))

global_los = create_global_los(dsm,
                               observers,
                               target,
                               sample_distance=1,
                               observer_offset=1.75,
                               target_offset=0)

ds_los = ogr.GetDriverByName("GPKG").CreateDataSource(os.path.join(PATH_TO_RESULTS, "global_los.gpkg"))
ds_los.CopyLayer(global_los.GetLayer(), "los", ["OVERWRITE=YES"])

analyze_global_los(ds_los, use_curvature_corrections=True, refraction_coefficient=0.13)

horizons = extract_horizons(global_los)
ds_horizons = ogr.GetDriverByName("GPKG").CreateDataSource(os.path.join(PATH_TO_RESULTS, "global_los_horizons.gpkg"))
ds_horizons.CopyLayer(horizons.GetLayer(), "horizons", ["OVERWRITE=YES"])
ds_horizons = None

horizons = extract_global_horizon(global_los)
ds_horizons = ogr.GetDriverByName("GPKG").CreateDataSource(os.path.join(PATH_TO_RESULTS,
                                                                        "global_los_global_horizons.gpkg"))
ds_horizons.CopyLayer(horizons.GetLayer(), "global_horizons", ["OVERWRITE=YES"])
ds_horizons = None

ds_los = None
