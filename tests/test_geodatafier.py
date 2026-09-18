import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point

from pynimate.geodatafier import GeoDatafier


def sample_gdf():
    return gpd.GeoDataFrame(
        {
            "name": ["A", "B"],
            "2020-01-01": [0, 100],
            "2020-01-03": [20, 160],
            "geometry": [Point(0, 0), Point(1, 1)],
        },
        geometry="geometry",
    )


def sample_gdf_monthly():
    return gpd.GeoDataFrame(
        {
            "name": ["A", "B"],
            "2020-01": [0, 100],
            "2020-02": [20, 160],
            "geometry": [Point(0, 0), Point(1, 1)],
        },
        geometry="geometry",
    )


def test_no_time_columns():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A"],
            "population": [100],
            "geometry": [Point(0, 0)],
        },
        geometry="geometry",
    )

    with pytest.raises(ValueError, match="Failed to detect any time column"):
        GeoDatafier(
            gdf,
            time_format="%Y",
            ip_freq="D",
        )


def test_single_time_column():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A"],
            "2020": [100],
            "geometry": [Point(0, 0)],
        },
        geometry="geometry",
    )

    with pytest.raises(ValueError, match="at least 2 time columns"):
        GeoDatafier(
            gdf,
            time_format="%Y",
            ip_freq="D",
        )


def test_interpolation_creates_new_columns():
    gdf = sample_gdf()

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    assert len(geo.time_cols) == 3
    assert pd.Timestamp("2020-01-01") in geo.data.columns


def test_interpolation_preserves_original_values():
    gdf = sample_gdf()

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    result = geo.data

    assert result.loc[0, pd.Timestamp("2020-01-01")] == 0
    assert result.loc[0, pd.Timestamp("2020-01-03")] == 20
    assert result.loc[1, pd.Timestamp("2020-01-01")] == 100
    assert result.loc[1, pd.Timestamp("2020-01-03")] == 160


def test_interpolation_linear_values():
    gdf = sample_gdf()

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
        ip_method="linear",
    )

    result = geo.data

    assert result.loc[0, pd.Timestamp("2020-01-02")] == 10
    assert result.loc[1, pd.Timestamp("2020-01-02")] == 130


def test_interpolation_preserves_static_columns():
    gdf = sample_gdf()

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    result = geo.data

    assert list(result["name"]) == ["A", "B"]
    assert result.geometry.equals(gdf.geometry)


def test_interpolation_with_two_day_frequency_creates_expected_columns():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A"],
            "2020-01-01": [0],
            "2020-01-05": [40],
            "geometry": [Point(0, 0)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="2D",
    )

    expected = [
        pd.Timestamp(time_str)
        for time_str in [
            "2020-01-01",
            "2020-01-03",
            "2020-01-05",
        ]
    ]
    assert len(geo.time_cols) == 3
    for col in expected:
        assert col in geo.data.columns


def test_monthly_to_10day_interpolation():
    gdf = sample_gdf_monthly()  # Jan 1 and Feb 1

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m",
        ip_freq="10D",
    )

    cols = [c for c in geo.time_cols]

    expected = [
        pd.Timestamp("2020-01-01"),
        pd.Timestamp("2020-01-11"),
        pd.Timestamp("2020-01-21"),
        pd.Timestamp("2020-01-31"),
        pd.Timestamp("2020-02-01"),
    ]
    assert len(cols) == 5
    assert cols == expected


