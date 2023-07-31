from pynimate.lineplot import Lineplot


def test_lineplot_linestyle(sample_data1_linedfr):
    plot = Lineplot(sample_data1_linedfr)
    linestyles = {
        "Afghanistan": "solid",
        "Angola": "solid",
        "Albania": "solid",
        "USA": "solid",
        "Argentina": "solid",
    }

    assert plot.column_linestyles == linestyles


def test_lineplot_linestyle_dict(sample_data1_linedfr):
    plot = Lineplot(sample_data1_linedfr)
    plot.set_column_linestyles({"Albania": "dashed"})
    linestyles = {
        "Afghanistan": "solid",
        "Angola": "solid",
        "Albania": "dashed",
        "USA": "solid",
        "Argentina": "solid",
    }

    assert plot.column_linestyles == linestyles
