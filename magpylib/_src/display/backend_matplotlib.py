"""matplotlib backend"""

# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=too-many-positional-arguments

import os
from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from matplotlib.animation import FuncAnimation

from magpylib._src.display.traces_utility import get_trace_kw
from magpylib._src.display.traces_utility import split_input_arrays
from magpylib._src.display.traces_utility import subdivide_mesh_by_facecolor
from magpylib._src.utility import is_array_like

if os.getenv("MAGPYLIB_MPL_SVG") == "true":  # pragma: no cover
    from matplotlib_inline.backend_inline import set_matplotlib_formats

    set_matplotlib_formats("svg")

SYMBOLS_TO_MATPLOTLIB = {
    "circle": "o",
    "cross": "+",
    "diamond": "d",
    "square": "s",
    "x": "x",
}

LINE_STYLES_TO_MATPLOTLIB = {
    "solid": "-",
    "dash": "--",
    "dashdot": "-.",
    "dot": (0, (1, 1)),
    "longdash": "loosely dotted",
    "longdashdot": "loosely dashdotted",
}


class StripedHandler:
    """
    Handler for creating a striped legend key using given color data.

    Parameters
    ----------
    color_data : dict
        Dictionary containing color names as keys and their respective proportions as values.

    Attributes
    ----------
    colors : list
        List of colors extracted from the color_data dictionary.
    proportions : list
        Normalized list of proportions extracted from the color_data dictionary.
    """

    def __init__(self, color_data):
        total = sum(color_data.values())
        self.colors = list(color_data.keys())
        self.proportions = [value / total for value in color_data.values()]

    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        # pylint: disable=unused-argument
        """Create custom legend key"""
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        width, height = handlebox.width, handlebox.height
        patch_width = width
        current_position = x0

        for color, proportion in zip(self.colors, self.proportions):
            handlebox.add_artist(
                patches.Rectangle(
                    [current_position, y0], patch_width * proportion, height, fc=color
                )
            )
            current_position += patch_width * proportion


def mesh3d_to_matplotlib(trace, antialiased):
    """Convert mesh3d trace input to a list of plot_trisurf constructor dicts
    Note: plot_trisurf does not accept different facecolors on the same trace
    so they need to be splitted into multiple traces
    """
    traces = []
    subtraces = [trace]
    has_facecolor = trace.get("facecolor", None) is not None
    if has_facecolor:
        subtraces = subdivide_mesh_by_facecolor(trace)
    for ind, subtrace in enumerate(subtraces):
        x, y, z = np.array([subtrace[k] for k in "xyz"], dtype=float)
        triangles = np.array([subtrace[k] for k in "ijk"]).T
        tr_mesh = {
            "constructor": "plot_trisurf",
            "args": (x, y, z),
            "kwargs": {
                "triangles": triangles,
                "alpha": subtrace.get("opacity", None),
                "color": subtrace.get("color", None),
                "linewidth": 0,
                "antialiased": antialiased,
            },
        }
        if trace.get("showlegend", True) and has_facecolor:
            tr_mesh["legend_handler"] = StripedHandler(Counter(trace["facecolor"]))
        if ind != 0:  # hide substrace legends except first
            tr_mesh["kwargs"]["label"] = "_nolegend_"
        traces.append(tr_mesh)
    return traces


def scatter_to_matplotlib(trace):
    """Convert scatter trace input to a list of plot or scatter constructor dicts
    Note on `scatter` constructor:
      - supports arrays for marker size and color, not symbol
      - no support for line
    Note on `plot` constructor:
      - support for line
      - no array support for marker size or marker color or line color or line style
    """
    traces = []

    # get kwargs
    mode = get_trace_kw(trace, "mode", none_replace="markers")
    line_color = get_trace_kw(trace, "line_color")
    line_width = get_trace_kw(trace, "line_width", none_replace=1)
    line_dash = get_trace_kw(trace, "line_dash")
    line_dash = LINE_STYLES_TO_MATPLOTLIB.get(line_dash, line_dash)
    marker_color = get_trace_kw(trace, "marker_color", none_replace=line_color)
    marker_size = get_trace_kw(trace, "marker_size", none_replace=1)
    marker_symbol = get_trace_kw(trace, "marker_symbol", none_replace="o")

    # get coords
    coords_str = "xyz"
    if trace["type"] == "scatter3d":
        # for 3d traces marker size is proportional to volume, not radius like generic
        marker_size = marker_size**3
    else:
        coords_str = "xy"
        # for 2d traces marker size is proportional to area, not radius like generic
        marker_size = marker_size**2

    coords = np.array([trace[k] for k in coords_str], dtype=float)

    # plot the marker part with `scatter` constructor
    if "markers" in mode:
        for (msymb,), inds in split_input_arrays(marker_symbol, ordered=False):
            msymb = SYMBOLS_TO_MATPLOTLIB.get(msymb, msymb)
            kw = {"s": marker_size, "color": marker_color}
            for k, v in kw.items():
                if is_array_like(v):
                    kw[k] = v[inds]
            traces.append(
                {
                    "constructor": "scatter",
                    "args": tuple(coords[:, inds]),
                    "kwargs": {"marker": msymb, "label": None, **kw},
                }
            )

    # plot the line part with `plot` constructor
    if "lines" in mode:
        for (lcolor, lwidth), inds in split_input_arrays(line_color, line_width):
            traces.append(
                {
                    "constructor": "plot",
                    "args": coords[:, inds],
                    "kwargs": {
                        "alpha": trace.get("opacity", 1),
                        "ls": line_dash,
                        "lw": lwidth,
                        "color": lcolor,
                    },
                }
            )
    # plot the test parts with `text` constructor
    if "text" in mode and trace.get("text", False) and len(coords) > 0:
        txt = trace["text"]
        txt = [txt] * len(coords[0]) if isinstance(txt, str) else txt
        for *coords_s, txt in zip(*coords, txt):
            traces.append({"constructor": "text", "args": (*coords_s, txt)})
    return traces


