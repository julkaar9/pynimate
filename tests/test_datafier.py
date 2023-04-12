# Legacy tests for datafier, will be removed in 2.0.0
import pandas as pd

from pynimate.datafier import Datafier, BaseDatafier, BarDatafier


def test_datafier_init(sample_data1):
    dfr = Datafier(sample_data1, "%Y-%m-%d", "3MS", 0.1)
    assert dfr.n_bars == 5


def test_datafier_interpolate_even(sample_data2):
    dfr = Datafier(sample_data2, "%Y", "3MS")
    interpolated_data = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "2012-01-01",
                    "2012-04-01",
                    "2012-07-01",
                    "2012-10-01",
                    "2013-01-01",
                    "2013-04-01",
                    "2013-07-01",
                    "2013-10-01",
                    "2014-01-01",
                ]
            ),
            "col1": [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0],
            "col2": [3.0, 2.75, 2.5, 2.25, 2.0, 1.75, 1.5, 1.25, 1.0],
        }
    ).set_index("time")
    dfr.data.index.name = "time"
    assert dfr.data.equals(interpolated_data)


def test_datafier_get_top_cols(map_data):
    dfr = Datafier(map_data, "%Y", "3MS")
    top_cols = [
        "Argentina",
        "Australia",
        "Brazil",
        "Canada",
        "China",
        "Germany",
        "Spain",
        "France",
        "United Kingdom",
        "India",
        "Iran",
        "Israel",
        "Italy",
        "Japan",
        "South Korea",
        "Kuwait",
        "Myanmar",
        "Netherlands",
        "Poland",
        "Romania",
        "Russian Federation",
        "Saudi Arabia",
        "Sweden",
        "USA",
    ]
    assert dfr.get_top_cols() == top_cols


def test_datafier_get_bar_colors(map_data):
    dfr = Datafier(map_data, "%Y", "3MS")
    bar_colors = {
        "Argentina": (0.278791, 0.062145, 0.386592),
        "Australia": (0.283197, 0.11568, 0.436115),
        "Brazil": (0.280255, 0.165693, 0.476498),
        "Canada": (0.270595, 0.214069, 0.507052),
        "China": (0.253935, 0.265254, 0.529983),
        "Germany": (0.235526, 0.309527, 0.542944),
        "Spain": (0.21621, 0.351535, 0.550627),
        "France": (0.197636, 0.391528, 0.554969),
        "United Kingdom": (0.179019, 0.433756, 0.55743),
        "India": (0.163625, 0.471133, 0.558148),
        "Iran": (0.149039, 0.508051, 0.55725),
        "Israel": (0.135066, 0.544853, 0.554029),
        "Italy": (0.122606, 0.585371, 0.546557),
        "Japan": (0.120081, 0.622161, 0.534946),
        "South Korea": (0.134692, 0.658636, 0.517649),
        "Kuwait": (0.170948, 0.694384, 0.493803),
        "Myanmar": (0.232815, 0.732247, 0.459277),
        "Netherlands": (0.304148, 0.764704, 0.419943),
        "Poland": (0.386433, 0.794644, 0.372886),
        "Romania": (0.477504, 0.821444, 0.318195),
        "Russian Federation": (0.585678, 0.846661, 0.249897),
        "Saudi Arabia": (0.688944, 0.865448, 0.182725),
        "Sweden": (0.79376, 0.880678, 0.120005),
        "USA": (0.89632, 0.893616, 0.096335),
    }
    assert dfr.get_bar_colors() == bar_colors


