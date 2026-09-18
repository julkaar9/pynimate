import geopandas as geo
import matplotlib as mpl
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from shapely import wkt

import pynimate as nim
from pynimate.utils import human_readable

mpl.rcParams["figure.facecolor"] = "#000B0F"
mpl.rcParams["axes.facecolor"] = "#000B0F"
mpl.rcParams["savefig.facecolor"] = "#000B0F"
data = pd.read_csv("data/mapdata.csv")

print(data.columns)
data = data[
    [
        "index",
        "objectid",
        "statecode",
        "statename",
        "distcode",
        "distname",
        "distarea",
        "st_areasha",
        "st_lengths",
        "geometry",
        "2009-01-01 00:00:00",
        "2009-02-01 00:00:00",
        "2009-03-01 00:00:00",
        "2009-04-01 00:00:00",
        "2009-05-01 00:00:00",
        "2009-06-01 00:00:00",
        "2009-07-01 00:00:00",
        "2009-08-01 00:00:00",
        "2009-09-01 00:00:00",
        "2009-10-01 00:00:00",
        "2009-11-01 00:00:00",
        "2009-12-01 00:00:00",
        "2010-01-01 00:00:00",
        "2010-02-01 00:00:00",
        "2010-03-01 00:00:00",
        "2010-04-01 00:00:00",
        "2010-05-01 00:00:00",
        "2010-06-01 00:00:00",
        "2010-07-01 00:00:00",
        "2010-08-01 00:00:00",
        "2010-09-01 00:00:00",
        "2010-10-01 00:00:00",
        "2010-11-01 00:00:00",
        "2010-12-01 00:00:00",
    ]
]
data["geometry"] = data["geometry"].apply(wkt.loads)
data = geo.GeoDataFrame(data, geometry=data.geometry)

canvas = nim.Canvas()
geoplot = nim.Choropleth.from_widedf(
    data,
    "%Y-%m-%d %H:%M:%S",
    "36h",
    vrange=(0, 700),
    cbar_unit="mm",
    cmap="viridis",
)
geoplot.set_title(
    "India's District wise Monthly Rainfall",
    0.02,
    1.05,
    size=18,
    color="#f5f5f5",
    weight=600,
)

geoplot.set_text(
    "time",
    callback=lambda i, dfr: dfr.time_cols[i].strftime("%b, %Y"),
    x=0.8,
    y=0.3,
    size=23,
    color="#f5f5f5",
    weight=800,
    ha="center",
    path_effects=[pe.withStroke(linewidth=2, foreground="black")],
)

geoplot.set_text(
    "sum",
    callback=lambda i, dfr: "".join(
        ("Monthly Total: ", human_readable(dfr.data[dfr.time_cols[i]].sum()))
    ),
    x=0.68,
    y=0.24,
    size=10,
    color="#777777",
    weight=200,
)

geoplot.set_nan_geo(color="#04212D")
geoplot.set_cbar_ticks(labelcolor="#f5f5f5", labelsize=9)

canvas.add_plot(geoplot)
ani = canvas.animate(interval=200)
canvas.save("district_rainfall", fps=24, extension="gif")
plt.show()
