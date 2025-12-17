"""this folder holds any MSU Enviroweather (ewx) specific functionality
that is not needed for general use of the NDFD data reading and processing
capabilities provided by this package, but is used by the Enviroweather system
"""

DEFAULT_TIME_ZONE = "US/Eastern"


from .ewx_ndfd_file import NDFD
from .ewx_datetime import ewx_daily_date, ewx_daily_date_for_utc  