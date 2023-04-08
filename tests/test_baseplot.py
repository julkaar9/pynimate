import pytest

from pynimate.baseplot import Baseplot


def test_baseplot_generate_column_colors(sample_data1_basedfr):
    base_plot = Baseplot(sample_data1_basedfr)
    column_colors = {
        "Afghanistan": (0.267968, 0.223549, 0.512008),
        "Angola": (0.190631, 0.407061, 0.556089),
        "Albania": (0.127568, 0.566949, 0.550556),
        "USA": (0.20803, 0.718701, 0.472873),
        "Argentina": (0.565498, 0.84243, 0.262877),
    }
    assert base_plot.generate_column_colors() == column_colors


def test_baseplot_set_column_colors_str(sample_data1_basedfr):
    base_plot = Baseplot(sample_data1_basedfr)
    base_plot.set_column_colors("#FF2C55")
    column_colors = {
        "Afghanistan": "#FF2C55",
        "Angola": "#FF2C55",
        "Albania": "#FF2C55",
        "USA": "#FF2C55",
        "Argentina": "#FF2C55",
    }
    assert base_plot.column_colors == column_colors


def test_baseplot_set_column_colors_list(sample_data1_basedfr):
    base_plot = Baseplot(sample_data1_basedfr)
    base_plot.set_column_colors(
        [
            "#C41E3D",
            "#7D1128",
            "#FF2C55",
            "#3C0919",
            "#E2294F",
        ]
    )
    column_colors = {
        "Afghanistan": "#C41E3D",
        "Angola": "#7D1128",
        "Albania": "#FF2C55",
        "USA": "#3C0919",
        "Argentina": "#E2294F",
    }
    assert base_plot.column_colors == column_colors


def test_baseplot_set_column_colors_dict(sample_data1_basedfr):
    base_plot = Baseplot(sample_data1_basedfr)
    base_plot.set_column_colors(
        {
            "Afghanistan": "#C41E3D",
            "Angola": "#7D1128",
            "Albania": "#FF2C55",
            "USA": "#3C0919",
            "Argentina": "#E2294F",
        }
    )
    column_colors = {
        "Afghanistan": "#C41E3D",
        "Angola": "#7D1128",
        "Albania": "#FF2C55",
        "USA": "#3C0919",
        "Argentina": "#E2294F",
    }
    assert base_plot.column_colors == column_colors


def test_baseplot_set_column_color_err_length(sample_data1_basedfr):
    with pytest.raises(AssertionError):
        base_plot = Baseplot(sample_data1_basedfr)
        column_colors = [
            "#2a9d8f",
            "#e9c46a",
            "#e76f51",
            "#a7c957",
        ]
        base_plot.set_column_colors(column_colors)


def test_baseplot_set_column_color_err_col_mismatch(sample_data1_basedfr):
    with pytest.raises(ValueError):
        bar = Baseplot(sample_data1_basedfr)
        bar_colors = {
            "India": "#2a9d8f",
            "Angola": "#e9c46a",
            "Albania": "#e76f51",
            "USA": "#a7c957",
            "Argentina": "#e5989b",
        }
        bar.set_column_colors(bar_colors)


def test_baseplot_set_column_color_err_type(sample_data1_basedfr):
    with pytest.raises(TypeError):
        bar = Baseplot(sample_data1_basedfr)
        bar_colors = set(
            [
                "#2a9d8f",
                "#e9c46a",
                "#e76f51",
                "#a7c957",
                "#e5989b",
            ]
        )

        bar.set_column_colors(bar_colors)


def test_baseplot_xylim(sample_data1_basedfr):
    base_plot = Baseplot(sample_data1_basedfr)
    xmin, xmax = base_plot.xlim
    ymin, ymax = base_plot.ylim
    assert xmin is None and ymin is None
    assert xmax.strftime("%Y-%m-%d") == "1962-01-01" and ymax == 5


def test_baseplot_text_structure(sample_data1_basedfr):
    base_plot = Baseplot(sample_data1_basedfr)
    base_plot.set_title("Title")
    base_plot.set_xlabel("Xlabel")
    base_plot.set_time()
    for text in base_plot.text_collection.values():
        assert isinstance(text, tuple)
        assert text[0] is None or callable(text[0])
        assert isinstance(text[1], dict)


def test_baseplot_set_text_error_empty_text(sample_data1_basedfr):
    with pytest.raises(AssertionError):
        bar = Baseplot(sample_data1_basedfr)
        bar.set_text("text1")


def test_baseplot_set_text_priority(sample_data1_basedfr):
    bar = Baseplot(sample_data1_basedfr)
    bar.set_text("text1", text="Test", callback=lambda *args: "Test")
    assert "s" not in bar.text_collection["text1"][1]


def test_baseplot_remove_text(sample_data1_basedfr):
    bar = Baseplot(sample_data1_basedfr)
    bar.set_text("text1", text="Test1")
    bar.set_text("text2", text="Test2")
    bar.set_text("text3", text="Test3")

    bar.remove_text(["text1", "text2"])
    assert list(bar.text_collection.keys()) == ["text3"]
