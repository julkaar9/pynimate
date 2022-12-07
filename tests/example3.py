import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

dir_path = os.path.dirname(os.path.realpath(__file__))
import pynimate as nim


def post_update(ax, i, datafier, bar_attr):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_facecolor("#001219")

    # annotates continents next to bars
    for bar, x, y in zip(
        bar_attr.top_bars,
        bar_attr.bar_length,
        bar_attr.bar_rank,
    ):
        ax.text(
            x - 0.3,
            y,
            datafier.col_var.loc[bar, "continent"],
            ha="right",
            color="k",
            size=12,
        )


df = pd.read_csv(dir_path + "/data/sample.csv").set_index("time")
col = pd.DataFrame(
    {
        "columns": ["Afghanistan", "Angola", "Albania", "USA", "Argentina"],
        "continent": ["Asia", "Africa", "Europe", "N America", "S America"],
    }
).set_index("columns")
bar_cols = {
    "Afghanistan": "#2a9d8f",
    "Angola": "#e9c46a",
    "Albania": "#e76f51",
    "USA": "#a7c957",
    "Argentina": "#e5989b",
}

cnv = nim.Canvas(figsize=(12.8, 7.2), facecolor="#001219")
bar = nim.Barplot(
    df, "%Y-%m-%d", "3d", post_update=post_update, rounded_edges=True, grid=False
)
bar.add_var(col_var=col)
bar.set_bar_color(bar_cols)
bar.set_title("Sample Title", color="w", weight=600)
bar.set_xlabel("xlabel", color="w")
bar.set_time(
    callback=lambda i, datafier: datafier.data.index[i].strftime("%b, %Y"), color="w"
)
bar.set_text(
    "sum",
    callback=lambda i, datafier: f"Total :{np.round(datafier.data.iloc[i].sum(), 2)}",
    size=20,
    x=0.72,
    y=0.20,
    color="w",
)
bar.set_bar_annots(color="w", size=13)
bar.set_xticks(colors="w", length=0, labelsize=13)
bar.set_yticks(colors="w", labelsize=13)
bar.set_bar_border_props(
    edge_color="black", pad=0.1, mutation_aspect=1, radius=0.2, mutation_scale=0.6
)
cnv.add_plot(bar)
cnv.animate()
# plt.show()
cnv.save("example3", 24, "gif")
