import os

dir_path = os.path.dirname(os.path.realpath(__file__))

import pytest
import pandas as pd


@pytest.fixture
def sample_bar_data1() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": ["1960-01-01", "1961-01-01", "1962-01-01"],
            "Afghanistan": [1, 2, 3],
            "Angola": [2, 3, 4],
            "Albania": [1, 2, 5],
            "USA": [5, 3, 4],
            "Argentina": [1, 4, 5],
        }
    ).set_index("time")


@pytest.fixture
def sample_bar_data2() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": ["2012", "2013", "2014"],
            "col1": [1, 2, 3],
            "col2": [3, 2, 1],
        }
    ).set_index("time")


@pytest.fixture
def map_data() -> pd.DataFrame:
    map_data = pd.read_csv(dir_path + "/data/map.csv").set_index("time")
    return map_data
