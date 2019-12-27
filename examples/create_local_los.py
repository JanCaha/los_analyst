from osgeo import ogr
import os
from gdalhelpers.classes.DEM import DEM
from losanalyst.create_los import create_local_los
from losanalyst.analyze_los import analyze_local_los
from losanalyst.extract_horizons import extract_horizons, extract_global_horizon

PATH_TO_DATA = os.path.join(os.path.dirname(__file__), "..", "tests", "test_data")
PATH_TO_RESULTS = os.path.join(PATH_TO_DATA, "results")

dsm = DEM(os.path.join(PATH_TO_DATA, "dsm.tif"))

observers = ogr.Open(os.path.join(PATH_TO_DATA,  "points.gpkg"))
target = ogr.Open(os.path.join(PATH_TO_DATA, "single_point.gpkg"))

local_los = create_local_los(dsm,
                             observers,
                             target,
                             sample_distance=1,
                             observer_offset=1.75,
                             target_offset=0)

ds_los = ogr.GetDriverByName("GPKG").CreateDataSource(os.path.join(PATH_TO_RESULTS, "local_los.gpkg"))
ds_los.CopyLayer(local_los.GetLayer(), "los", ["OVERWRITE=YES"])

ds_los = analyze_local_los(ds_los, use_curvature_corrections=True, refraction_coefficient=0.13)

horizons = extract_horizons(local_los)
ds_horizons = ogr.GetDriverByName("GPKG").CreateDataSource(os.path.join(PATH_TO_RESULTS, "local_los_horizons.gpkg"))
ds_horizons.CopyLayer(horizons.GetLayer(), "horizons", ["OVERWRITE=YES"])
ds_horizons = None

ds_los = None
