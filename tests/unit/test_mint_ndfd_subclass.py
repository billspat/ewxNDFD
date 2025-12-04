from pathlib import Path
from datetime import date
import os
import pytest

from ewxndfd.mint_ndfd import NDFDMinT


def test_ndfdmint_instantiation(sample_dir):
    if not os.path.exists(str(sample_dir)):
        pytest.skip(f"fixture directory missing: {sample_dir}")

    n = NDFDMinT(str(sample_dir))
    assert isinstance(n, NDFDMinT)
    assert n.variable_type == 'mint'
    assert n.unit_str == 'Celsius'
    assert n.unit_abbr == '°C'
    assert n.ndfd_dir == str(sample_dir)


def test_construct_and_forecast_filename(sample_dir, sample_datetime, sample_ndfd_mint):
    n = NDFDMinT(str(sample_dir))

    # construct file name from date/hour
    fname = n.contstruct_file_name(date(2025, 11, 19), 6)
    assert fname == sample_ndfd_mint

    # forecast_file_for_local_datetime should produce same filename
    fname2 = n.forecast_file_for_local_datetime(sample_datetime)
    assert fname2 == sample_ndfd_mint


def test_get_forecast_reads_file(sample_dir, sample_datetime):
    n = NDFDMinT(str(sample_dir))
    data = n.get_forecast(local_datetime=sample_datetime)
    assert isinstance(data, list)
    assert len(data) > 0
