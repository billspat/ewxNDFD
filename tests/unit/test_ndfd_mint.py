
from datetime import datetime, timezone, date
import os
import pytest

from ewxndfd.ewx.ewx_ndfd_file import NDFD

# use contsant for example data path dir, but in future use data 
# in example have the files present drive the tests with parameterized tests


def test_ndfd_instance(sample_dir, v_type):
    if not os.path.exists(str(sample_dir)):
        raise ValueError(f"test cancelled, bad fixture, Sample directory does not exist: {sample_dir}")
    
    n = NDFD(str(sample_dir), variable_type=v_type, unit_str='Celsius', unit_abbr='°C')
    assert isinstance(n, NDFD)
    assert n.variable_type == v_type
    assert n.ndfd_dir == str(sample_dir)

    try:
        n = NDFD(str(sample_dir), variable_type='invalid_var', unit_str='Celsius', unit_abbr='°C')
        assert False, "Expected ValueError for invalid variable type"
    except ValueError as e:
        assert True  # Expected exception
    

    try:
        n = NDFD('/non/existent/path', variable_type=v_type, unit_str='Celsius', unit_abbr='°C')
        assert False, "Expected ValueError for non-existent directory"
    except ValueError as e:
        assert True  # Expected exception   
        
        
def test_construct_file_given_exact_datetime(sample_dir):
    n = NDFD(str(sample_dir),  variable_type='mint', unit_str='Celsius', unit_abbr='°C')
    
    d = date(year=2025, month=11, day= 19)
    h:int = 6
    fname = n.contstruct_file_name(date_forecast_created = d, hour_forecast_created = h)
    
    assert fname ==  'mint_20251119t06.csv'


def test_construct_file_given_any_datetime(sample_dir, sample_datetime):
    n = NDFD(str(sample_dir), variable_type='mint', unit_str='Celsius', unit_abbr='°C')
    
    sample_datetime_utc = sample_datetime.astimezone(timezone.utc)
    fname = n.forecast_file_for_utc_datetime(sample_datetime_utc)
    
    assert fname ==  'mint_20251119t06.csv'


# def test_read_and_cache_with_sample_file(sample_dir, sample_datetime):
    
#     src = sample_dir / 'mint_20251119t06.csv'
#     assert src.exists(), f"Expected sample file: {src}"

#     n = NDFD(str(sample_dir), variable_type='mint')
    
#     data = n.read(str(dest))

#     assert isinstance(data, list)
#     assert len(data) > 0
#     assert n.ndfd_file_path_cache == str(dest)
#     assert n.ndfd_data_cache == data


# def test_read_file_not_found(sample_dir):
#     n = NDFD(str(sample_dir), 'mint')
#     missing = sample_dir / 
#     with pytest.raises(FileNotFoundError):
#         n.read(str(missing))


def test_invalid_variable_raises():
    with pytest.raises(ValueError):
        NDFD('/tmp', 'notavalid', 'Celsius', '°C')
