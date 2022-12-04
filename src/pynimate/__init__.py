"""
Pynimate
=====
Python package for statistical data animations.

Bar Example
-------------

It is assumed `pyniamte` is imported as `nim`.
>>> import pynimate as nim
>>> from pynimate.utils import human_readable
>>> import pandas as pd
>>> df = pd.read_csv("sample.csv").set_index("time")
>>> nim.Canvas()
>>> bar = nim.BarBasic(df, '%Y-%m-%d', 'MS')
>>> bar.set_time(callback=lambda i, datafier: datafier.data.index[i].year)
>>> bar.set_bar_annots(text_callback=human_readable)
>>> cnv.add_plot(bar)
>>> cnv.animate()
>>> cnv.save('sample', fps=24)
"""

__version__ = "1.0.1"

from .canvas import Canvas
from .bar import BarBasic
from .datafier import Datafier
