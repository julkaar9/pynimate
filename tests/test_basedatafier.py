import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from pynimate.datafier import BaseDatafier


@pytest.fixture
def datafier1():
    df = pd.DataFrame(
        {
            "num1": [0, np.nan, 10],
            "num2": [20, 2, 1],
            "cat": [np.nan, "a", "b"],
        },
        index=pd.to_datetime(["2020-01-01", "2020-01-03"]),
    )
    return BaseDatafier(df, "%Y-%m-%d", "D")


def test_interpolate_even_num():
    df = pd.DataFrame(
        {
            "num1": [20, 8, 1],
        },
        index=pd.to_datetime(["2020-01-01", "2020-01-03", "2020-01-05"]),
    )
    dfr = BaseDatafier(df, "%Y-%m-%d", "D")

    expected = pd.DataFrame(
        {
            "num1": [20.0, 14.0, 8.0, 4.5, 1.0],
        },
        index=pd.to_datetime(
            ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
        ),
    )

    pdt.assert_frame_equal(dfr.data, expected)


def test_interpolate_even_col_order():
    df = pd.DataFrame(
        {
            "num1": [20, 8, 1],
            "cat": ["a", "b", "c"],
        },
        index=pd.to_datetime(["2020-01-01", "2020-01-03", "2020-01-05"]),
    )
    dfr = BaseDatafier(df, "%Y-%m-%d", "D")

    expected = pd.DataFrame(
        {
            "cat": ["a", "b", "b", "c", "c"],
            "num1": [20.0, 14.0, 8.0, 4.5, 1.0],
        },
        index=pd.to_datetime(
            ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
        ),
    )

    pdt.assert_frame_equal(dfr.data, expected)


def test_interpolate_even_fills_num_edge_nans():
    df = pd.DataFrame(
        {
            "num1": [20, np.nan, 1],
            "num2": [np.nan, 10.5, 1],
            "num3": [20, 10.5, np.nan],
        },
        index=pd.to_datetime(["2020-01-01", "2020-01-03", "2020-01-05"]),
    )
    dfr = BaseDatafier(df, "%Y-%m-%d", "D")

    expected = pd.DataFrame(
        {
            "num1": [20.0, 15.25, 10.5, 5.75, 1.0],
            "num2": [10.5, 10.5, 10.5, 5.75, 1.0],
            "num3": [20.0, 15.25, 10.5, 10.5, 10.5],
        },
        index=pd.to_datetime(
            ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
        ),
    )

    pdt.assert_frame_equal(dfr.data, expected)


def test_interpolate_even_fills_cat():
    df = pd.DataFrame(
        {
            "cat1": ["a", "b", "c"],
            "cat2": [np.nan, "b", "c"],
            "num1": [20, np.nan, 1],
            "cat3": ["a", "b", np.nan],
        },
        index=pd.to_datetime(["2020-01-01", "2020-01-03", "2020-01-05"]),
    )
    dfr = BaseDatafier(df, "%Y-%m-%d", "D")

    expected = pd.DataFrame(
        {
            "cat1": ["a", "b", "b", "c", "c"],
            "cat2": ["b", "b", "b", "c", "c"],
            "cat3": ["a", "b", "b", "b", "b"],
            "num1": [20.0, 15.25, 10.5, 5.75, 1.0],
        },
        index=pd.to_datetime(
            ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
        ),
    )

    pdt.assert_frame_equal(dfr.data, expected)


def test_interpolate_even_expanded():
    df = pd.DataFrame(
        {
            "catt1": ["a", "b", "c"],
            "num1": [20, 25, 30],
            "num2": [np.nan, 10.5, 1],
            "num3": [20, 10.5, np.nan],
            "num4": [20, np.nan, 1],
        },
        index=pd.to_datetime(["2020-01-01", "2020-01-03", "2020-01-05"]),
    )
    dfr = BaseDatafier(df, "%Y-%m-%d", "D")

    expected = pd.DataFrame(
        {
            "catt1": ["a", np.nan, "b", np.nan, "c"],
            "num1": [20, np.nan, 25, np.nan, 30],
            "num2": [np.nan, np.nan, 10.5, np.nan, 1],
            "num3": [20, np.nan, 10.5, np.nan, np.nan],
            "num4": [20, np.nan, np.nan, np.nan, 1],
        },
        index=pd.to_datetime(
            ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"]
        ),
    )

    pdt.assert_frame_equal(dfr.expanded, expected)


