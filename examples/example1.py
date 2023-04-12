import pandas as pd
from matplotlib import pyplot as plt

import pynimate as nim

df = pd.DataFrame(
    {
        "time": ["1960-01-01", "1961-01-01", "1962-01-01"],
        "Afghanistan": [1, 2, 3],
        "Angola": [2, 3, 4],
        "Albania": [1, 2, 5],
        "USA": [5, 3, 4],
        "Argentina": [1, 4, 5],
    }
).set_index("time")

cnv = nim.Canvas()
bar = nim.Barhplot.from_df(df, "%Y-%m-%d", "3d", rounded_edges=True)
bar.set_time(callback=lambda i, datafier: datafier.data.index[i].year)
cnv.add_plot(bar)
cnv.animate()
plt.show()
# cols = ["r", "g", "b"]
# vals = [1, 2, 2.5]
# ranks = [1, 2, 2.5]
# col_zorder = {"r": 1, "g": 3, "b": 2}
# fig, ax = plt.subplots()
# ax.barh(ranks, vals, tick_label=cols, color=cols)
# for z, patch in zip(col_zorder.values(), ax.patches):
#     patch.set_zorder(z)
#     print(patch, patch.zorder)
# print()
# for z, patch in zip(col_zorder.values(), ax.patches):
#     print(patch, patch.zorder)

# plt.show()
