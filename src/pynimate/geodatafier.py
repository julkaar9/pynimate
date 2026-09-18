from __future__ import annotations

from numbers import Number
from typing import TYPE_CHECKING, Callable

import pandas as pd

from pynimate.datafier import BaseDatafier
from pynimate.utils import normalize_time_col

if TYPE_CHECKING:
    import geopandas as gpd


def ordered_difference(base_list: list, not_in_list: list) -> list:
    not_in_list_set = set(not_in_list)
    return [c for c in base_list if c not in not_in_list_set]


class GeoDatafier(BaseDatafier):
    def __init__(
        self,
        data: gpd.GeoDataFrame,
        time_format: str,
        ip_freq: str,
        ip_method: str = "linear",
    ) -> None:
        """
        Preprocesses wide-format geographic time-series data for choropleth animations.

        The input data must be a GeoDataFrame containing a valid ``geometry`` column
        and time-series columns in wide format. The detected time columns are
        interpolated to the specified temporal frequency while all remaining columns
        are preserved.

        -------
        Expected input format::
        ```text
            geometry      NAME       ISO_A3    2020    2021    2022
            -------------------------------------------------------
            POLYGON(...)  India      IND       1380    1395    1410
            POLYGON(...)  China      CHN       1439    1441    1443
            POLYGON(...)  Japan      JPN        126     125     124
        ```
        Parameters
        ----------
        data : geopandas.GeoDataFrame
            Input GeoDataFrame containing geographic features and time-series
            columns.

        time_format : str
            Datetime format used to identify and parse time columns.
            For example, ``"%Y"``, ``"%Y-%m"``, or ``"%Y-%m-%d"``.

        ip_freq : str
            Interpolation frequency passed to ``pandas.date_range()``.
            For example, ``"MS"``, ``"5D"``, or ``"1H"``.

        ip_method : str, optional
            Interpolation method passed to ``DataFrame.interpolate()``,
            by default ``"linear"``.
        """
        self.raw_data = data
        self.time_format = time_format
        self.ip_freq = ip_freq
        self.ip_method = ip_method

        self.raw_time_cols, self.raw_time_idxs = self.get_time_cols(data, time_format)
        self.annot_data = None

        if len(self.raw_time_cols) == 0:
            raise ValueError("Failed to detect any time column")
        if len(self.raw_time_cols) < 2:
            raise ValueError("Data must contain at least 2 time columns")

        self.static_cols = self.get_static_cols(self.raw_data, self.raw_time_cols)
        self.data = self.interpolate_uneven(
            data, self.raw_time_cols, self.time_format, self.ip_freq, self.ip_method
        )
        self.time_cols = ordered_difference(self.data.columns, self.static_cols)

    def interpolate_uneven(
        self,
        data: gpd.GeoDataFrame,
        time_cols: list[str],
        time_format: str,
        ip_freq: str = "5D",
        ip_method: str = "time",
    ) -> gpd.GeoDataFrame:
        """
        Interpolates wide-format temporal data to a uniform time frequency.

        The input time columns are transposed into a datetime index, expanded to the
        requested interpolation frequency, interpolated, and finally converted back
        to wide format while preserving all non-temporal columns.

        Parameters
        ----------
        data : geopandas.GeoDataFrame
            Input GeoDataFrame containing static columns and wide-format
            time-series columns.

        time_cols : list[str]
            Names of the time-series columns to interpolate.

        ip_freq : str, optional
            Target interpolation frequency passed to ``pandas.date_range()``,
            by default ``"5D"``.

        ip_method : str, optional
            Interpolation method passed to ``DataFrame.interpolate()``,
            by default ``"time"``.

        Returns
        -------
        geopandas.GeoDataFrame
            GeoDataFrame containing the interpolated time-series columns along
            with the original static columns.
        """
        num = data[time_cols]
        num = num.T
        num.index = pd.to_datetime(num.index, format=time_format)
        new_ind = pd.date_range(num.index.min(), num.index.max(), freq=ip_freq)
        new_series = pd.Series(
            [0] * len(new_ind), index=new_ind, name="new_ind"
        ).to_frame()
        num = (
            new_series.join(num, how="outer")
            .drop("new_ind", axis=1)
            .sort_index()
            .interpolate(method=ip_method)
        )
        data = data[ordered_difference(data.columns, time_cols)].join(num.T)
        return data

    def get_time_cols(
        self, data: pd.DataFrame, time_format: str
    ) -> tuple[list[str], list[int]]:
        """Identifies time-series columns from the dataframe.

        Parameters
        ----------
        data : pandas.DataFrame
            Input dataframe.

        time_format : str
            Datetime format used to identify time columns.

        Returns
        -------
        tuple[list[str], list[int]]
            Detected time column names and their corresponding indices.
        """
        time_col_idxs = []

        for i, col in enumerate(data.columns):
            try:
                _ = normalize_time_col(col, time_format)
                time_col_idxs.append(i)
            except ValueError:
                pass
        time_cols = [data.columns[i] for i in time_col_idxs]
        return time_cols, time_col_idxs

    def get_static_cols(
        self, data: gpd.GeoDataFrame, time_columns: list[str]
    ) -> list[str]:
        """Returns all non-temporal columns.

        Parameters
        ----------
        data : geopandas.GeoDataFrame
            Input GeoDataFrame.

        time_columns : list[str]
            Names of the detected time columns.

        Returns
        -------
        list[str]
            List containing the static (non-time) column names.
        """
        time_cols_set = set(time_columns)
        static_cols = [col for col in data.columns if col not in time_cols_set]
        return static_cols

    def _get_masked_geo_annots(self, col_masks: dict[str, list]):
        """Internal helper to filter geometry annotations using column masks.

        Filters the annotation data by retaining rows whose values match the
        provided values for each specified column. Multiple column masks are
        applied sequentially.

        Parameters
        ----------
        col_masks : dict[str, list]
            Mapping of column names to the values to retain. Each column is
            filtered using ``Series.isin()``.
        """

        self.annot_data = (
            self.data.copy() if self.annot_data is None else self.annot_data
        )
        for col_name, col_mask in col_masks.items():
            exclude = col_name.startswith("~")
            col_name = col_name.lstrip("~")
            mask = self.annot_data[col_name].isin(col_mask)
            self.annot_data = self.annot_data.loc[~mask if exclude else mask]

    def _get_filtered_geo_annots(
        self, filter_callback: Callable[[pd.Series[Number]], pd.Series[Number]]
    ):
        """Internal helper to cache geometry annotations using a filter callback.

        Applies ``filter_callback`` independently to each time column. Values
        replaced with ``NaN`` are omitted from geometry annotations.

        Parameters
        ----------
        filter_callback : Callable[[pd.Series], pd.Series]
            Callback that receives a time column as a Series and returns the
            filtered Series.
        """
        self.annot_data = (
            self.data.copy() if self.annot_data is None else self.annot_data
        )
        self.annot_data[self.time_cols] = self.annot_data[self.time_cols].apply(
            filter_callback
        )

    def _format_geo_annots(self, geo_annot_formatter: Callable[[Number], str]):
        """Internal helper to format cached geometry annotations.

        Applies the formatter to every annotation value and caches the resulting
        strings for use during rendering.

        Parameters
        ----------
        geo_annot_formatter : Callable[[Number], str]
            Function used to convert numeric values into annotation strings.
        """
        self.annot_data[self.time_cols] = self.annot_data[self.time_cols].map(
            geo_annot_formatter
        )
