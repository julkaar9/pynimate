import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import pandas as pd

import pynimate as nim
from pynimate.utils import human_readable

for side in ["left", "right", "top", "bottom"]:
    mpl.rcParams[f"axes.spines.{side}"] = False
mpl.rcParams["figure.facecolor"] = "#001219"
mpl.rcParams["axes.facecolor"] = "#001219"
mpl.rcParams["savefig.facecolor"] = "#001219"

dir_path = os.path.dirname(os.path.realpath(__file__))


def post(self, i):
    self.ax.yaxis.set_major_formatter(
        tick.FuncFormatter(lambda x, pos: human_readable(x))
    )


df = pd.read_csv(dir_path + "/data/covid_IN.csv").set_index("time")
df = df["2020-05-01":"2021-01-01"]
cnv = nim.Canvas()
dfr = nim.LineDatafier(df, "%Y-%m-%d", "12h")
plot = nim.Lineplot(
    dfr,
    post_update=post,
    palettes=["Set3"],
    scatter_markers=False,
    legend=True,
    fixed_ylim=True,
    grid=False,
)
plot.set_column_linestyles({"cured": "dashed"})
plot.set_title("Covid cases India(2020)", y=1.05, color="w", weight=600)
plot.set_xlabel("date", color="w", size=11)
plot.set_time(
    callback=lambda i, datafier: datafier.data.index[i].strftime("%d %b, %Y"),
    color="w",
    size=13,
)
plot.set_line_annots(lambda col, val: f"({human_readable(val)})", color="w")
plot.set_legend(labelcolor="w")
plot.set_text(
    "sum",
    callback=lambda i, datafier: f"Total cases :{human_readable(datafier.data.cases.iloc[:i+1].sum() )}",
    size=10,
    x=0.84,
    y=0.20,
    color="w",
)
plot.set_xticks(colors="w", length=0, labelsize=10)
plot.set_yticks(colors="w", labelsize=10)
cnv.add_plot(plot)
cnv.animate(interval=20)
cnv.save("lineplot_dark", 24)
plt.show()
