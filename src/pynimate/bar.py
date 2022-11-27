from typing import Callable, Union

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from pynimate.datafier import Datafier


class BarBasic:
    def __init__(
        self,
        data: pd.DataFrame,
        time_format: str,
        ip_freq: str,
        ip_frac: float = 0.5,
        n_bars: int = 10,
        palettes: list[str] = ["viridis"],
        post_update: Callable[[plt.Axes, int, pd.DataFrame, pd.DataFrame], None] = None,
        annot_bars: bool = True,
        fixed_xlim: bool = True,
        xticks: bool = True,
        yticks: bool = True,
        grid: bool = True,
        rounded_edges: bool = False,
    ) -> None:
        """Basic BarChartRace module that requires a valid time index

        Parameters
        ----------
        data : pd.DataFrame
            The data to be prepared, should be in this format where time is set to index.
        time_format : str
            Index datetime format
        ip_freq : str
            Interpolation frequency
        ip_frac : float, optional
            Interpolation fraction (check end of docstring), by default 0.5
        n_bars : int, optional
            Number of bars to be visible on the plot Defaults to 10 or less, by default 10
        palettes : list[str], optional
            List of color palettes to generate bar colors, by default ["viridis"]
        post_update : Callable[[plt.Axes, int, pd.DataFrame, pd.DataFrame], None], optional
            callback function for additional customization,, by default None\n
            ```
                args:
                    plt.Axes: The matplotlib Axes used for the barplot
                    int: Current animation frame / dataframe row
                    pd.DataFrame: The actual data
                    pd.DataFrame: Dataframe containing bar ranks

                example:
                >>> def post_update(ax, i, data, df_ranks):
                >>>     # sets log scale for x-axis
                >>>     ax.set_xscale("log")
            ```
        annot_bars : bool, optional
            Sets bar annotations, by default True
        fixed_xlim : bool, optional
            If False xlim will gradually change in every frame, by default True
        xticks : bool, optional
            Sets xticks, by default True
        yticks : bool, optional
            Sets yticks, by default True
        grid : bool, optional
             Sets xgrid, by default True
        rounded_edges : bool, optional
             Sets rounded bar edges, by default False

        ```
            ip_frac is the percentage of NaN values to be linearly interpolated for column ranks\n
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

            >>>                 a         b
            >>> 2021-11-13  1.000000  4.000000  << original value ---------------
            >>> 2021-11-14  1.333333  4.666667                                   |
            >>> 2021-11-15  1.666667  5.333333                                   |  50% linearly
            >>> 2021-11-16  2.000000  6.000000  <- linear interpolation          |  interpolated
            >>> 2021-11-17  2.000000  6.000000      upto here                    |  rest are filled.
            >>> 2021-11-18  2.000000  6.000000  << original value (upper bound)--
            This adds some stability in the barChartRace and reduces constantly shaking of bars.```
        """

        self.n_bars = min(n_bars, len(data.columns))
        (self.data, self.df_ranks, self.bar_colors,) = self.get_datafier_data(
            data, time_format, ip_freq, ip_frac, n_bars, palettes
        )
        self.post_update = post_update or (lambda *args: None)

        self.time_range = list(self.data.index)
        self.length = len(self.time_range)

        self.annot_bars = annot_bars
        self.fixed_xlim = fixed_xlim
        self.xticks = xticks
        self.yticks = yticks
        self.grid = grid
        self.rounded_edges = rounded_edges

        self.set_figure()

        self.text_collection = {}
        self.extra_callbacks = {}

        self.set_barh()
        self.set_bar_border_props()
        self.set_xticks()
        self.set_yticks()
        self.set_grid()
        self.set_bar_annots()

        self.set_time()

    def get_datafier_data(self, *args) -> tuple:
        """Handles the required data for animation
        override this if you use custom data handlers instead of Datafier

        """
        data_handler = Datafier(*args)
        return data_handler.prepared_data()

    def set_bar_color(self, colors: Union[list, dict[str, str]]):
        """If colors is a list, length of colors should be equal to no of columns. If it is a dict, all columns should be mapped to a color.

        Parameters
        ----------
        colors : Union[list, dict[str, str]]
            list of colors or dict of column to color mapping
        """
        assert len(colors) == len(
            self.data.columns
        ), "Number of colors does not match number of columns"
        if isinstance(colors, list):
            self.bar_colors = {
                k: v2 for v2, (k, v1) in zip(colors, self.bar_colors.items())
            }
        elif isinstance(colors, dict):
            self.bar_colors = colors
        else:
            ValueError("colors must be list or dict")

    def set_figure(
        self,
        figsize: tuple[int, int] = (16, 9),
        xlim: list[float] = [],
        ylim: list[float] = [],
        **kwargs,
    ) -> None:
        """ets figure size, xlim and ylim. Additional kwargs ara passed to plt.subplots(**kwargs)

        Parameters
        ----------
        figsize : tuple[int, int], optional
            plot figure size, by default (16, 9)
        xlim : list[float], optional
            x axis limits in this format [min, max], by default [min, max + 5]
        ylim : list[float], optional
            y axis limits in this format [min, max], by default [0.5, n_bars + 0.6]
        """
        if xlim != None:
            assert (
                len(xlim) == 2 or len(xlim) == 0
            ), "xlim is incorrect (correct format- [minLim, maxLim]"
        # closes the previous figure window
        if hasattr(self, "fig"):
            plt.close(self.fig)

        self.fig, self.ax = plt.subplots(1, 1, figsize=figsize, **kwargs)
        if xlim != None:
            if xlim == []:
                self.total_max = self.data.max().max()
                xlim = [None, self.total_max + 5]
            self.xlim = xlim
            self.ax.set_xlim(xlim)
        if ylim == []:
            ylim = [0.5, self.n_bars + 0.6]
        self.ylim = ylim

    def getTopXY(self, i: int) -> tuple:
        """Prepares top n_bar columns and their respective attributes such as position, length, colors.
        Not to be used outside animation update.

        Parameters
        ----------
        i : int
            Animation frame index

        Returns
        -------
        tuple
            Bar locationn length, columns and their respective colors
        """

        bar_location = self.df_ranks.iloc[i].values
        top_filt = (bar_location >= 1) & (bar_location <= self.n_bars)
        bar_location = bar_location[top_filt]
        bar_length = self.data.iloc[i].values[top_filt]
        cols = self.data.columns[top_filt]
        colors = [self.bar_colors[column] for column in cols]
        return bar_location, bar_length, cols, colors

    def set_title(
        self,
        title: str,
        x: float = 0,
        y: float = 1.01,
        size: float = 13,
        color: str = "#777777",
        **kwargs,
    ) -> None:
        """Sets the plot title and additional `kwargs` are passed to plt.text(**kwargs)

        Parameters
        ----------
        title : str
            _description_
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
                    "transform": self.ax.transAxes,
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
        """Sets the plot xlabel and additional `kwargs` are passed to plt.text(**kwargs)

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
                    "transform": self.ax.transAxes,
                },
                **kwargs,
            },
        )

    def set_time(
        self,
        callback: Callable[
            [int, pd.DataFrame, list, any], str
        ] = lambda i, data, time, rank: time[i],
        x: float = 0.97,
        y: float = 0.27,
        size: float = 46,
        weight: float = 800,
        ha="right",
        color: str = "#777777",
        **kwargs,
    ) -> None:
        """_summary_

        Parameters
        ----------
        callback : Callable[ [int, pd.DataFrame, list, any], str ], optional
            Callback function to customize the time text, by default `lambda i, data, time, rank: time[i]`
        ```
            args:
            i: Animation frame / data row index
            data: The actual data
            time: The time index, i.e data.index
            rank: Dataframe containing the bar rankings
        ```
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
                    "transform": self.ax.transAxes,
                },
                **kwargs,
            },
        )

    def set_text(
        self,
        key: str,
        text: str = None,
        callback: Callable[[int, pd.DataFrame, list, pd.DataFrame], str] = None,
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
              overwrite them if you wish to use callbacks instead of texts in title or xlabel.
        text : str, optional
            The text to be added in the plot, by default None
        callback : Callable[[int, pd.DataFrame, list, pd.DataFrame], str], optional
            Callback function to customize the text, by default None\n
            ```
            Example:
            >>> lambda i, data, time, rank: time[i]
            args:
            i: Animation frame / data row index
            data: The actual data
            time: The time index, i.e data.index
            rank: Dataframe containing the bar rankings
            ```
        x : float, optional
            X coordinate of the text, by default 0
        y : str, optional
            Y coordinate of the text, by default 0
        size : float, optional
            Text size, by default 13
        color : str, optional
            Text color, by default "#777777"
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
                    "transform": self.ax.transAxes,
                },
                **kwargs,
            },
        )
        if callback:
            self.text_collection[key][1].pop("s")

    def remove_text(self, keys: list[str]):
        """Removes texts by key.

        Parameters
        ----------
        keys : list[str]
            List of keys to be removed
        """
        for key in keys:
            self.text_collection.pop(key)

    def set_bar_border_props(
        self,
        edge_color: str = "k",
        radius: float = 0.5,
        pad: float = -0.0040,
        mutation_aspect: float = 0.2,
        **kwargs,
    ) -> None:
        """Sets bar border properties. Additional `kwargs` are passed to FancyBboxPatch.
        See https://matplotlib.org/3.1.0/api/_as_gen/matplotlib.patches.FancyBboxPatch.html

        Parameters
        ----------
        edge_color : str, optional
            Bar edge color, by default "k"
        radius : float, optional
            Bar border radius, by default 0.5
        pad : float, optional
            See above link, by default -0.0040
        mutation_aspect : float, optional
            See above link, by default 0.2
        """
        self.bar_border_props = {
            "edge_color": edge_color,
            "radius": radius,
            "pad": pad,
            "mutation_aspect": mutation_aspect,
            "kwargs": kwargs,
        }

    def _get_rounded_eges(
        self,
    ) -> None:
        """Created bar border properties.
        See https://matplotlib.org/3.1.0/api/_as_gen/matplotlib.patches.FancyBboxPatch.html
        """
        border = self.bar_border_props
        self.new_patches = []

        for patch in reversed(self.ax.patches):
            bb = patch.get_bbox()
            color = patch.get_facecolor()
            p_bbox = FancyBboxPatch(
                (bb.xmin, bb.ymin),
                abs(bb.width),
                abs(bb.height),
                boxstyle=f"round,pad={border['pad']}"
                + (
                    f",rounding_size={border['radius']}"
                    if border["radius"] != None
                    else ""
                ),
                ec=border["edge_color"],
                fc=color,
                mutation_aspect=border["mutation_aspect"],
                **border["kwargs"],
            )
            # p_bbox.set_edgecolor(border["edge_color"])
            patch.remove()
            self.new_patches.append(p_bbox)

    def set_barh(self, bar_height: float = 0.86, **kwargs):
        """Sets barh properties, addition `kwargs` are passed to ax.barh(**kwargs)

        Parameters
        ----------
        bar_height : float, optional
            Height of the bars (Note this is horizontal barplot), by default 0.86
        """
        self.barh_props = {**kwargs}
        self.barh_props["height"] = bar_height

    def set_xticks(
        self, axis: str = "x", colors: str = "#777777", labelsize: float = 12, **kwargs
    ):
        """Sets xtick properties, additional `kwargs` are passed to ax.tick_params(**.kwargs)

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
        """Sets ytick properties, additional `kwargs` are passed to ax.tick_params(**kwargs)

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
        """Sets the plots grid, additional `kwargs` are passed to ax.grid(**kwargs)

        Parameters
        ----------
        which : str, optional
            The grid lines to apply the changes on, by default "major"
        axis : str, optional
            Sets the axis of the grid, by default "x"
        linestyle : str, optional
            Grids line style, by default "-"
        grid_behind : bool, optional
            Sets the grid behind the bars, by default True
        """
        self.ax.set_axisbelow(grid_behind)
        self.grid_props = {
            "which": which,
            "axis": axis,
            "linestyle": linestyle,
            **kwargs,
        }

    def set_bar_annots(
        self,
        text_callback: Callable[[float], Union[str, float]] = lambda val: np.round(
            val, 2
        ),
        xoffset: float = 0.1,
        yoffset: float = -0.1,
        ha: str = "left",
        **kwargs,
    ) -> None:
        """Sets bar annotation properties, additional kwargs are passed to `ax.text(**kwargs)`.
        (Note these annotations are the texts near the bars)

        Parameters
        ----------
        text_callback : _type_, optional
            Callback function for customizing the text, by default lambda val:np.round(val, 2)
        xoffset : float, optional
            X offset relative to bar length, by default 0.1
        yoffset : float, optional
             Y offset relative to bar height, by default -0.1
        ha : str, optional
            Horizontal alignment, by default "left"
        """
        self.bar_annot_props = {
            "callback": text_callback,
            "xoffset": xoffset,
            "yoffset": yoffset,
            "ha": ha,
            "kwargs": kwargs,
        }

    def add_extras(
        self,
        key: str,
        callback: list[Callable[[plt.Axes, int, pd.DataFrame, pd.DataFrame], None]],
    ):
        """Adds extra callback functions for additional customizations

        Parameters
        ----------
        key : str
            Unique identifier for each callback functions
        callback : list[Callable[[plt.Axes, int, pd.DataFrame, pd.DataFrame], None]]
            Callback function for additional customization
            ```
                args:
                    plt.Axes: The matplotlib Axes used for the barplot
                    int: Current animation frame / dataframe row
                    pd.DataFrame: The actual data
                    pd.DataFrame: Dataframe containing bar ranks

                Example:
                >>> lambda ax, *args: ax.set_xcale("log)
            ```
        """
        self.extra_callbacks[key] = callback

    def _init(self) -> None:
        """FuncAnimation init"""
        bar_location, bar_length, cols = self.getTopXY(0)
        self.ax.barh(bar_location, bar_length, tick_label=cols, **self.barh_props)

    def _update(self, i: int) -> None:
        """FuncAnimation update

        Parameters
        ----------
        i : int
            Animation frame
        """
        self.ax.clear()

        if self.fixed_xlim:
            self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)

        Y, X, cols, colors = self.getTopXY(i)

        self.ax.barh(
            Y,
            X,
            tick_label=cols,
            color=colors,
            **self.barh_props,
        )

        if self.annot_bars:
            for x, y in zip(X, Y):
                self.ax.text(
                    x + self.bar_annot_props["xoffset"],
                    y + self.bar_annot_props["yoffset"],
                    self.bar_annot_props["callback"](x),
                    ha=self.bar_annot_props["ha"],
                    **self.bar_annot_props["kwargs"],
                )

        if self.xticks:
            self.ax.tick_params(**self.xtick_props)

        if self.yticks:
            self.ax.tick_params(**self.ytick_props)

        if self.grid:
            self.ax.grid(**self.grid_props)

        for k, v in self.text_collection.items():
            if v[0]:
                self.ax.text(
                    s=v[0](i, self.data, self.time_range, self.df_ranks), **v[1]
                )
            else:
                self.ax.text(**v[1])

        for k, v in self.extra_callbacks.items():
            v(self.ax)

        self.post_update(self.ax, i, self.data, self.df_ranks)

        if self.rounded_edges:
            self._get_rounded_eges()
            for patch in self.new_patches:
                self.ax.add_patch(patch)

    def animate(self, interval: int = 50, **kwargs) -> None:
        """Main module to create the animation, additional `kwargs` are passed to animation.FuncAnimation(**kwargs)

        Parameters
        ----------
        interval : int, optional
            Interval between each frame. Defaults to 50ms, by default 50

        """
        self.ani = animation.FuncAnimation(
            self.fig,
            self._update,
            frames=self.length,
            interval=interval,
            blit=False,
            **kwargs,
        )
        return self.ani

    def save(self, filename: str, fps: int, extension: str = "gif", **kwargs):
        """Saves the current animation

        Parameters
        ----------
        filename : str
            ilename
        fps : int
            Video fps / frames per second
        extension : str, optional
            File extension, by default "mp4"
        """
        self.ani.save(f"{filename}.{extension}", fps=fps, **kwargs)
