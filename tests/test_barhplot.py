from pynimate.barhplot import Barhplot


def test_barhplot_xylim(sample_data1_bardfr):
    barhplot = Barhplot(sample_data1_bardfr)
    assert barhplot.xlim == [None, 10] and barhplot.ylim == [0.5, 5.6]


def test_barhplot_generate_column_colors(map_data):
    base_plot = Barhplot.from_df(map_data, "%Y", "MS")
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
    assert base_plot.column_colors == bar_colors


def test_barhplot_ith_bar_attrs(sample_data1):
    barhplot = Barhplot.from_df(sample_data1, "%Y-%m-%d", "6MS")
    bar_ranks = [
        [3.0, 4.0, 2.0, 5.0, 1.0],
        [2.0, 4.0, 1.0, 3.0, 5.0],
        [2.0, 4.0, 1.0, 3.0, 5.0],
        [1.0, 3.0, 5.0, 2.0, 4.0],
        [1.0, 3.0, 5.0, 2.0, 4.0],
    ]
    bar_lengths = [
        [1.0, 2.0, 1.0, 5.0, 1.0],
        [1.5, 2.5, 1.5, 4.0, 2.5],
        [2.0, 3.0, 2.0, 3.0, 4.0],
        [2.5, 3.5, 3.5, 3.5, 4.5],
        [3.0, 4.0, 5.0, 4.0, 5.0],
    ]

    for i in range(barhplot.length):
        ith_attrs = barhplot.get_ith_bar_attrs(i)
        assert list(ith_attrs.bar_rank) == bar_ranks[i]
        assert list(ith_attrs.bar_length) == bar_lengths[i]
