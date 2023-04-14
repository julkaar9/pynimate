from types import SimpleNamespace
from typing import Callable, Union

import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from pynimate.baseplot import Baseplot
from pynimate.datafier import BarDatafier


class Barhplot(Baseplot):
    def __init__(
        self,
        datafier: BarDatafier,
        palettes: list[str] = ["viridis"],
        post_update: Callable[[__qualname__, int], None] = lambda self, i: None,
        annot_bars: bool = True,
        rounded_edges: bool = False,
        fixed_xlim: bool = True,
        xticks: bool = True,
        yticks: bool = True,
        grid: bool = True,
    ) -> None:
        """Bar Chart animation module that requires a valid time index.The data
        should be in this format where time is set to index
            ```
                Example:
                >>> time  col1 col2 col3 ...
                >>> 2012   1    0    2
                >>> 2013   2    3    1
            ```
        Parameters
        ----------
        datafier : BarDatafier
            The datafier instance
        palettes : list[str], optional
            List of color palettes to generate bar colors, by default ["viridis"]
        post_update : Callable[[Barhplot, i], None], optional
            callback function for additional customization, by default lambda self, i: None
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
        super().__init__(
            datafier, palettes, post_update, fixed_xlim, True, xticks, yticks, grid
        )
        self.annot_bars = annot_bars
        self.rounded_edges = rounded_edges

        self.set_barh()
        self.set_bar_border_props()
        self.set_bar_annots()

    @classmethod
    def from_df(
        cls,
        data: pd.DataFrame,
        time_format: str,
        ip_freq: str,
        palettes: list[str] = ["viridis"],
        post_update: Callable[[__qualname__, int], None] = lambda self, i: None,
        annot_bars: bool = True,
        rounded_edges: bool = False,
        fixed_xlim=True,
        xticks=True,
        yticks=True,
        grid=True,
    ):
        return cls(
            BarDatafier(data, time_format, ip_freq),
            palettes,
            post_update,
            annot_bars,
            rounded_edges,
            fixed_xlim,
            xticks,
            yticks,
            grid,
        )

    def set_xylim(
        self,
        xlim: list[float] = [],
        ylim: list[float] = [],
        xoffset: float = 5,
        yoffset: float = 0.6,
    ) -> None:
        """Sets xlim and ylim.

        Parameters
        ----------
        xlim : list[float], optional
            x axis limits in this format [min, max], by default [min, max + xoffset]
        ylim : list[float], optional
            y axis limits in this format [min, max], by default [0.5, n_bars + yoffset]
        xoffset : float, optional
            additional offset value for x axis max, by default 5
        yoffset : float, optional
            additional offset value for y axis max, by default 0.6
        """
        super().set_xylim(xlim, ylim)

        if xlim == []:
            self.total_max = self.datafier.data.max().max()
            xlim = [None, self.total_max + xoffset]
        self.xlim = xlim

        if ylim == []:
            ylim = [0.5, self.dfr.n_bars + yoffset]
        self.ylim = ylim

    def get_ith_bar_attrs(self, i: int) -> SimpleNamespace:
        """Prepares ith top columns and their respective attributes such as position, length, colors.
        Not meant to be used outside animation update.

        Parameters
        ----------
        i : int
            Animation frame index

        Returns
        -------
        SimpleNamespace
            bar_rank, bar_length, top_cols, column_colors
        """

        bar_rank = self.dfr.df_ranks.iloc[i].values
        top_cols = (bar_rank >= 1) & (bar_rank <= self.dfr.n_bars)
        bar_rank = bar_rank[top_cols]
        bar_length = self.dfr.data.iloc[i].values[top_cols]
        cols = self.dfr.data.columns[top_cols]
        colors = [self.column_colors[column] for column in cols]
        return SimpleNamespace(
            bar_rank=bar_rank,
            bar_length=bar_length,
            top_cols=cols,
            column_colors=colors,
        )

    def _get_rounded_eges(
        self,
    ) -> None:
        """Creates bar border properties.
        See https://matplotlib.org/3.1.0/api/_as_gen/matplotlib.patches.FancyBboxPatch.html
        """
        border = self.bar_border_props
        self.new_patches = []

        for patch in reversed(self.ax.patches):
            bb = patch.get_bbox()
            color = patch.get_facecolor()
            zorder = patch.zorder
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
                zorder=zorder,
                **border["kwargs"],
            )
            patch.remove()
            self.new_patches.append(p_bbox)

    def set_barh(self, bar_height: float = 0.86, **kwargs):
        """Sets barh properties, addition kwargs are passed to `ax.barh(**kwargs)`

        Parameters
        ----------
        bar_height : float, optional
            Height of the bars (Note this is horizontal barplot), by default 0.86
        """
        self.barh_props = {"height": bar_height, **kwargs}

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
        text_callback : Callable[[float], Union[str, float]], optional
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

    def set_bar_border_props(
        self,
        edge_color: str = "k",
        radius: float = 0.5,
        pad: float = -0.0040,
        mutation_aspect: float = 0.2,
        **kwargs,
    ) -> None:
        """Sets bar border properties. Additional kwargs are passed to `FancyBboxPatch`.
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

    def update(self, i: int) -> None:
        """FuncAnimation update

        Parameters
        ----------
        i : int
            Animation frame
        """
        self.ax.clear()

        self.bar_attr = self.get_ith_bar_attrs(i)

        self.ax.barh(
            self.bar_attr.bar_rank,
            self.bar_attr.bar_length,
            tick_label=self.bar_attr.top_cols,
            color=self.bar_attr.column_colors,
            **self.barh_props,
        )
        if self.annot_bars:
            for ind, (x, y) in enumerate(
                zip(self.bar_attr.bar_length, self.bar_attr.bar_rank)
            ):
                self.ax.text(
                    x + self.bar_annot_props["xoffset"],
                    y + self.bar_annot_props["yoffset"],
                    self.bar_annot_props["callback"](x),
                    ha=self.bar_annot_props["ha"],
                    **self.bar_annot_props["kwargs"],
                    zorder=ind,
                )

        if self.rounded_edges:
            self._get_rounded_eges()
            for patch in self.new_patches[::-1]:
                self.ax.add_patch(patch)

        for ind, patch in enumerate(self.ax.patches):
            patch.set_zorder(ind)

        super().update(i)
