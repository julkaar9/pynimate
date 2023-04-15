from typing import Callable

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


class Canvas:
    def __init__(
        self,
        nrows: int = 1,
        ncols: int = 1,
        figsize: tuple[int, int] = (16, 9),
        post_update: Callable[[plt.Figure, list[list[plt.Axes]]], None] = None,
        **kwargs,
    ) -> None:
        """Creates the matplotlib figure, subplots and additional figure properties.
        Also creates and saves the animation.

        Parameters
        ----------
        nrows : int, optional
            Number of rows of the subplot grid, by default 1
        ncols : int, optional
            Number of columns of the subplot grid, by default 1
        figsize : tuple[int, int], optional
            Width, height in inches, by default (16, 9)
        post_update : Callable[[plt.Figure, list[list[plt.Axes]]], None], optional
            callback function for additional figure customization, by default None

        post_update args:
        ```
            plt.Figure: Matplotlib figure
            list[list[plt.Axes]]]: Subplot Axes
        ```
        """
        self.post_update = post_update or (lambda *args: None)
        self.fig, self.ax = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)

        if nrows == 1 and ncols == 1:
            self.ax = np.array([[self.ax]])
        elif nrows == 1:
            self.ax = np.array([self.ax])
        self.plots = []
        self.length = 0

    def add_plot(self, plot, index: tuple[int, int] = (0, 0)) -> __qualname__:
        """Adds the plot to be animated with its ax index (for multiple subplots)

        Parameters
        ----------
        plot : Plot_like
            Plot to be animated
        index : tuple[int, int], optional
            Subplot index, by default (0, 0)

        Returns
        -------
        Canvas
            Returns the canvas instance
        """
        plot.set_axes(self.ax[index])
        self.length = max(self.length, plot.length)
        self.plots.append(plot)
        return self

    # def _init(self) -> None:
    #     for plot in self.plots:
    #         plot.init()

    def _update(self, i: int) -> None:
        self.post_update(self.fig, self.ax)
        for plot in self.plots:
            plot.update(min(plot.length - 1, i))

    def animate(
        self,
        frames_callback: Callable[[int], any] = lambda length: length,
        interval: int = 50,
        **kwargs,
    ) -> None:
        """Main module to create the animation, additional `kwargs` are passed to animation.FuncAnimation(**kwargs)

        Parameters
        ----------
        frames_callback : int, optional
            Passed to funcAnimation frames, by default lambda length: length
        interval : int, optional
            Interval between each frame. Defaults to 50ms, by default 50

        """
        self.ani = animation.FuncAnimation(
            self.fig,
            self._update,
            frames=frames_callback(self.length),
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
            Filename
        fps : int
            Video fps / frames per second
        extension : str, optional
            File extension, by default "gif"
        """
        self.ani.save(f"{filename}.{extension}", fps=fps, **kwargs)
