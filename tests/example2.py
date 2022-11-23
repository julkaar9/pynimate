from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os

dir_path = os.path.dirname(os.path.realpath(__file__)) 
import pynimate as nim
from pynimate.utils import human_readable

df = pd.read_csv(dir_path + "/data/sample.csv").set_index("time")
bar = nim.BarBasic(df, "%Y-%m-%d", "2d")
bar.set_time(callback=lambda i, data, time, rank: time[i].strftime('%b, %Y')) 
bar.animate()
plt.show() 
 