def test_interpolate_even_preserves_original_numeric_points():
    df = pd.DataFrame(
        {
            "num": [20.0, 8.0, 1.0],
        },
        index=pd.to_datetime(
            ["2020-01-01 00:00", "2020-01-02 00:00", "2020-01-03 00:00"]
        ),
    )

    dfr = BaseDatafier(df, "%Y-%m-%d %H:%M", "12h")

    expected = pd.Series(
        [20.0, 14.0, 8.0, 4.5, 1.0],
        index=pd.to_datetime(
            [
                "2020-01-01 00:00",
                "2020-01-01 12:00",
                "2020-01-02 00:00",
                "2020-01-02 12:00",
                "2020-01-03 00:00",
            ]
        ),
        name="num",
    )

    pdt.assert_series_equal(dfr.data["num"], expected)


def test_interpolate_even_preserves_existing_aligned_points():
    df = pd.DataFrame(
        {
            "num": [20.0, 8.0, 5.0, 1.0],
        },
        index=pd.to_datetime(["2020-01-01", "2020-01-05", "2020-01-07", "2020-01-09"]),
    )

    dfr = BaseDatafier(df, "%Y-%m-%d", "2D")

    expected = pd.DataFrame(
        {
            "num": [
                20.0,  # Jan 1 (original)
                14.0,  # Jan 3 (inserted)
                8.0,  # Jan 5 (original)
                5.0,  # Jan 7 (original)
                1.0,  # Jan 9 (original)
            ]
        },
        index=pd.to_datetime(
            [
                "2020-01-01",
                "2020-01-03",
                "2020-01-05",
                "2020-01-07",
                "2020-01-09",
            ]
        ),
    )

    pdt.assert_frame_equal(dfr.data, expected)


def test_interpolate_even_midnight_boundary():
    df = pd.DataFrame(
        {
            "num": [20.0, 8.0],
        },
        index=pd.to_datetime(
            [
                "2020-01-01 23:00",
                "2020-01-02 01:00",
            ]
        ),
    )

    dfr = BaseDatafier(df, "%Y-%m-%d %H:%M", "1h")

    expected = pd.DataFrame(
        {
            "num": [20.0, 14.0, 8.0],
        },
        index=pd.to_datetime(
            [
                "2020-01-01 23:00",
                "2020-01-02 00:00",
                "2020-01-02 01:00",
            ]
        ),
    )

    pdt.assert_frame_equal(dfr.data, expected)


def test_interpolate_even_month_boundary():
    df = pd.DataFrame(
        {
            "num": [20.0, 8.0],
        },
        index=pd.to_datetime(
            [
                "2020-01-30",
                "2020-02-02",
            ]
        ),
    )

    dfr = BaseDatafier(df, "%Y-%m-%d", "D")

    expected = pd.DataFrame(
        {
            "num": [20.0, 16.0, 12.0, 8.0],
        },
        index=pd.to_datetime(
            [
                "2020-01-30",
                "2020-01-31",
                "2020-02-01",
                "2020-02-02",
            ]
        ),
    )

    pdt.assert_frame_equal(dfr.data, expected)


def test_interpolate_even_year_boundary():
    df = pd.DataFrame(
        {
            "num": [20.0, 8.0],
        },
        index=pd.to_datetime(
            [
                "2020-12-31",
                "2021-01-02",
            ]
        ),
    )

    dfr = BaseDatafier(df, "%Y-%m-%d", "D")

    expected = pd.DataFrame(
        {
            "num": [20.0, 14.0, 8.0],
        },
        index=pd.to_datetime(
            [
                "2020-12-31",
                "2021-01-01",
                "2021-01-02",
            ]
        ),
    )

    pdt.assert_frame_equal(dfr.data, expected)


def test_interpolate_even_leap_year():
    df = pd.DataFrame(
        {
            "num": [20.0, 8.0],
        },
        index=pd.to_datetime(
            [
                "2020-02-28",
                "2020-03-01",
            ]
        ),
    )

    dfr = BaseDatafier(df, "%Y-%m-%d", "D")

    expected = pd.DataFrame(
        {
            "num": [20.0, 14.0, 8.0],
        },
        index=pd.to_datetime(
            [
                "2020-02-28",
                "2020-02-29",
                "2020-03-01",
            ]
        ),
    )

    pdt.assert_frame_equal(dfr.data, expected)
