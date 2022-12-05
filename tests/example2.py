from matplotlib import pyplot as plt
import pandas as pd
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
cnv = nim.Canvas(figsize=(12.8, 7.2))
bar = nim.Barplot(df, "%Y-%m-%d", "2d")
bar.set_time(callback=lambda i, datafier: datafier.data.index[i].year)
cnv.add_plot(bar)
cnv.animate()
# cnv.save(
#     "exm2",
#     24,
#     "gif",
# )
plt.show()
