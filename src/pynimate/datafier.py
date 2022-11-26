import numpy as np
import pandas as pd

import seaborn as sns


class Datafier:
    def __init__(
        self,
        data: pd.DataFrame,
        time_format: str,
        ip_freq: str,
        ip_frac: float = 0.5,
        n_bars: int = 10,
        palettes: list[str] = ["viridis"],
    ) -> None:
        """Contains data preparation modules, which includes interpolation, rank generation, color_generation

        Parameters
        ----------
        data : pd.DataFrame
            The data to be prepared, should be in this format where time is set to index.
            ```
                Example:
                >>> time  col1 col2 col3 ...
                >>> 2012   1    0    2
                >>> 2013   2    3    1
            ```
        time_format : str
            Index datetime format
        ip_freq : str
            Interpolation frequency
        ip_frac : float, optional
            Interpolation fraction (check end of docstring), by default 0.5
        n_bars : int, optional
            Number of bars to be visible on the plot Defaults to 10 or less, by default 10
        palettes : list[str], optional
            List of color palettes to generate bar
                colors. Defaults to ["viridis"], by default ["viridis"]

        ```
            ip_frac is the percentage of NaN values to be linearly interpolated\n
            Consider this example
            >>>               a    b
            >>> date
            >>> 2021-11-13  1.0  4.0
            >>> 2021-11-14  NaN  NaN
            >>> 2021-11-15  NaN  NaN
            >>> 2021-11-16  NaN  NaN
            >>> 2021-11-17  NaN  NaN
            >>> 2021-11-18  2.0  6.0

            with ip_frac set to 0.5, 50% of NaN's will be linearly interpolated while\n
            the rest will back filled.

            >>>               a    b
            >>> 2021-11-13  1.000000  4.000000  << original value ---------------
            >>> 2021-11-14  1.333333  4.666667                                   |
            >>> 2021-11-15  1.666667  5.333333                                   |  50% linearly
            >>> 2021-11-16  2.000000  6.000000  <- linear interpolation          |  interpolated
            >>> 2021-11-17  2.000000  6.000000      upto here                    |  rest are filled.
            >>> 2021-11-18  2.000000  6.000000  << original value (upper bound)--
            This adds some stability in the barChartRace and reduces constantly shaking of bars.
        ```
        """

        self.raw_data = data
        self.ip_freq = ip_freq
        self.ip_frac = ip_frac
        self.n_bars = min(n_bars, len(self.raw_data.columns))
        self.palettes = palettes
        self.raw_data.index = pd.to_datetime(self.raw_data.index, format=time_format)
        self.data, self.df_ranks = self.get_prepared_data(self.raw_data, self.ip_frac)
        self.top_cols = self.get_top_cols()
        self.bar_colors = self.get_bar_colors()

    def prepared_data(
        self,
    ) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
        """_summary_

        Returns
        -------
        tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]
            Tuple containing the following data
            ```
                pd.DataFrame: The actual data interpolated
                pd.DataFrame: Dataframe containing bar ranks
                dict[str, str]: Dict containing column to color mapping
            ```
        """
        self.data.columns = list(self.data.columns)
        self.df_ranks.columns = list(self.df_ranks.columns)
        return self.data, self.df_ranks, self.bar_colors

    def interpolate(
        self, data: pd.DataFrame, freq: str, method: str = "linear"
    ) -> pd.DataFrame:
        num_cols = data.select_dtypes("number").columns
        num_data = data[num_cols]
        # num_data = num_data.T
        num_data.index = pd.to_datetime(num_data.index)
        new_ind = pd.date_range(num_data.index.min(), num_data.index.max(), freq=freq)
        num_data = num_data.reindex(new_ind).interpolate(method=method)
        data = data[data.select_dtypes(exclude="number").columns].join(
            num_data, how="right"
        )
        return data

    def intepolateEven(
        self, data: pd.DataFrame, freq: str, method: str = "linear"
    ) -> pd.DataFrame:
        """Interpolates the given dataframe according to the frequency

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe contaning the data
        freq : str
            Interpolation frequency
        method : str, optional
            Interpolation method, by default "linear"

        Returns
        -------
        pd.DataFrame
            Interpolated dataframe
        """
        ncols = data.select_dtypes("number").columns
        num_data = data[ncols]
        new_ind = pd.date_range(num_data.index.min(), num_data.index.max(), freq=freq)
        new_ser = pd.Series(
            [0] * len(new_ind), index=new_ind, name="new_ind"
        ).to_frame()
        num_data = (
            new_ser.join(num_data, how="outer")
            .drop("new_ind", axis=1)
            .sort_index()
            .interpolate(method=method)
        )
        data = data[data.select_dtypes(exclude="number").columns].join(
            num_data, how="right"
        )
        return data

    def get_prepared_data(
        self, data: pd.DataFrame, ip_frac: float = 0.5
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Creates interpolated data and column ranks

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe contaning the data
        ip_frac : float, optional
            Interpolation fraction, by default 0.5

        Returns
        -------
        tuple[pd.DataFrame, pd.DataFrame]
            Tuple containing the following data
            ```
                pd.DataFrame: Interpolated data values
                pd.DataFrame: Interpolated column ranks
            ```
        """

        df_ranks = data.rank(axis=1, method="first", ascending=False).clip(
            upper=self.n_bars + 1
        )

        df_ranks = self.n_bars + 1 - df_ranks
        data.replace(np.nan, 0, inplace=True)
        df_ranks.replace(np.nan, -1, inplace=True)
        data = self.intepolateEven(data, freq=self.ip_freq)
        df_ranks = df_ranks.reindex(data.index)
        # calculate the no of nans in each interval
        # see https://stackoverflow.com/questions/69951782/pandas-interpolate-with-condition
        if ip_frac != 0:
            t = df_ranks.iloc[:, 0]
            # total length
            x = len(t)
            # no of nans
            z = t.isna().sum()
            # no of non-nans
            y = x - z
            # no of nans in each interval
            w = z / (y - 1)
            if w * ip_frac > 0:
                df_ranks = df_ranks.interpolate(
                    method="bfill", limit=int(np.ceil(w * ip_frac))
                )
        df_ranks = df_ranks.interpolate()
        return (data, df_ranks)

    def get_top_cols(self) -> list[int]:
        """Selects columns that a rank < n_bars in any timestamp

        Returns
        -------
        list[int]
            List of columns that will appear in the animation atleast once
        """
        top_cols = self.df_ranks.max(axis=0)
        top_cols = top_cols[top_cols >= 1]
        return list(top_cols.index)

    def get_bar_colors(self) -> dict[str, str]:
        """Generates bar (column) colors based on the given color palettes

        Returns
        -------
        dict[str, str]
            dict containing column to color mapping
        """
        all_colors = []
        for palette in self.palettes:
            all_colors.extend(
                list(
                    sns.color_palette(
                        palette, int(np.ceil(len(self.top_cols) / len(self.palettes)))
                    )
                )
            )

        return {column: color for column, color in zip(self.top_cols, all_colors)}
