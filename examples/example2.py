import os

import matplotlib as mpl
import matplotlib.ticker as tick
import pandas as pd
from matplotlib import pyplot as plt

import pynimate as nim
from pynimate.utils import human_readable

dir_path = os.path.dirname(os.path.realpath(__file__))

for side in ["left", "right", "top", "bottom"]:
    mpl.rcParams[f"axes.spines.{side}"] = False


def post(self, i):
    self.ax.xaxis.set_major_formatter(
        tick.FuncFormatter(lambda x, pos: human_readable(x))
    )


df = pd.read_csv(dir_path + "/data/map.csv").set_index("time")
cnv = nim.Canvas()
dfx = pd.DataFrame(
    {
        "time": ["2012", "2013", "2014"],
        "col1": [1, 2, 3],
        "col2": [3, 2, 1],
    }
).set_index("time")
bar = nim.Barhplot.from_df(df, "%Y", "MS", post_update=post, grid=False)
bar.set_title("Top 10 Richest Person in the World (yearly)")
bar.set_xlabel("Net Worth in Billion USD")
bar.set_time(callback=lambda i, dfr: dfr.data.index[i].year)
bar.set_bar_annots(text_callback=human_readable)

cnv.add_plot(bar)
cnv.animate()
plt.show()
# cnv.save("example1", 24, "gif")