def generic_trace_to_matplotlib(trace, antialiased=True):
    """Transform a generic trace into a matplotlib trace"""
    traces_mpl = []
    if trace["type"] == "mesh3d":
        traces_mpl.extend(mesh3d_to_matplotlib(trace, antialiased))
    elif trace["type"] in ("scatter", "scatter3d"):
        traces_mpl.extend(scatter_to_matplotlib(trace))
    else:  # pragma: no cover
        raise ValueError(f"{trace['type']!r} trace type conversion not supported")
    for tr in traces_mpl:
        tr["row"] = trace.get("row", 1)
        tr["col"] = trace.get("col", 1)
        tr["kwargs"] = tr.get("kwargs", {})
        if tr["constructor"] != "text":
            if trace.get("showlegend", True):
                if "label" not in tr["kwargs"]:
                    tr["kwargs"]["label"] = trace.get("name", "")
                    leg_title = trace.get("legendgrouptitle_text", None)
                    if leg_title is not None:
                        tr["kwargs"]["label"] += f" ({leg_title})"
            else:
                tr["kwargs"]["label"] = "_nolegend"
    return traces_mpl


def extract_axis_from_row_col(fig, row, col):
    "Return axis from row and col values"

    def geom(ax):
        return ax.get_subplotspec().get_topmost_subplotspec().get_geometry()

    # get nrows and ncols of fig for first axis
    rc = geom(fig.axes[0])[:2]
    # get the axis index based on row first
    default_ind = rc[0] * (row - 1) + col - 1
    # get last index of geometry, gives the actual index,
    # since axis can be added in a different order
    inds = [geom(ax)[-1] for ax in fig.axes]
    # retrieve first index that matches
    ind = inds.index(default_ind)
    ax = fig.axes[ind]
    return ax


def process_extra_trace(model):
    "process extra trace attached to some magpylib object"
    trace3d = model.copy()
    kw = trace3d.pop("kwargs_extra")
    trace3d.update({"row": kw["row"], "col": kw["col"]})
    kw = {
        "alpha": kw["opacity"],
        "color": kw["color"],
        "label": kw["name"] if kw["showlegend"] else "_nolegend_",
    }
    trace3d["kwargs"] = {**kw, **trace3d["kwargs"]}
    return trace3d


