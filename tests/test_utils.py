import pandas as pd
import pytest

from pynimate.utils import human_readable, normalize_time_col


def test_human_readable():
    assert human_readable(20.2333) == "20.23"


def test_human_readable_k():
    assert human_readable(21014, 3) == "21.014K"


def test_human_readable_m():
    assert human_readable(5241725, 1) == "5.2M"


def test_normalize_time_col_string():
    result = normalize_time_col("2024-01-15", "%Y-%m-%d")

    assert result == pd.Timestamp("2024-01-15")


def test_normalize_time_col_timestamp():
    ts = pd.Timestamp("2024-01-15")

    result = normalize_time_col(ts, "%Y-%m-%d")

    assert result is ts


def test_normalize_time_col_datetime():
    from datetime import datetime

    dt = datetime(2024, 1, 15)

    result = normalize_time_col(dt, "%Y-%m-%d")

    assert result is dt


def test_normalize_time_col_invalid_string():
    with pytest.raises(ValueError):
        normalize_time_col("15-01-2024", "%Y-%m-%d")