def test_month_end_interpolation():

    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", "B"],
            "2020-01-31": [0, 100],
            "2020-02-29": [20, 160],
            "geometry": [Point(0, 0), Point(1, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="10D",
    )

    assert len(geo.time_cols) == 4
    assert pd.Timestamp("2020-01-31") in geo.time_cols
    assert pd.Timestamp("2020-02-10") in geo.time_cols
    assert pd.Timestamp("2020-02-20") in geo.time_cols
    assert pd.Timestamp("2020-02-29") in geo.time_cols


def test_get_time_cols_detect_time_columns():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", "B"],
            "2020-01-31": [0, 100],
            "ISO": ["USA", "IND"],
            "2020-02-29": [20, 160],
            "geometry": [Point(0, 0), Point(1, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    cols, idxs = geo.get_time_cols(gdf, "%Y-%m-%d")

    assert cols == ["2020-01-31", "2020-02-29"]
    assert idxs == [1, 3]
    assert geo.raw_time_cols == ["2020-01-31", "2020-02-29"]
    assert geo.raw_time_idxs == [1, 3]


def test_get_time_cols_invalid_dates_are_ignored():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", "B"],
            "2020": [0, 100],
            "2021": [0, 100],
            "2021-02-29": [20, 160],
            "geometry": [Point(0, 0), Point(1, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y",
        ip_freq="MS",
    )

    cols, idxs = geo.get_time_cols(gdf, "%Y")

    assert cols == ["2020", "2021"]
    assert idxs == [1, 2]
    assert geo.raw_time_cols == ["2020", "2021"]
    assert geo.raw_time_idxs == [1, 2]


def test_get_static_cols():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", "B"],
            "ISO": ["USA", "IND"],
            "2020": [0, 100],
            "2021": [0, 100],
            "geometry": [Point(0, 0), Point(1, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y",
        ip_freq="MS",
    )

    static_cols = geo.get_static_cols(
        gdf,
        ["2020", "2021"],
    )

    assert static_cols == ["name", "ISO", "geometry"]
    assert geo.static_cols == ["name", "ISO", "geometry"]


def test_get_static_cols_geo_only():
    gdf = gpd.GeoDataFrame(
        {
            "2020": [0, 100],
            "2021": [0, 100],
            "geometry": [Point(0, 0), Point(1, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y",
        ip_freq="MS",
    )

    static_cols = geo.get_static_cols(
        gdf,
        ["2020", "2021"],
    )

    assert static_cols == ["geometry"]
    assert geo.static_cols == ["geometry"]


def test_get_masked_geo_annots():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", "B", "A", "D"],
            "2020-01-01": [0, 100, 12, 45],
            "2020-01-03": [20, 160, 50, 8],
            "geometry": [Point(0, 0), Point(1, 1), Point(1, 2), Point(2, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_masked_geo_annots({"name": ["A", "D"]})

    assert len(geo.annot_data) == 3
    assert list(geo.annot_data["name"]) == ["A", "A", "D"]


def test_mult_get_masked_geo_annots():
    gdf = gpd.GeoDataFrame(
        {
            "continent": ["Asia", "Asia", "North America", "Europe"],
            "country": ["India", "China", "USA", "Germany"],
            "2020-01-01": [0, 100, 12, 45],
            "2020-01-03": [20, 160, 50, 8],
            "geometry": [Point(0, 0), Point(1, 1), Point(1, 2), Point(2, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_masked_geo_annots({"continent": ["Asia"], "country": ["India"]})
    assert len(geo.annot_data) == 1
    assert list(geo.annot_data["continent"]) == ["Asia"]
    assert list(geo.annot_data["country"]) == ["India"]


def test_exclude_get_masked_geo_annots():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", "B", "A", "D"],
            "2020-01-01": [0, 100, 12, 45],
            "2020-01-03": [20, 160, 50, 8],
            "geometry": [Point(0, 0), Point(1, 1), Point(1, 2), Point(2, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_masked_geo_annots({"~name": ["A", "D"]})

    assert len(geo.annot_data) == 1
    assert list(geo.annot_data["name"]) == ["B"]


def test_exclude_mult_get_masked_geo_annots():
    gdf = gpd.GeoDataFrame(
        {
            "continent": ["Asia", "Asia", "North America", "Europe"],
            "country": ["India", "China", "USA", "Germany"],
            "2020-01-01": [0, 100, 12, 45],
            "2020-01-03": [20, 160, 50, 8],
            "geometry": [Point(0, 0), Point(1, 1), Point(1, 2), Point(2, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_masked_geo_annots({"~continent": ["Asia"], "~country": ["Germany"]})
    assert len(geo.annot_data) == 1
    assert list(geo.annot_data["continent"]) == ["North America"]
    assert list(geo.annot_data["country"]) == ["USA"]


def test_exclude_include_mult_get_masked_geo_annots():
    gdf = gpd.GeoDataFrame(
        {
            "continent": ["Asia", "Asia", "North America", "Europe"],
            "country": ["India", "China", "USA", "Germany"],
            "2020-01-01": [0, 100, 12, 45],
            "2020-01-03": [20, 160, 50, 8],
            "geometry": [Point(0, 0), Point(1, 1), Point(1, 2), Point(2, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_masked_geo_annots({"~continent": ["Asia"], "country": ["Germany"]})
    assert len(geo.annot_data) == 1
    assert list(geo.annot_data["continent"]) == ["Europe"]
    assert list(geo.annot_data["country"]) == ["Germany"]


def test_get_masked_geo_annots_no_matches():
    gdf = sample_gdf()

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_masked_geo_annots({"name": ["Z"]})

    assert geo.annot_data.empty


def test_get_masked_geo_annots_internal():
    gdf = sample_gdf()

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_masked_geo_annots({"name": ["A"]})

    wanted = gpd.GeoDataFrame(
        {
            "name": ["A"],
            "geometry": [Point(0, 0)],
            pd.Timestamp("2020-01-01"): [0.0],
            pd.Timestamp("2020-01-02"): [10.0],
            pd.Timestamp("2020-01-03"): [20.0],
        },
        geometry="geometry",
    )
    wanted.index = pd.Index([0], dtype="object")
    pd.testing.assert_frame_equal(wanted, geo.annot_data)

    geo.annot_data.loc[:, "name"] = "Changed"
    assert geo.data.loc[0, "name"] == "A"


def test_get_filtered_geo_annots():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", "B", "A", "D"],
            "2020-01-01": [0, 100, 12, 45],
            "2020-01-03": [20, 160, 50, 8],
            "geometry": [Point(0, 0), Point(1, 1), Point(1, 2), Point(2, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_filtered_geo_annots(lambda s: s.where(s >= 50, np.nan))

    np.testing.assert_array_equal(
        np.array(geo.annot_data[pd.Timestamp("2020-01-01")]),
        np.array(
            [
                np.nan,
                100.0,
                np.nan,
                np.nan,
            ]
        ),
    )

    np.testing.assert_array_equal(
        np.array(geo.annot_data[pd.Timestamp("2020-01-03")]),
        np.array(
            [
                np.nan,
                160.0,
                50.0,
                np.nan,
            ]
        ),
    )


def test_get_filtered_geo_annots_internal():
    gdf = sample_gdf()

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_filtered_geo_annots(lambda s: s.where(s >= 50, np.nan))
    original = geo.data.copy()

    wanted = gpd.GeoDataFrame(
        {
            "name": ["A", "B"],
            "geometry": [Point(0, 0), Point(1, 1)],
            pd.Timestamp("2020-01-01"): [np.nan, 100.0],
            pd.Timestamp("2020-01-02"): [np.nan, 130.0],
            pd.Timestamp("2020-01-03"): [np.nan, 160.0],
        },
        geometry="geometry",
    )
    wanted.index = pd.Index([0, 1], dtype="object")
    pd.testing.assert_frame_equal(wanted, geo.annot_data)
    assert geo.annot_data["name"].equals(geo.data["name"])
    assert geo.annot_data.geometry.equals(geo.data.geometry)
    assert geo.data.equals(original)


def test_format_geo_geo_annots():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", "B", "A", "D"],
            "2020-01-01": [0, 100, 12, 45],
            "2020-01-03": [20, 160, 50, 8],
            "geometry": [Point(0, 0), Point(1, 1), Point(1, 2), Point(2, 1)],
        },
        geometry="geometry",
    )

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_filtered_geo_annots(lambda s: s.where(s >= 50, np.nan))
    geo._format_geo_annots(lambda x: f"{int(x)} km" if not pd.isna(x) else "")
    np.testing.assert_array_equal(
        np.array(geo.annot_data[pd.Timestamp("2020-01-01")]),
        np.array(
            [
                "",
                "100 km",
                "",
                "",
            ]
        ),
    )

    np.testing.assert_array_equal(
        np.array(geo.annot_data[pd.Timestamp("2020-01-03")]),
        np.array(
            [
                "",
                "160 km",
                "50 km",
                "",
            ]
        ),
    )


def test_format_geo_geo_annots_annot_data():
    gdf = sample_gdf()

    geo = GeoDatafier(
        gdf,
        time_format="%Y-%m-%d",
        ip_freq="D",
    )

    geo._get_filtered_geo_annots(lambda s: s.where(s >= 50, np.nan))
    geo._format_geo_annots(lambda x: f"{int(x)} km" if not pd.isna(x) else "")
    original = geo.data.copy()

    wanted = gpd.GeoDataFrame(
        {
            "name": ["A", "B"],
            "geometry": [Point(0, 0), Point(1, 1)],
            pd.Timestamp("2020-01-01"): ["", "100 km"],
            pd.Timestamp("2020-01-02"): ["", "130 km"],
            pd.Timestamp("2020-01-03"): ["", "160 km"],
        },
        geometry="geometry",
    )
    wanted.index = pd.Index([0, 1], dtype="object")
    pd.testing.assert_frame_equal(wanted, geo.annot_data)
    assert geo.annot_data["name"].equals(geo.data["name"])
    assert geo.annot_data.geometry.equals(geo.data.geometry)
    assert geo.data.equals(original)


# Regression Tests


def test_interpolate_arbitrary_time_format1():
    data = gpd.GeoDataFrame(
        {
            "name": ["A"],
            "2020_01": [0],
            "2020_03": [10],
            "2020_05": [20],
            "geometry": [Point(0, 0)],
        },
        geometry="geometry",
    )

    dfr = GeoDatafier(
        data,
        time_format="%Y_%m",
        ip_freq="MS",
    )

    expected = gpd.GeoDataFrame(
        {
            "name": ["A"],
            "geometry": [Point(0, 0)],
            pd.Timestamp("2020-01-01"): [0.0],
            pd.Timestamp("2020-02-01"): [5.0],
            pd.Timestamp("2020-03-01"): [10.0],
            pd.Timestamp("2020-04-01"): [15.0],
            pd.Timestamp("2020-05-01"): [20.0],
        },
        geometry="geometry",
    )
    print(dfr.data)
    pd.testing.assert_frame_equal(dfr.data, expected, check_index_type=False)
