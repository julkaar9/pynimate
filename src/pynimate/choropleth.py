from __future__ import annotations

from numbers import Number
from typing import TYPE_CHECKING, Callable, Optional, Self, Tuple

import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
import matplotlib.ticker as tick
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable

from pynimate._internals import _require_package
from pynimate.baseplot import Baseplot
from pynimate.geodatafier import GeoDatafier
from pynimate.utils import human_readable

if TYPE_CHECKING:
    import geopandas as gpd


class Choropleth(Baseplot):
    def __init__(
        self,
        datafier: GeoDatafier,
        *,
        post_update: Callable[[Self, int], None] = lambda self, i: None,
        vrange: tuple[float, float] = None,
        log_norm: bool = False,
        cmap: str = "viridis",
        annot_geo_masks: Optional[dict[str, list]] = None,
        annot_geo_filter: Callable[[pd.Series], pd.Series] = None,
        geo_annot_formatter: Callable[[Number], str] = human_readable,
        cbar_unit: str = "",
        set_frame_on: bool = False,
    ):
        """
        Choropleth animation module for visualizing temporal geographic data.

        The data must be a GeoDataFrame containing a valid ``geometry`` column and
        time-series columns in wide format.

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
        datafier : GeoDatafier
            GeoDatafier instance containing the interpolated geographic time-series
            data.

        post_update : Callable[[Choropleth, int], None], optional
            Callback function for additional customization.

        vrange : tuple[float, float], optional
            Fixed value range ``(vmin, vmax)`` used for color normalization.
            If ``None``, by default (min, max)

        cmap : str, optional
            Matplotlib colormap used for the choropleth, by default ``"viridis"``.

        annot_geo_mask : tuple[str, list], optional
            Enables geometry annotations for features whose values in the specified
            column match the provided list.

            Example:
                `("ISO_A3", ["IND", "USA", "CHN"])`

        annot_geo_filter : Callable[[pd.Series], pd.Series], optional
            Callback applied independently to every time column to determine which
            geometries should be annotated.

            The callback receives a Series representing one time column and should
            return a modified Series, replacing unwanted values with
            ``NaN``.

            Example:
                ``` annot_geo_filter = lambda col: col.where(col >= col.nlargest(n).min(), np.nan) ```

        geo_annot_formatter : Callable[[Number], str], optional
            Function used to format geometry annotation values before rendering.
            Formatting is performed once during preprocessing and cached for the
            duration of the animation.

            Default:
                `human_readable`

        cbar_unit : str, optional
            Unit appended to colorbar tick labels.

        set_frame_on : bool, optional
            Set whether the Axes rectangle patch is drawn., by default False

        post_update callback
        --------------------
        The callback receives:

        - ``self`` : Choropleth instance
        - ``i`` : Current frame index

        Example
        ```python
        def post_update(self, i):
            self.ax.set_facecolor("#202020")
            self.ax.set_title(f"Frame {i}")
        ```
        """

        _require_package("geopandas", feature="Choropleth", extra="geo")
        import geopandas as geo

        self._gpd = geo

        self.datafier = self.dfr = datafier
        self.length = len(self.dfr.time_cols)

        self.log_norm = log_norm
        self.geo_plot_params = {}

        # assert not (
        #     annot_geo_mask is not None and annot_geo_filter is not None
        # ), "Both annot_geo_mask and annot_geo_filter cannot be set"

        self.annot_geo_mask = annot_geo_masks
        self.annot_geo_filter = annot_geo_filter
        self.geo_annot_formatter = geo_annot_formatter
        self.annot_geo: bool = (
            annot_geo_masks is not None or annot_geo_filter is not None
        )

        if self.annot_geo_mask is not None:
            self.dfr._get_masked_geo_annots(annot_geo_masks)

        if self.annot_geo_filter is not None:
            self.dfr._get_filtered_geo_annots(self.annot_geo_filter)

        if self.annot_geo:
            self.dfr._format_geo_annots(self.geo_annot_formatter or human_readable)
            self.set_annot_geo(
                ha="center",
                color="white",
                path_effects=[pe.withStroke(linewidth=2, foreground="black")],
            )

        self._set_vrange(*vrange if vrange is not None else (None, None))

        if self.log_norm and self.vrange[0] <= 0:
            raise ValueError("Log normalization requires all values to be positive")

        if self.log_norm:
            self.geo_plot_params["norm"] = mcolors.LogNorm(
                vmin=self.vrange[0], vmax=self.vrange[1]
            )

        self.cbar_unit = cbar_unit
        self.cmap = cmap
        self.set_cbar_ax()
        self.set_cbar_ticks(lambda x, y: (f"{human_readable(x)}{self.cbar_unit}"))

        self.set_nan_geo()

        self._setup_plot(
            post_update=post_update,
            fixed_xlim=False,
            fixed_ylim=False,
            xticks=False,
            yticks=False,
            grid=False,
            set_frame_on=set_frame_on,
        )

    @classmethod
    def from_widedf(
        cls,
        data: gpd.GeoDataFrame,
        time_format: str,
        ip_freq: str,
        *,
        post_update: Callable[[Self, int], None] = lambda self, i: None,
        vrange: tuple[float, float] = None,
        log_norm: bool = False,
        cmap: str = "viridis",
        annot_geo_masks: Optional[Tuple[str, list]] = None,
        annot_geo_filter: Optional[Callable[[str], any]] = None,
        geo_annot_formatter: Callable[[Number], str] = human_readable,
        cbar_unit: str = "",
        set_frame_on: bool = False,
    ):
        """
        Choropleth animation module for visualizing temporal geographic data.

        The data must be a GeoDataFrame containing a valid ``geometry`` column and
        time-series columns in wide format.

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
        post_update : Callable[[Choropleth, int], None], optional
            Callback function for additional customization.

        vrange : tuple[float, float], optional
            Fixed value range ``(vmin, vmax)`` used for color normalization.
            If ``None``, by default (min, max)

        cmap : str, optional
            Matplotlib colormap used for the choropleth, by default ``"viridis"``.

        annot_geo_mask : tuple[str, list], optional
            Enables geometry annotations for features whose values in the specified
            column match the provided list.

            Example:
                `("ISO_A3", ["IND", "USA", "CHN"])`

        annot_geo_filter : Callable[[pd.Series], pd.Series], optional
            Callback applied independently to every time column to determine which
            geometries should be annotated.

            The callback receives a Series representing one time column and should
            return a modified Series, replacing unwanted values with
            ``NaN``.

            Example:
                ``` annot_geo_filter = lambda col: col.where(col >= col.nlargest(n).min(), np.nan) ```

        geo_annot_formatter : Callable[[Number], str], optional
            Function used to format geometry annotation values before rendering.
            Formatting is performed once during preprocessing and cached for the
            duration of the animation.

            Default:
                `human_readable`

        cbar_unit : str, optional
            Unit appended to colorbar tick labels.

        post_update args
        -------
        - ``self`` : Choropleth instance
        - ``i`` : Current frame index

        Example
        ```python
        def post_update(self, i):
            self.ax.set_facecolor("#202020")
            self.ax.set_title(f"Frame {i}")
        ```
        """
        return cls(
            GeoDatafier(data, time_format, ip_freq),
            post_update=post_update,
            vrange=vrange,
            log_norm=log_norm,
            cmap=cmap,
            annot_geo_masks=annot_geo_masks,
            annot_geo_filter=annot_geo_filter,
            geo_annot_formatter=geo_annot_formatter,
            cbar_unit=cbar_unit,
            set_frame_on=set_frame_on,
        )

    def set_geo_plot(self, **kwargs):
        """Sets matplotlib keyword arguments for plotting the geographic data.

        Parameters
        ----------
        **kwargs
            Keyword arguments passed directly to
            ``GeoDataFrame.plot()``.

        Examples
        --------
        ```python
        plot.set_geo_plot(
            edgecolor="white",
            linewidth=0.5,
            alpha=0.9,
        )
        ```
        """
        self.geo_plot_params |= kwargs

    def _set_vrange(self, vmin: float = None, vmax: float = None):
        """Sets the color mapping range for the choropleth.

        Parameters
        ----------
        vmin : float, optional
            Minimum value for the colormap. By default, min value in the dataset.

        vmax : float, optional
            Maximum value for the colormap. By default, max value in the dataset.
        """
        self.vrange = (
            (
                vmin
                if vmin is not None
                else self.dfr.data[self.dfr.time_cols].min().min()
            ),
            (
                vmax
                if vmax is not None
                else self.dfr.data[self.dfr.time_cols].max().max()
            ),
        )

    def set_annot_geo(self, **kwargs):
        """Sets matplotlib keyword arguments for geometry annotations.

        Parameters
        ----------
        **kwargs
            Keyword arguments passed directly to
            ``Axes.annotate()``.

        Example:
        ----------
        ```python
        plot.set_annot_geo(
            color="white",
            fontsize=10,
            ha="center",
        )
        ```
        """
        self.annot_geo_params = {**kwargs}

    def set_cbar_ax(
        self, position: str = "right", size: str = "4%", pad: float = 0.1, **kwargs
    ):
        """Sets the position and properties of the colorbar axis.

        Parameters
        ----------
        position : str, optional
            Position of the colorbar relative to the plot, by default ``"right"``.

        size : str, optional
            Width of the colorbar axis, by default ``"4%"``.

        pad : float, optional
            Padding between the plot and colorbar, by default ``0.1``.

        **kwargs
            Additional keyword arguments passed to
            ``make_axes_locatable(...).append_axes()``.
        """
        self.colorbar_ax_params = {
            "position": position,
            "size": size,
            "pad": pad,
            **kwargs,
        }

    def set_cbar_ticks(
        self,
        tick_formatter: Callable[[float, float], str] = None,
        axis: str = "both",
        which: str = "both",
        length: int = 0,
        **kwargs,
    ):
        """Sets the formatting and appearance of the colorbar ticks.

        Parameters
        ----------
        tick_formatter : Callable[[float, float], str], optional
            Function used to format colorbar tick labels. Passed to
            ``matplotlib.ticker.FuncFormatter``.

        axis : str, optional
            Axis on which to apply the tick parameters, by default ``"both"``.

        which : str, optional
            Specifies which ticks to modify (``"major"``, ``"minor"``, or
            ``"both"``), by default ``"both"``.

        length : int, optional
            Tick length, by default ``0``.

        **kwargs
            Additional keyword arguments passed to
            ``Axes.tick_params()``.
        """
        if tick_formatter is not None:
            self.cbar_tick_formatter = tick_formatter
        self.cbar_tick_params = {
            "axis": axis,
            "which": which,
            "length": length,
            **kwargs,
        }

    def set_nan_geo(self, color="#62656B", **kwargs):
        """Sets the appearance of geometries with missing values.

        Parameters
        ----------
        color : str, optional
            Fill color used for geometries whose value is ``NaN``, by default
            ``"#62656B"``.

        **kwargs
            Additional keyword arguments passed directly to
            ``GeoDataFrame.plot()`` when rendering missing-value geometries.

        Example:
        --------
        ```python
        plot.set_nan_geo(
            color="#444444",
            edgecolor="black",
            hatch="///",
        )
        ```
        """
        self.geo_nan_params = {"color": color, **kwargs}

    def init(self):
        divider = make_axes_locatable(self.ax)
        self.cax = divider.append_axes(**self.colorbar_ax_params)

        self.map = self.dfr.data.plot(
            ax=self.ax,
            column=self.dfr.time_cols[0],
            cmap=self.cmap,
            vmin=self.vrange[0],
            vmax=self.vrange[1],
            legend=True,
            cax=self.cax,
            **self.geo_plot_params,
        )

        self.cax.yaxis.set_major_formatter(tick.FuncFormatter(self.cbar_tick_formatter))
        self.cax.tick_params(**self.cbar_tick_params)

        nan_geo: gpd.GeoDataFrame = self.dfr.data[
            self.dfr.data[self.dfr.time_cols[0]].isna()
        ]

        if len(nan_geo) > 0:
            nan_geo.plot(ax=self.ax, **self.geo_nan_params)

        if self.annot_geo:
            self.dfr.annot_data.apply(
                lambda x: self.ax.annotate(
                    text=x[self.dfr.time_cols[0]],
                    xy=x.geometry.centroid.coords[0],
                    **self.annot_geo_params,
                ),
                axis=1,
            )

    def update(self, i):
        self.ax.clear()

        self.dfr.data.plot(
            ax=self.ax,
            column=self.dfr.time_cols[i],
            cmap=self.cmap,
            vmin=self.vrange[0],
            vmax=self.vrange[1],
            **self.geo_plot_params,
        )
        nan_geo: gpd.GeoDataFrame = self.dfr.data[
            self.dfr.data[self.dfr.time_cols[i]].isna()
        ]

        if len(nan_geo) > 0:
            nan_geo.plot(ax=self.ax, **self.geo_nan_params)

        if self.annot_geo:
            self.dfr.annot_data.apply(
                lambda x: self.ax.annotate(
                    text=x[self.dfr.time_cols[i]],
                    xy=x.geometry.centroid.coords[0],
                    **self.annot_geo_params,
                ),
                axis=1,
            )
        super().update(i)
