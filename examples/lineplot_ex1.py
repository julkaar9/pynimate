import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

import pynimate as nim

for side in ["left", "right", "top", "bottom"]:
    mpl.rcParams[f"axes.spines.{side}"] = False

dir_path = os.path.dirname(os.path.realpath(__file__))


df = pd.read_csv(dir_path + "/data/map.csv").set_index("time")
df = df.drop(columns=["USA"]).iloc[:, :8]

cnv = nim.Canvas()
plot = nim.Lineplot.from_df(
    df, "%Y", "6MS", palettes=["Dark2"], legend=False, grid=False
)
plot.set_time(callback=lambda i, datafier: datafier.data.index[i].year)
plot.set_column_linestyles({"Albania": "dashed"})
cnv.add_plot(plot)
print(plot.column_linestyles)
cnv.animate()
# cnv.save("tt", 24)
plt.show()
