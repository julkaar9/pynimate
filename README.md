![](https://github.com/julkaar9/pynimate/blob/gh-pages/assets/pynimate_logo2.png)

# Pynimate

[![PyPI](https://img.shields.io/pypi/v/pynimate?color=orange)](https://pypi.org/project/pynimate/)
[![Downloads](https://static.pepy.tech/personalized-badge/pynimate?period=total&units=international_system&left_color=grey&right_color=red&left_text=Downloads)](https://pepy.tech/project/pynimate) 
![Tests](https://github.com/julkaar9/pynimate/actions/workflows/tests.yml/badge.svg)
[![License](https://img.shields.io/pypi/l/pynimate?color=green)](https://github.com/julkaar9/pynimate/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)  

Python package for statistical data animations.
![](https://github.com/julkaar9/pynimate/blob/main/docs/assets/example3.gif)

## Installation
### with pip
Pynimate is avaialbe at [pypi](https://pypi.org/project/pynimate/)
``` sh
pip install pynimate
```

## How to use
Pynimate expects pandas dataframe formatted in this manner:  
Where the time column is set to index.
```python
time, col1, col2, col3
2012   1     2     1
2013   1     1     2
2014   2     1.5   3
2015   2.5   2     3.5
```
## Bar Chart Example
```python
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
bar = nim.Barhplot.from_df(df, "%Y-%m-%d", "2d")
bar.set_time(callback=lambda i, datafier: datafier.data.index[i].year)
cnv.add_plot(bar)
cnv.animate()
plt.show()
``` 
## Documentation
The official documentation : https://julkaar9.github.io/pynimate/

## License
[MIT License (MIT)](LICENSE)