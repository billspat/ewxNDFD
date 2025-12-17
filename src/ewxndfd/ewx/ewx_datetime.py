from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
    
from ..datetime_utils import is_utc

from . import DEFAULT_TIME_ZONE

def ewx_daily_date(local_dt:datetime)->date:
    if isinstance(local_dt, date) and not isinstance(local_dt, datetime):
        local_date = local_dt.date()
    else:
        local_date = local_dt
        
    ewx_date = local_date + timedelta(days=1)
    return(ewx_date)

def ewx_daily_date_for_utc(utc_dt:datetime, tz:str = DEFAULT_TIME_ZONE)->date:
    """get the ewx date for daily NDFD data, which is the date
    of the local datetime at 12:00 am

    Args:
        dt (datetime): local datetime value 
    Returns:
        date: ewx date for daily NDFD data
    """
    if not is_utc(utc_dt):
        raise ValueError("dt_utc must be in utc timezone")
    # check is_valid_timezone tz
          
    local_dt = utc_dt.astimezone(ZoneInfo(tz))
    return(ewx_daily_date(local_dt))   
        
        
    