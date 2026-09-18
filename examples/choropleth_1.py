import geopandas as geo
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd

import pynimate as nim
from pynimate.filters import top_n
from pynimate.utils import human_readable

df = pd.read_csv("data/population.csv")
df = df.dropna()

df = df.pivot(
    index=["Entity", "Code"], columns="Year", values="all years"
).reset_index()

mapdf = geo.read_file("data/mapdata/ne_110m_admin_0_countries.shp")

mapdf = mapdf[["ISO_A3", "geometry"]]
mapdf.columns = ["Code", "geometry"]

mapdf = pd.merge(mapdf, df, how="inner", on=["Code"])

mapdf = geo.GeoDataFrame(mapdf, geometry=mapdf.geometry)


canvas = nim.Canvas()
canvas.fig.subplots_adjust(
    left=0.02,
    right=0.91,
    bottom=0.02,
    top=0.98,
)
plot = nim.Choropleth.from_widedf(
    mapdf,
    "%Y",
    "3MS",
    log_norm=True,
    annot_geo_masks={"~Code": ["BGD"]},
    annot_geo_filter=top_n(10),
)
print(plot.dfr.data.shape)
plot.set_title(
    "World Population over the years",
    0.02,
    1.05,
    size=18,
    color="#777777",
    weight=600,
)

plot.set_text(
    "time",
    callback=lambda i, dfr: dfr.time_cols[i].strftime("%Y"),
    x=0.68,
    y=0.2,
    size=23,
    color="#b3df72",
    weight=800,
    ha="center",
    path_effects=[pe.withStroke(linewidth=2, foreground="black")],
)

plot.set_text(
    "sum",
    callback=lambda i, dfr: "".join(
        ("Total Population: ", human_readable(dfr.data[dfr.time_cols[i]].sum()))
    ),
    x=0.6,
    y=0.14,
    size=10,
    color="#777777",
    weight=200,
)
canvas.add_plot(plot)
ani = canvas.animate(interval=200)
canvas.save("population_plot", fps=24, extension="gif")
plt.show()
