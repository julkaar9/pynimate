from typing import Callable, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from pynimate.datafier import BaseDatafier


class Baseplot:
    def __init__(
        self,
        datafier: BaseDatafier,
        palettes: list[str] = ["viridis"],
        post_update: Callable[[__qualname__, int], None] = lambda self, i: None,
        fixed_xlim=True,
        fixed_ylim=True,
        xticks=True,
        yticks=True,
        grid=True,
    ) -> None:
        """General Chart animation module that requires a valid time index.The data
        should be in this format where time is set to index
            ```
                Example:
                >>> time  col1 col2 col3 ...
                >>> 2012   1    0    2
                >>> 2013   2    3    1
            ```
        Parameters
        ----------
        datafier : BaseDatafier
            The datafier instance
        palettes : list[str], optional
            List of color palettes to generate bar colors, by default ["viridis"]
        post_update : Callable[[Baseplot, i], None], optional
            callback function for additional customization, by default lambda self, i: None
        fixed_xlim : bool, optional
            If False xlim will gradually change in every frame, by default True
        fixed_ylim : bool, optional
            If False ylim will gradually change in every frame, by default True
        xticks : bool, optional
            Sets xticks, by default True
        yticks : bool, optional
            Sets yticks, by default True
        grid : bool, optional
             Sets xgrid, by default True

        post_update args
        ```
            self: Baseplot instance
            i: Frame index

        example:

        >>> def post_update(self, i):
        >>>     # sets log scale for x-axis
        >>>     self.ax.set_xscale("log")

        ```
        """
        self.datafier = self.dfr = datafier

        self.time_range = list(self.datafier.data.index)
        self.length = len(self.time_range)

        self.palettes = palettes
        self.column_colors = self.generate_column_colors()

        self.text_collection = {}
        self.post_update = post_update
        self.fixed_xlim = fixed_xlim
        self.fixed_ylim = fixed_ylim
        self.xticks = xticks
        self.yticks = yticks
        self.grid = grid
        self.set_xylim()
        self.set_xticks()
        self.set_yticks()
        self.set_grid()

    @classmethod
    def from_df(
        cls,
        data: pd.DataFrame,
        time_format: str,
        ip_freq: str,
        palettes: list[str] = ["viridis"],
        post_update: Callable[[__qualname__, int], None] = lambda self, i: None,
        fixed_xlim=True,
        fixed_ylim=True,
        xticks=True,
        yticks=True,
        grid=True,
    ):
        return cls(
            BaseDatafier(data, time_format, ip_freq),
            palettes,
            post_update,
            fixed_ylim,
            fixed_xlim,
            xticks,
            yticks,
            grid,
        )

    def generate_column_colors(self) -> dict[str, str]:
        """Generates column colors based on the given color palettes.

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
                        palette,
                        int(
                            np.ceil(
                                len(self.dfr.colorable_columns) / len(self.palettes)
                            )
                        ),
                    )
                )
            )

        return {
            column: color
            for column, color in zip(self.dfr.colorable_columns, all_colors)
        }

    def set_column_decorations(
        self,
        new_decorations: Union[str, list[str], dict[str, str]],
        old_decorations: dict[str, str],
    ) -> dict[str, str]:
        decorations = {}
        if isinstance(new_decorations, str):
            decorations = {k: new_decorations for (k, _) in old_decorations.items()}

        elif isinstance(new_decorations, dict):
            decorations = old_decorations
            for key in new_decorations:
                if key not in old_decorations.keys():
                    raise ValueError(f"Invalid column name found {key}")
            else:
                decorations.update(new_decorations)

        elif isinstance(new_decorations, list):
            assert len(new_decorations) == len(
                old_decorations
            ), "Number of colors does not match number of columns"

            decorations = {
                k: v2 for v2, (k, _) in zip(new_decorations, old_decorations.items())
            }
        else:
            raise TypeError("colors must be str, list or dict")

        return decorations

    def set_column_colors(self, colors: Union[str, list[str], dict[str, str]]) -> None:
        """Sets column colors. If colors is a list, length of colors should be equal
        to `len(column_colors)`

        Parameters
        ----------
        colors : Union[str, list[str], dict[str, str]]
            Single color str or list of colors or dict of column to color mapping
        """
        self.column_colors = self.set_column_decorations(colors, self.column_colors)

    # def set_column_colors(self, colors: Union[str, list[str], dict[str, str]]) -> None:
    #     """Sets column colors. If colors is a list, length of colors should be equal
    #     to `len(column_colors)`

    #     Parameters
    #     ----------
    #     colors : Union[str, list[str], dict[str, str]]
    #         Single colors str or list of colors or dict of column to color mapping
    #     """

    #     if isinstance(colors, str):
    #         self.column_colors = {k: colors for (k, _) in self.column_colors.items()}

    #     elif isinstance(colors, dict):
    #         for key in colors:
    #             if key not in self.column_colors.keys():
    #                 raise ValueError(f"Invalid column name found {key}")
    #         else:
    #             self.column_colors.update(colors)

    #     elif isinstance(colors, list):
    #         assert len(colors) == len(
    #             self.column_colors
    #         ), "Number of colors does not match number of columns"

    #         self.column_colors = {
    #             k: v2 for v2, (k, _) in zip(colors, self.column_colors.items())
    #         }

    #     else:
    #         raise TypeError("colors must be str, list or dict")

    def set_xylim(self, xlim: list[float] = [], ylim: list[float] = []):
        """Sets xlim and ylim

        Parameters
        ----------
        xlim : list[float], optional
            x axis limits in this format [min, max], by default [min date, max date]
        ylim : list[float], optional
            y axis limits in this format [min, max], by default [min y val, max y val]
        """

        assert (
            len(xlim) == 2 or len(xlim) == 0
        ), "xlim is incorrect (correct format - [minLim, maxLim])"
        assert (
            len(ylim) == 2 or len(ylim) == 0
        ), "ylim is incorrect (correct format - [minLim, maxLim])"

        if xlim == []:
            self.max_date = self.datafier.data.index.max()
            xlim = [None, self.max_date]
        self.xlim = xlim

        if ylim == []:
            self.total_max = self.datafier.data.max().max()
            ylim = [None, self.total_max]
        self.ylim = ylim

    def set_axes(self, ax: plt.Axes) -> None:
        """Sets the Axes of this plot

        Parameters
        ----------
        ax : plt.Axes
            Axes of this plot
        """
        self.ax = ax

    def set_title(
        self,
        title: str,
        x: float = 0,
        y: float = 1.01,
        size: float = 13,
        color: str = "#777777",
        **kwargs,
    ) -> None:
        """Sets the plot title and additional kwargs are passed to `plt.text(**kwargs)`

        Parameters
        ----------
        title : str
            Title text
        x : float, optional
            x coordinate of the text, by default 0
        y : float, optional
            y coordinate, by default 1.01
        size : float, optional
            text size, by default 13
        color : str, optional
            text color, by default "#777777"
        """
        self.text_collection["title"] = (
            None,
            {
                **{
                    "x": x,
                    "y": y,
                    "s": title,
                    "color": color,
                    "size": size,
                },
                **kwargs,
            },
        )

    def set_xlabel(
        self,
        text: str,
        x: float = 0.43,
        y: float = -0.09,
        size: float = 13,
        color: str = "#777777",
        **kwargs,
    ) -> None:
        """Sets the plot xlabel and additional kwargs are passed to `plt.text(**kwargs)`

        Parameters
        ----------
        text : str
            The xlabel text
        x : float, optional
             X coordinate of the text, by default 0.43
        y : float, optional
            Y coordinate, by default -0.09
        size : float, optional
            Text size, by default 13
        color : str, optional
            Text color, by default "#777777"
        """
        self.text_collection["xlabel"] = (
            None,
            {
                **{
                    "x": x,
                    "y": y,
                    "s": text,
                    "color": color,
                    "size": size,
                },
                **kwargs,
            },
        )

    def set_time(
        self,
        callback: Callable[
            [int, BaseDatafier], str
        ] = lambda i, datafier: datafier.data.index[i],
        x: float = 0.97,
        y: float = 0.27,
        size: float = 46,
        weight: float = 800,
        ha="right",
        color: str = "#777777",
        **kwargs,
    ) -> None:
        """Annotates the time in the plot and additional kwargs are passed to `plt.text(**kwargs)`

        Parameters
        ----------
        callback : Callable[ [int, BaseDatafier], str ], optional
            Callback function to customize the time text, by default `lambda i, datafier: datafier.data.index[i]`
        x : float, optional
            x coordinate of the text, by default 0.97
        y : float, optional
            y coordinate of the text, by default 0.27
        size : float, optional
            text size, by default 46
        weight : float, optional
            text weight, by default 800
        ha : str, optional
            horizontal alignment, by default "right"
        color : str, optional
            text color, by default "#777777"

        callback args:
        ```
            i: Animation frame / data row index
            datafier: The datafier instance,
                access the data using datafier.data
        ```
        """
        self.text_collection["time"] = (
            callback,
            {
                **{
                    "x": x,
                    "y": y,
                    "color": color,
                    "size": size,
                    "weight": weight,
                    "ha": ha,
                },
                **kwargs,
            },
        )

    def set_text(
        self,
        key: str,
        text: str = None,
        callback: Callable[[int, BaseDatafier], str] = None,
        x: float = 0,
        y: str = 0,
        size: float = 13,
        color: str = "#777777",
        **kwargs,
    ):
        """General function to add custom texts in the plot. Either text or callback should be passd but not both.

        Parameters
        ----------
        key : str
            Unique identifier for each texts, note: These keys, title, xlabel, time, are reserved.
              overwrite them if you wish to use callbacks instead of texts in title or xlabel
        text : str, optional
            The text to be added in the plot, by default None
        callback : Callable[[int, pd.DataFrame], str], optional
            Callback function to customize the text, by default None
        x : float, optional
            X coordinate of the text, by default 0
        y : str, optional
            Y coordinate of the text, by default 0
        size : float, optional
            Text size, by default 13
        color : str, optional
            Text color, by default "#777777"

        Callback args:
        ```
            args:
            i: Animation frame / data row index
            datafier: The datafier instance

            Example:
            >>> lambda i, datafier: datafier.data.index[i]
        ```
        """
        assert text or callback, "Both text and callback cannot be None"
        self.text_collection[key] = (
            callback,
            {
                **{
                    "x": x,
                    "y": y,
                    "s": text,
                    "color": color,
                    "size": size,
                },
                **kwargs,
            },
        )
        if callback:
            self.text_collection[key][1].pop("s")

    def remove_text(self, keys: Union[str, list[str]]):
        """Removes texts by key

        Parameters
        ----------
        keys : list[str]
            key or List of keys to be removed
        """
        if isinstance(keys, str):
            keys = [keys]

        print(self.text_collection)
        for key in keys:
            self.text_collection.pop(key)

    def set_xticks(
        self, axis: str = "x", colors: str = "#777777", labelsize: float = 12, **kwargs
    ):
        """Sets xtick properties, additional kwargs are passed to `ax.tick_params(**kwargs)`

        Parameters
        ----------
        axis : str, optional
            Defines tick axis, by default "x"
        colors : str, optional
            Sets tick color, by default "#777777"
        labelsize : float, optional
            Sets tick size, by default 12
        """
        self.xtick_props = {
            "axis": axis,
            "colors": colors,
            "labelsize": labelsize,
            **kwargs,
        }

    def set_yticks(
        self, axis: str = "y", colors: str = "#777777", labelsize: float = 10, **kwargs
    ):
        """Sets ytick properties, additional kwargs are passed to `ax.tick_params(**kwargs)`

        Parameters
        ----------
        axis : str, optional
            Defines tick axis, by default "y"
        colors : str, optional
            Sets tick color, by default "#777777"
        labelsize : float, optional
            Sets tick size, by default 10
        """
        self.ytick_props = {
            "axis": axis,
            "colors": colors,
            "labelsize": labelsize,
            **kwargs,
        }

    def set_grid(
        self,
        which: str = "major",
        axis: str = "x",
        linestyle: str = "-",
        grid_behind: bool = True,
        **kwargs,
    ) -> None:
        """Sets the plots grid, additional kwargs are passed to `ax.grid(**kwargs)`

        Parameters
        ----------
        which : str, optional
            The grid lines to apply the changes on, by default "major"
        axis : str, optional
            Sets the axis of the grid, by default "x"
        linestyle : str, optional
            Grids line style, by default "-"
        grid_behind : bool, optional
            Sets the grid behind the plot, by default True
        """
        self.grid_behind = grid_behind
        self.grid_props = {
            "which": which,
            "axis": axis,
            "linestyle": linestyle,
            **kwargs,
        }

    def update(self, i):
        if self.fixed_xlim:
            self.ax.set_xlim(self.xlim)
        if self.fixed_ylim:
            self.ax.set_ylim(self.ylim)

        if self.xticks:
            self.ax.tick_params(**self.xtick_props)
        if self.yticks:
            self.ax.tick_params(**self.ytick_props)

        if self.grid:
            self.ax.grid(**self.grid_props)

        self.ax.set_axisbelow(self.grid_behind)

        self.post_update(self, i)
        for v in self.text_collection.values():
            callback, props_dict = v[0], v[1]
            if callback:
                self.ax.text(
                    s=callback(i, self.datafier),
                    transform=self.ax.transAxes,
                    **props_dict,
                )
            else:
                self.ax.text(
                    **props_dict,
                    transform=self.ax.transAxes,
                )
