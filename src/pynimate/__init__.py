"""
Pynimate
=====
Python package for statistical data animations.
 Currently provides Bar Chart Race

Basic Example
-------------

It is assumed `pyniamte` is imported as `nim`.
>>> import pynimate as nim
>>> from pynimate.utils import human_readable
>>> import pandas as pd
>>> df = pd.read_csv("sample.csv").set_index("time")
>>> bar = nim.BarBasic(df, '%Y-%m-%d', 'MS')
>>> bar.set_time(callback=lambda i, data, time, rank: time[i].strftime('%b, %Y'))
>>> bar.set_bar_annots(text_callback=human_readable)
>>> bar.animate()
>>> bar.save('sample', fps=24)
"""

__version__ = "1.0.1"

from .bar import BarBasic
from .datafier import Datafier

# __all__ = ["BarBasic", "Datafier"]
