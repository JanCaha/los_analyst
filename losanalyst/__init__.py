"""
Main module that provides access to the most important functions of the package.

Functions :

* `losanalyst.tools.create_los.create_local_los()`

* `losanalyst.tools.create_los.create_global_los()`

* `losanalyst.tools.create_los.create_no_target_los()`

* `losanalyst.tools.analyze_los.analyze_local_los()`

* `losanalyst.tools.analyze_los.analyze_global_los()`

* `losanalyst.tools.analyze_los.analyze_no_target_los()`
"""

from losanalyst.tools.create_los import create_local_los, create_global_los, create_no_target_los
from losanalyst.tools.analyze_los import analyze_no_target_los, analyze_local_los, analyze_global_los
from losanalyst.tools.extract_horizons import *

