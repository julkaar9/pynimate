import os

dir_path = os.path.dirname(os.path.realpath(__file__))
from matplotlib import pyplot as plt
import matplotlib.ticker as tick
import pandas as pd
import pynimate as nim
from pynimate.utils import human_readable


def post(ax, *args):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_formatter(tick.FuncFormatter(human_readable))


cnv = nim.Canvas()
df = pd.read_csv(dir_path + "/data/map.csv").set_index("time")
bar = nim.Barplot(df, "%Y", "MS", post_update=post, grid=False)
print(df.shape)
bar.set_title("Top 10 Richest Person in the World (yearly)")
bar.set_xlabel("Net Worth in Billion USD")
bar.set_time(callback=lambda i, datafier: datafier.data.index[i].year)
bar.set_bar_annots(text_callback=human_readable)
cnv.add_plot(bar)
cnv.animate()
# cnv.save("example1", 24, "mp4")
plt.show()
