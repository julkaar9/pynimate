# Legacy tests for barplot, will be removed in 2.0.0
import pytest

from pynimate.bar import Barplot


def test_barplot_set_bar_color_list(sample_data1):
    bar = Barplot(sample_data1, "%Y-%m-%d", "3MS")
    bar_colors_list = [
        "#2a9d8f",
        "#e9c46a",
        "#e76f51",
        "#a7c957",
        "#e5989b",
    ]
    bar_colors = {
        "Afghanistan": "#2a9d8f",
        "Angola": "#e9c46a",
        "Albania": "#e76f51",
        "USA": "#a7c957",
        "Argentina": "#e5989b",
    }
    bar.set_bar_color(bar_colors_list)
    assert bar.datafier.bar_colors == bar_colors


def test_barplot_set_bar_color_dict(sample_data1):
    bar = Barplot(sample_data1, "%Y-%m-%d", "3MS")
    bar_colors = {
        "Afghanistan": "#2a9d8f",
        "Angola": "#e9c46a",
        "Albania": "#e76f51",
        "USA": "#a7c957",
        "Argentina": "#e5989b",
    }
    bar.set_bar_color(bar_colors)
    assert bar.datafier.bar_colors == bar_colors


def test_barplot_set_bar_color_error_length(sample_data1):
    with pytest.raises(AssertionError):
        bar = Barplot(sample_data1, "%Y-%m-%d", "3MS")
        bar_colors = [
            "#2a9d8f",
            "#e9c46a",
            "#e76f51",
            "#a7c957",
        ]
        bar.set_bar_color(bar_colors)
        assert bar.datafier.bar_colors == bar_colors


def test_barplot_set_bar_color_error_col_mismatch(sample_data1):
    with pytest.raises(AssertionError):
        bar = Barplot(sample_data1, "%Y-%m-%d", "3MS")
        bar_colors = {
            "India": "#2a9d8f",
            "Angola": "#e9c46a",
            "Albania": "#e76f51",
            "USA": "#a7c957",
            "Argentina": "#e5989b",
        }
        bar.set_bar_color(bar_colors)
        assert bar.datafier.bar_colors == bar_colors


def test_barplot_set_text_error_empty_text(sample_data1):
    with pytest.raises(AssertionError):
        bar = Barplot(sample_data1, "%Y-%m-%d", "3MS")
        bar.set_text("text1")


def test_barplot_set_text_priority(sample_data1):
    bar = Barplot(sample_data1, "%Y-%m-%d", "3MS")
    bar.set_text("text1", text="Test", callback=lambda *args: "Test")
    assert "s" not in bar.text_collection["text1"][1]


def test_barplot_remove_text(sample_data1):
    bar = Barplot(sample_data1, "%Y-%m-%d", "3MS")
    bar.set_text("text1", text="Test1")
    bar.set_text("text2", text="Test2")
    bar.set_text("text3", text="Test3")

    bar.remove_text(["text1", "text2"])
    assert list(bar.text_collection.keys()) == ["time", "text3"]
