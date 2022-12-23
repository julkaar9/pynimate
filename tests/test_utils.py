from pynimate.utils import human_readable


def test_human_readable():
    assert human_readable(20.2333) == "20.23"


def test_human_readable_k():
    assert human_readable(21014, 3) == "21.014K"


def test_human_readable_m():
    assert human_readable(5241725, 1) == "5.2M"
