from typing import Union

import numpy as np
import pandas as pd


def human_readable(num: Union[float, int], precision: int = 2, *args) -> str:
    """Converts large numeric values(>10^3) into human readable strings.
    `ie. 1000 -> 1k`,
    `1000000 -> 1M`, etc.

    Parameters
    ----------
    num : Union[float, int]
        Numeric value
    precision : int, optional
        Rounding precision, by default 2

    Returns
    -------
    str
        Human readable numeric string
    """
    if pd.isna(num):
        return ""

    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    return f'{np.round(num, precision)}{["", "K", "M", "B", "T", "Q"][magnitude]}'


def normalize_time_col(col: Union[any, str], fmt: str):
    if isinstance(col, str):
        return pd.to_datetime(col, format=fmt)
    return col
