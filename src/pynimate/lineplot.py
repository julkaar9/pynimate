from typing import Callable, Union

import matplotlib.dates as mdates
import pandas as pd

from pynimate.baseplot import Baseplot
from pynimate.datafier import LineDatafier
from pynimate.utils import human_readable


class Lineplot(Baseplot):
    def __init__(
        self,
        datafier: LineDatafier,
        palettes: list[str] = ["viridis"],
        post_update: Callable[[__qualname__, int], None] = lambda self, i: None,
        line_annots: bool = True,
        legend: bool = True,
        scatter_markers: bool = True,
        line_head: bool = True,
        fixed_xlim: bool = True,
        fixed_ylim: bool = False,
        xticks: bool = True,
        yticks: bool = True,
        grid: bool = True,
    ) -> None:
        """Lineplot animation module that requires a valid time index.The data
        should be in this format where time is set to index
            ```
                Example:
                >>> time  col1 col2 col3 ...
                >>> 2012   1    0    2
                >>> 2013   2    3    1
            ```

        Parameters
        ----------
        datafier : LineDatafier
            The datafier instance
        palettes : list[str], optional
            List of color palettes to generate line / marker colors, by default ["viridis"]
        post_update : Callable[[__qualname__, int], None], optional
            callback function for additional customization, by default lambda self, i: None
        line_annots : bool, optional
            Sets line annotations leading the lines, by default True
        legend : bool, optional
            Sets plot legend, by default True
        scatter_markers : bool, optional
            Enables line markers / Scatterplot, by default True
        line_head : bool, optional
            Enables markers leading every line, by default True
        fixed_xlim : bool, optional
            If False xlim will gradually change in every frame, by default True
        fixed_ylim : bool, optional
            If False ylim will gradually change in every frame, by default False
        xticks : bool, optional
            Sets xticks, by default True
        yticks : bool, optional
            Sets yticks, by default True
        grid : bool, optional
            Sets xgrid, by default True
        """
        super().__init__(
            datafier,
            palettes,
            post_update,
            fixed_xlim,
            fixed_ylim,
            xticks,
            yticks,
            grid,
        )
        self.line_annots = line_annots
        self.legend = legend
        self.line_head = line_head
        self.scatter_markers = scatter_markers
        self.column_linestyles = {col: "solid" for col in self.column_colors.keys()}
        self.set_line()
        self.set_line_annots()
        self.set_line_head()
        self.set_marker()
        self.set_legend()

    @classmethod
    def from_df(
        cls,
        data: pd.DataFrame,
        time_format: str,
        ip_freq: str,
        palettes: list[str] = ["viridis"],
        post_update: Callable[[__qualname__, int], None] = lambda self, i: None,
        line_annots: bool = True,
        legend: bool = True,
        scatter_markers: bool = True,
        line_head: bool = True,
        fixed_xlim: bool = True,
        fixed_ylim: bool = False,
        xticks: bool = True,
        yticks: bool = True,
        grid: bool = True,
    ):
        return cls(
            LineDatafier(data, time_format, ip_freq),
            palettes,
            post_update,
            line_annots,
            legend,
            scatter_markers,
            line_head,
            fixed_xlim,
            fixed_ylim,
            xticks,
            yticks,
            grid,
        )

    def set_xylim(self, xlim: list[float] = [], ylim: list[float] = []):
        """Sets xlim and ylim

        Parameters
        ----------
        xlim : list[float], optional
            x axis limits in this format [min, max], by default [min date, max date]
        ylim : list[float], optional
            y axis limits in this format [min, max], by default [min y val, max y val]
        """
        super().set_xylim(xlim, ylim)
        if xlim == []:
            self.max_date = self.datafier.data.index.max()
            self.min_date = self.datafier.data.index.min()
            xlim = [self.min_date, self.max_date]
        self.xlim = xlim
        if ylim == []:
            self.total_max = self.datafier.data.max().max()
            self.total_min = self.datafier.data.min().min()
            ylim = [self.total_min, self.total_max]
        self.ylim = ylim

    def set_column_linestyles(
        self, linestyles: Union[str, list[str], dict[str, str]]
    ) -> None:
        """Sets column linestyles. If linestyles is a list, length of linestyles should be equal
        to `len(self.column_linestyles)`

        Parameters
        ----------
        linestyles : Union[str, list[str], dict[str, str]]
            Single linestyle str or list of linestyles or dict of column to linestyle mapping
        """
        self.column_linestyles = self.set_column_decorations(
            linestyles, self.column_linestyles
        )

    def set_line(self, **kwargs) -> None:
        """Sets line properties, addition kwargs are passed to `ax.plot(**kwargs)`"""
        assert (
            "linestyle" not in kwargs
        ), "Use 'set_column_linestyle()' for linestyle customization"

        self.line_props = kwargs

    def set_line_annots(
        self,
        callback: Callable[
            [str, float], str
        ] = lambda col, val: f"{col}({human_readable(val)})",
        size: float = 10,
        **kwargs,
    ) -> None:
        """Sets line annotation properties, additional kwargs are passed to `ax.text(**kwargs)`.
        (Note these annotations are the texts leading the lines)

        Parameters
        ----------
        callback : Callable[ [str, float], str ], optional
            Callback function for customizing the text, by default lambda col, val: f"{col}({human_readable(val)})"
        size : float, optional
            Text size, by default 10
        """
        kwargs = {"size": size, **kwargs}
        self.line_annot_props = {"callback": callback, "kwargs": kwargs}

    def set_line_head(self, edgecolors: Union[str, list[str]] = "k", **kwargs) -> None:
        """Sets the line head(leading marker) properites, additional kwargs are passed to `ax.scatter(**kwargs)`

        Parameters
        ----------
        edgecolors : Union[str, list[str]], optional
            Edge color of the point, by default "k"
        """
        self.line_head_props = {"edgecolors": edgecolors, **kwargs}

    def set_marker(self, **kwargs) -> None:
        """Sets the line marker (scatterplot) properties, kwargs are passed to `ax.scatter(**kwargs)`"""
        self.marker_props = kwargs

    def set_legend(self, **kwargs) -> None:
        """Sets legend properties, kwargs are passed to `ax.legend(**kwargs)`"""
        self.legend_props = kwargs

    def update(self, i) -> None:
        self.ax.clear()
        for col in self.dfr.data.columns:
            self.X, self.Y = self.dfr.data.index, self.dfr.data[col]
            self.Y_og = self.dfr.expanded[col]
            self.ax.plot(
                self.X[: i + 1],
                self.Y[: i + 1],
                color=self.column_colors[col],
                linestyle=self.column_linestyles[col],
                label=col,
                **self.line_props,
            )
            if self.scatter_markers:
                self.ax.scatter(
                    self.X[:i],
                    self.Y_og[:i],
                    color=self.column_colors[col],
                    **self.marker_props,
                )

            if self.line_annots:
                self.annot = self.ax.annotate(
                    self.line_annot_props["callback"](col, self.Y[i]),
                    (mdates.date2num(self.X[i]), self.Y[i]),
                    **self.line_annot_props["kwargs"],
                )

            if self.legend:
                self.ax.legend(**self.legend_props)

            if self.line_head:
                self.ax.scatter(
                    self.X[i : i + 1],
                    self.Y[i : i + 1],
                    color=self.column_colors[col],
                    **self.line_head_props,
                )
        super().update(i)
