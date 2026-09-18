import os

import geopandas as gpd
import pandas as pd
import pytest
from shapely import Point

from pynimate.datafier import BarDatafier, BaseDatafier, LineDatafier
from pynimate.geodatafier import GeoDatafier

dir_path = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def sample_data1() -> pd.DataFrame:
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
def sample_data2() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": ["2012", "2013", "2014"],
            "col1": [1, 2, 3],
            "col2": [3, 2, 1],
        }
    ).set_index("time")


@pytest.fixture
def sample_data1_basedfr(sample_data1) -> BaseDatafier:
    return BaseDatafier(sample_data1, "%Y-%m-%d", "3MS")


@pytest.fixture
def sample_data1_bardfr(sample_data1) -> BarDatafier:
    return BarDatafier(sample_data1, "%Y-%m-%d", "3MS")


@pytest.fixture
def sample_data1_linedfr(sample_data1) -> BarDatafier:
    return LineDatafier(sample_data1, "%Y-%m-%d", "3MS")


@pytest.fixture
def map_data() -> pd.DataFrame:
    map_data = pd.read_csv(dir_path + "/data/map.csv").set_index("time")
    return map_data


@pytest.fixture
def sample_geodfr():
    return GeoDatafier(
        gpd.GeoDataFrame(
            {
                "name": ["A", "B"],
                "2020-01-01": [0, 100],
                "2020-01-03": [20, 160],
                "geometry": [Point(0, 0), Point(1, 1)],
            },
            geometry="geometry",
        ),
        time_format="%Y-%m-%d",
        ip_freq="D",
    )