def display_matplotlib(
    data,
    canvas=None,
    repeat=False,
    return_fig=False,
    canvas_update="auto",
    return_animation=False,
    max_rows=None,
    max_cols=None,
    subplot_specs=None,
    antialiased=True,
    legend_maxitems=20,
    fig_kwargs=None,
    show_kwargs=None,
    **kwargs,  # pylint: disable=unused-argument
):
    """Display objects and paths graphically using the matplotlib library."""
    frames = data["frames"]
    ranges = data["ranges"]
    labels = data["labels"]

    # only update layout if canvas is not provided
    fig_kwargs = {} if not fig_kwargs else fig_kwargs
    show_kwargs = {} if not show_kwargs else show_kwargs
    show_kwargs = {**show_kwargs}

    for fr in frames:
        new_data = []
        for tr in fr["data"]:
            new_data.extend(generic_trace_to_matplotlib(tr, antialiased=antialiased))
        for model in fr["extra_backend_traces"]:
            new_data.append(process_extra_trace(model))
        fr["data"] = new_data

    show_canvas = bool(canvas is None)
    axes = {}
    if canvas_update:
        fig_kwargs["dpi"] = fig_kwargs.get("dpi", 80)
        if fig_kwargs.get("figsize", None) is None:
            figsize = (8, 8)
            ratio = subplot_specs.shape[1] / subplot_specs.shape[0]
            if legend_maxitems != 0:
                ratio *= 1.5  # extend horizontal ratio if legend is present
            fig_kwargs["figsize"] = (figsize[0] * ratio, figsize[1])
    if canvas is None:
        fig = plt.figure(**{"tight_layout": True, **fig_kwargs})
    elif isinstance(canvas, matplotlib.axes.Axes):
        fig = canvas.get_figure()
        if max_rows is not None or max_cols is not None:
            raise ValueError(
                "Provided canvas is an instance of `matplotlib.axes.Axes` and does not support "
                "`rows` or `cols` attributes. Use an instance of `matplotlib.figure.Figure` "
                "instead"
            )
    elif isinstance(canvas, matplotlib.figure.Figure):
        fig = canvas
    else:
        raise TypeError(
            "The `canvas` parameter must be one of `[None, matplotlib.axes.Axes, "
            f"matplotlib.figure.Figure]`. Received type {type(canvas)!r} instead"
        )
    if canvas is not None and canvas_update:
        fig.set_size_inches(*fig_kwargs["figsize"], forward=True)
        fig.set_dpi(fig_kwargs["dpi"])
    if max_rows is None and max_cols is None:
        if isinstance(canvas, matplotlib.axes.Axes):
            axes[(1, 1)] = canvas
        else:
            sp_typ = subplot_specs[0, 0]["type"]
            axes[(1, 1)] = fig.add_subplot(
                111, projection="3d" if sp_typ == "scene" else None
            )
    else:
        max_rows = max_rows if max_rows is not None else 1
        max_cols = max_cols if max_cols is not None else 1
        count = 0
        for row in range(1, max_rows + 1):
            for col in range(1, max_cols + 1):
                subplot_found = True
                count += 1
                row_col_num = (row, col)
                projection = (
                    "3d" if subplot_specs[row - 1, col - 1]["type"] == "scene" else None
                )
                if isinstance(canvas, matplotlib.figure.Figure):
                    try:
                        axes[row_col_num] = extract_axis_from_row_col(fig, row, col)
                    except (ValueError, IndexError):  # IndexError if axis is not found
                        subplot_found = False
                if canvas is None or not subplot_found:
                    axes[row_col_num] = fig.add_subplot(
                        max_rows, max_cols, count, projection=projection
                    )
                if axes[row_col_num].name == "3d":
                    axes[row_col_num].set_box_aspect((1, 1, 1))

    def draw_frame(frame_ind):
        count_with_labels = {}
        handler_map = {}
        for tr in frames[frame_ind]["data"]:
            row_col_num = (tr["row"], tr["col"])
            ax = axes[row_col_num]
            constructor = tr["constructor"]
            args = tr.get("args", ())
            kwargs = tr.get("kwargs", {})
            if frame_ind == 0:
                if row_col_num not in count_with_labels:
                    count_with_labels[row_col_num] = 0
                label = kwargs.get("label", "_")
                if label and not label.startswith("_"):
                    count_with_labels[row_col_num] += 1
            trace = getattr(ax, constructor)(*args, **kwargs)
            if "legend_handler" in tr:
                handler_map[trace] = tr["legend_handler"]
            if constructor == "plot_trisurf":
                # 'Poly3DCollection' object has no attribute '_edgecolors2d'
                for arg in ("face", "edge"):
                    color = getattr(trace, f"_{arg}color3d", None)
                    color = (  # for mpl version <3.3.3
                        getattr(trace, f"_{arg}colors3d", None)
                        if color is None
                        else color
                    )
                    setattr(trace, f"_{arg}colors2d", color)
        for row_col_num, ax in axes.items():
            count = count_with_labels.get(row_col_num, 0)
            if ax.name == "3d":
                if row_col_num in ranges and canvas_update:
                    ax.set(
                        **{f"{k}label": labels[row_col_num][k] for k in "xyz"},
                        **{f"{k}lim": r for k, r in zip("xyz", ranges[row_col_num])},
                    )
                ax.set_box_aspect(aspect=(1, 1, 1))
                if 0 < count <= legend_maxitems:
                    lg_kw = {"bbox_to_anchor": (1.04, 1), "loc": "upper left"}
                    if handler_map:
                        lg_kw["handler_map"] = handler_map
                    try:
                        ax.legend(**lg_kw)
                    except AttributeError:
                        # see https://github.com/matplotlib/matplotlib/pull/25565
                        pass
            else:
                ax.legend(loc="best")

    def animate(ind):  # pragma: no cover
        for ax in axes.values():
            ax.clear()
        draw_frame(ind)
        return list(axes.values())

    anim = None
    if len(frames) == 1:
        draw_frame(0)
    else:
        anim = FuncAnimation(
            fig,
            animate,
            frames=range(len(frames)),
            interval=data["frame_duration"],
            blit=False,
            repeat=repeat,
        )

    out = ()
    if return_fig:
        show_canvas = False
        out += (fig,)
    if return_animation and len(frames) != 1:
        show_canvas = False
        out += (anim,)
    if show_canvas:
        plt.show(**show_kwargs)

    if out:
        return out[0] if len(out) == 1 else out
