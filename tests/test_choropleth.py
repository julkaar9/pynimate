import geopandas as gpd
import pandas as pd
import pytest
from shapely import Point

from pynimate.choropleth import Choropleth


def test_choropleth_init(sample_geodfr):
    choropleth = Choropleth(sample_geodfr)

    assert choropleth._gpd is not None
    assert choropleth.dfr is sample_geodfr


def test_init_lognorm_with_negvmin(sample_geodfr):
    with pytest.raises(
        ValueError,
        match="Log normalization requires all values to be positive",
    ):
        Choropleth(sample_geodfr, vrange=(-1, None), log_norm=True)


def test_init_lognorm(sample_geodfr):

    plot = Choropleth(sample_geodfr, vrange=(5, 20), log_norm=True)
    assert plot.log_norm is True
    assert plot.vrange == (5, 20)
    assert "norm" in plot.geo_plot_params


def test_vrange_default(sample_geodfr):
    plot = Choropleth(sample_geodfr)
    assert plot.vrange == (0.0, 160.0)


def test_vrange_custom(sample_geodfr):
    plot = Choropleth(sample_geodfr, vrange=(10, 50))
    assert plot.vrange == (10, 50)


def test_vrange_one_param(sample_geodfr):
    plot = Choropleth(sample_geodfr, vrange=(10, None))

    assert plot.vrange == (10, 160.0)

    plot._set_vrange(None, 50)
    assert plot.vrange == (0.0, 50)


def test_set_geo_plot_update(sample_geodfr):

    plot = Choropleth(sample_geodfr, vrange=(5, 20), log_norm=True)
    plot.set_geo_plot(alpha=0.6)

    assert "norm" in plot.geo_plot_params
    assert "alpha" in plot.geo_plot_params


def test_init_both_annotation(sample_geodfr):
    plot = Choropleth(
        sample_geodfr,
        annot_geo_masks={"name": ["A"]},
        annot_geo_filter=lambda s: s.where(s > 10),
    )
    wanted = gpd.GeoDataFrame(
        {
            "name": ["A"],
            "geometry": [Point(0, 0)],
            pd.Timestamp("2020-01-01"): [""],
            pd.Timestamp("2020-01-02"): [""],
            pd.Timestamp("2020-01-03"): ["20.0"],
        },
        geometry="geometry",
    )
    pd.testing.assert_frame_equal(
        wanted,
        plot.dfr.annot_data,
        check_index_type=False,
    )
