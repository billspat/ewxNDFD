
from ewxndfd.datetime_utils import ensure_datetime_has_tz, has_timezone
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import pytest

@pytest.fixture
def sample_datetime():
    return datetime(2025, 11, 19, 2, 0, tzinfo=ZoneInfo("US/Eastern"))

def test_ensure_datetime_has_tz(sample_datetime):  
    # try with a datetime that already has tz info
    assert has_timezone(sample_datetime) is True  
    dt_with_tz = ensure_datetime_has_tz(sample_datetime)
    assert has_timezone(sample_datetime) is True  
    
    # try with a naive datetime
    naive_dt = datetime(2025, 11, 19, 2, 0)
    assert has_timezone(naive_dt) is False
    dt_with_tz = ensure_datetime_has_tz(naive_dt, tz="UTC")
    assert has_timezone(dt_with_tz) is True 
    
    
    
    # assert dt_with_tz.tzinfo is not None
    # assert dt_with_tz.tzinfo.zone == "US/Eastern"