def test_datafier_get_prepared_data(sample_data1):
    dfr = Datafier(sample_data1, "%Y-%m-%d", "3MS")
    dfr.df_ranks.index.name = "time"
    df_ranks = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "1960-01-01",
                    "1960-04-01",
                    "1960-07-01",
                    "1960-10-01",
                    "1961-01-01",
                    "1961-04-01",
                    "1961-07-01",
                    "1961-10-01",
                    "1962-01-01",
                ]
            ),
            "Afghanistan": [3.0, 2.5, 2.0, 2.0, 2.0, 1.5, 1.0, 1.0, 1.0],
            "Angola": [4.0, 4.0, 4.0, 4.0, 4.0, 3.5, 3.0, 3.0, 3.0],
            "Albania": [2.0, 1.5, 1.0, 1.0, 1.0, 3.0, 5.0, 5.0, 5.0],
            "USA": [5.0, 4.0, 3.0, 3.0, 3.0, 2.5, 2.0, 2.0, 2.0],
            "Argentina": [1.0, 3.0, 5.0, 5.0, 5.0, 4.5, 4.0, 4.0, 4.0],
        }
    ).set_index("time")
    data = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "1960-01-01",
                    "1960-04-01",
                    "1960-07-01",
                    "1960-10-01",
                    "1961-01-01",
                    "1961-04-01",
                    "1961-07-01",
                    "1961-10-01",
                    "1962-01-01",
                ]
            ),
            "Afghanistan": [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0],
            "Angola": [2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0],
            "Albania": [1.0, 1.25, 1.5, 1.75, 2.0, 2.75, 3.5, 4.25, 5.0],
            "USA": [5.0, 4.5, 4.0, 3.5, 3.0, 3.25, 3.5, 3.75, 4.0],
            "Argentina": [1.0, 1.75, 2.5, 3.25, 4.0, 4.25, 4.5, 4.75, 5.0],
        }
    ).set_index("time")
    assert dfr.df_ranks.equals(df_ranks)
    assert dfr.data.equals(data)


def test_basedatafier_interpolate_even(sample_data2):
    dfr = BaseDatafier(sample_data2, "%Y", "3MS")
    interpolated_data = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "2012-01-01",
                    "2012-04-01",
                    "2012-07-01",
                    "2012-10-01",
                    "2013-01-01",
                    "2013-04-01",
                    "2013-07-01",
                    "2013-10-01",
                    "2014-01-01",
                ]
            ),
            "col1": [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0],
            "col2": [3.0, 2.75, 2.5, 2.25, 2.0, 1.75, 1.5, 1.25, 1.0],
        }
    ).set_index("time")
    dfr.data.index.name = "time"
    assert dfr.data.equals(interpolated_data)


def test_bardfr_init(sample_data1):
    dfr = BarDatafier(sample_data1, "%Y-%m-%d", "3MS", 0.1)
    assert dfr.n_bars == 5


def test_bardfr_df_ranks(sample_data1):
    dfr = BarDatafier(sample_data1, "%Y-%m-%d", "3MS", 0.5)
    dfr.df_ranks.index.name = "time"
    df_ranks = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "1960-01-01",
                    "1960-04-01",
                    "1960-07-01",
                    "1960-10-01",
                    "1961-01-01",
                    "1961-04-01",
                    "1961-07-01",
                    "1961-10-01",
                    "1962-01-01",
                ]
            ),
            "Afghanistan": [3.0, 2.5, 2.0, 2.0, 2.0, 1.5, 1.0, 1.0, 1.0],
            "Angola": [4.0, 4.0, 4.0, 4.0, 4.0, 3.5, 3.0, 3.0, 3.0],
            "Albania": [2.0, 1.5, 1.0, 1.0, 1.0, 3.0, 5.0, 5.0, 5.0],
            "USA": [5.0, 4.0, 3.0, 3.0, 3.0, 2.5, 2.0, 2.0, 2.0],
            "Argentina": [1.0, 3.0, 5.0, 5.0, 5.0, 4.5, 4.0, 4.0, 4.0],
        }
    ).set_index("time")
    assert dfr.df_ranks.equals(df_ranks)


def test_bardfr_get_top_cols(map_data):
    dfr = BarDatafier(map_data, "%Y", "3MS")
    top_cols = [
        "Argentina",
        "Australia",
        "Brazil",
        "Canada",
        "China",
        "Germany",
        "Spain",
        "France",
        "United Kingdom",
        "India",
        "Iran",
        "Israel",
        "Italy",
        "Japan",
        "South Korea",
        "Kuwait",
        "Myanmar",
        "Netherlands",
        "Poland",
        "Romania",
        "Russian Federation",
        "Saudi Arabia",
        "Sweden",
        "USA",
    ]
    assert dfr.get_top_cols() == top_cols
