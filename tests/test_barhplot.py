from pynimate.barhplot import Barhplot


def test_barhplot_xylim(sample_data1_bardfr):
    barhplot = Barhplot(sample_data1_bardfr)
    assert barhplot.xlim == [None, 10] and barhplot.ylim == [0.5, 5.6]
