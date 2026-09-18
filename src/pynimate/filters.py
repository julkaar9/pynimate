import numpy as np


def top_n(n: int = 10):
    return lambda col: col.where(col >= col.nlargest(n).min(), np.nan)
