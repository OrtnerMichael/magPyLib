"""Display function codes"""

# pylint: disable=too-many-branches
# pylint: disable=too-many-positional-arguments

from collections import defaultdict
from functools import lru_cache
from itertools import chain
from itertools import cycle
from typing import Tuple

import numpy as np
from scipy.spatial.transform import Rotation as RotScipy

from magpylib._src.defaults.defaults_classes import default_settings
from magpylib._src.defaults.defaults_utility import linearize_dict
from magpylib._src.input_checks import check_input_zoom
from magpylib._src.style import get_style
from magpylib._src.utility import format_obj_input
from magpylib._src.utility import merge_dicts_with_conflict_check

DEFAULT_ROW_COL_PARAMS = {
    "row": 1,
    "col": 1,
    "output": "model3d",
    "sumup": True,
    "pixel_agg": "mean",
    "in_out": "auto",
    "zoom": 0,
    "units_length": "auto",
}


def get_legend_label(obj, style=None, suffix=True):
    """provides legend entry based on name and suffix"""
    style = obj.style if style is None else style
    name = style.label if style.label else obj.__class__.__name__
    legend_txt = style.legend.text
    if legend_txt:
        return legend_txt
    suff = ""
    if suffix and style.description.show:
        desc = style.description.text
        if not desc:
            desc = getattr(obj, "_default_style_description", "")
        if desc:
            suff = f" ({desc})"
    return f"{name}{suff}"


def place_and_orient_model3d(
    model_kwargs,
    *,
    model_args=None,
    orientation=None,
    position=None,
    coordsargs=None,
    scale=1,
    return_model_args=False,
    return_coordsargs=False,
    length_factor=1,
    **kwargs,
):
    """places and orients mesh3d dict"""
    if orientation is None and position is None and length_factor == 1:
        new_model_kwargs = {**model_kwargs, **kwargs}
        new_model_args = model_args
    else:
        position = (0.0, 0.0, 0.0) if position is None else position
        position = np.array(position, dtype=float)
        new_model_dict = {}
        if model_args is None:
            model_args = ()
        new_model_args = list(model_args)
        vertices, coordsargs, useargs = get_vertices_from_model(
            model_kwargs, model_args, coordsargs
        )
        # sometimes traces come as (n,m,3) shape
        vert_shape = vertices.shape
        vertices = np.reshape(vertices.astype(float), (3, -1))

        vertices = vertices.T

        if orientation is not None:
            vertices = orientation.apply(vertices)
        new_vertices = (vertices * scale + position).T * length_factor
        new_vertices = np.reshape(new_vertices, vert_shape)
        for i, k in enumerate("xyz"):
            key = coordsargs[k]
            if useargs:
                ind = int(key[5])
                new_model_args[ind] = new_vertices[i]
            else:
                new_model_dict[key] = new_vertices[i]
        new_model_kwargs = {**model_kwargs, **new_model_dict, **kwargs}

    out = (new_model_kwargs,)
    if return_model_args:
        out += (new_model_args,)
    if return_coordsargs:
        out += (coordsargs,)
    return out[0] if len(out) == 1 else out


def get_vertices_from_model(model_kwargs, model_args=None, coordsargs=None):
    """get vertices from model kwargs and args"""
    if model_args:
        if coordsargs is None:  # matplotlib default
            coordsargs = {"x": "args[0]", "y": "args[1]", "z": "args[2]"}
    vertices = []
    if coordsargs is None:
        coordsargs = {"x": "x", "y": "y", "z": "z"}
    useargs = False
    for k in "xyz":
        key = coordsargs[k]
        if key.startswith("args"):
            useargs = True
            ind = int(key[5])
            v = model_args[ind]
        else:
            if key in model_kwargs:
                v = model_kwargs[key]
            else:
                raise ValueError(
                    "Rotating/Moving of provided model failed, trace dictionary "
                    f"has no argument {k!r}, use `coordsargs` to specify the names of the "
                    "coordinates to be used.\n"
                    "Matplotlib backends will set up coordsargs automatically if "
                    "the `args=(xs,ys,zs)` argument is provided."
                )
        vertices.append(v)

    vertices = np.array(vertices)
    return vertices, coordsargs, useargs


def draw_arrowed_line(
    vec,
    pos,
    sign=1,
    arrow_size=0.1,
    arrow_pos=0.5,
    pivot="middle",
    include_line=True,
) -> Tuple:
    """
    Provides x,y,z coordinates of an arrow drawn in the x-y-plane (z=0), showing up the y-axis and
    centered in x,y,z=(0,0,0). The arrow vertices are then turned in the direction of `vec` and
    moved to position `pos`.
    """
    norm = np.linalg.norm(vec)
    nvec = np.array(vec) / norm
    yaxis = np.array([0, 1, 0])
    cross = np.cross(nvec, yaxis)
    dot = np.dot(nvec, yaxis)
    n = np.linalg.norm(cross)
    arrow_shift = arrow_pos - 0.5
    hx = 0.6 * arrow_size
    hy = np.sign(sign) * arrow_size
    anchor = (
        (0, -0.5, 0)
        if pivot == "tip"
        else (0, 0.5, 0) if pivot == "tail" else (0, 0, 0)
    )
    arrow = [
        [0, arrow_shift, 0],
        [-hx, arrow_shift - hy, 0],
        [0, arrow_shift, 0],
        [hx, arrow_shift - hy, 0],
        [0, arrow_shift, 0],
    ]
    if include_line:
        arrow = [[0, -0.5, 0], *arrow, [0, 0.5, 0]]
    else:
        arrow = [[0, -0.5, 0], [np.nan] * 3, *arrow, [np.nan] * 3, [0, 0.5, 0]]
    arrow = (np.array(arrow) + np.array(anchor)) * norm

    if n == 0 and dot == -1:
        R = RotScipy.from_rotvec([0, 0, np.pi])
        arrow = R.apply(arrow)
    elif n != 0:
        t = np.arccos(dot)
        R = RotScipy.from_rotvec(-t * cross / n)
        arrow = R.apply(arrow)
    return arrow + pos


def draw_arrow_from_vertices(
    vertices, sign, arrow_size, arrow_pos=0.5, scaled=True, include_line=True
):
    """returns scatter coordinates of arrows between input vertices"""
    vectors = np.diff(vertices, axis=0)
    if scaled:
        arrow_sizes = [arrow_size * 0.1] * (len(vertices) - 1)
    else:
        vec_lens = np.linalg.norm(vectors, axis=1)
        mask0 = vec_lens == 0
        vec_lens[mask0] = 1
        arrow_sizes = arrow_size / vec_lens
        arrow_sizes[mask0] = 0
    positions = vertices[:-1] + vectors / 2
    vertices = np.concatenate(
        [
            draw_arrowed_line(
                vec,
                pos,
                sign,
                arrow_size=siz,
                arrow_pos=arrow_pos,
                include_line=include_line,
            ).T
            for vec, pos, siz in zip(vectors, positions, arrow_sizes)
        ],
        axis=1,
    )

    return vertices.T


def draw_arrow_on_circle(sign, diameter, arrow_size, scaled=True, angle_pos_deg=0):
    """draws an oriented circle with an arrow"""
    if scaled:
        hy = 0.2 * arrow_size
    else:
        hy = arrow_size / diameter * 2
    hx = 0.6 * hy
    hy *= np.sign(sign)
    x = np.array([1 + hx, 1, 1 - hx]) * diameter / 2
    y = np.array([-hy, 0, -hy]) * diameter / 2
    z = np.zeros(x.shape)
    vertices = np.array([x, y, z]).T
    if angle_pos_deg != 0:
        rot = RotScipy.from_euler("z", angle_pos_deg, degrees=True)
        vertices = rot.apply(vertices)
    return vertices


def get_rot_pos_from_path(obj, show_path=None):
    """
    subsets orientations and positions depending on `show_path` value.
    examples:
    show_path = [1,2,8], path_len = 6 -> path_indices = [1,2,6]
    returns rots[[1,2,6]], poss[[1,2,6]]
    """
    # pylint: disable=protected-access
    # pylint: disable=invalid-unary-operand-type
    if show_path is None:
        show_path = True
    pos = obj._position
    orient = obj._orientation
    path_len = pos.shape[0]
    if show_path is True or show_path is False or show_path == 0:
        inds = np.array([-1])
    elif isinstance(show_path, int):
        inds = np.arange(path_len, dtype=int)[::-show_path]
    elif hasattr(show_path, "__iter__") and not isinstance(show_path, str):
        inds = np.array(show_path)
    else:  # pragma: no cover
        raise ValueError(f"Invalid show_path value ({show_path})")
    inds[inds >= path_len] = path_len - 1
    inds = np.unique(inds)
    if inds.size == 0:
        inds = np.array([path_len - 1])
    rots = orient[inds]
    poss = pos[inds]
    return rots, poss, inds


def get_objects_props_by_row_col(*objs, colorsequence, style_kwargs):
    """Return flat dict with objs as keys object properties as values.
    Properties include: row_cols, style, legendgroup, legendtext"""
    flat_objs_rc = {}
    rc_params_by_obj = {}
    obj_list_semi_flat = [o for obj in objs for o in obj["objects"]]
    for obj in objs:
        rc_params = {k: v for k, v in obj.items() if k != "objects"}
        for subobj in obj["objects"]:
            children = getattr(subobj, "children_all", [])
            for child in chain([subobj], children):
                if child not in rc_params_by_obj:
                    rc_params_by_obj[child] = []
                rc_params_by_obj[child].append(rc_params)
    flat_sub_objs = get_flatten_objects_properties_recursive(
        *obj_list_semi_flat,
        style_kwargs=style_kwargs,
        colorsequence=colorsequence,
    )
    for obj, rc_params_list in rc_params_by_obj.items():
        for rc_params in rc_params_list:
            rc = rc_params["row"], rc_params["col"]
            if rc not in flat_objs_rc:
                flat_objs_rc[rc] = {"objects": {}, "rc_params": rc_params}
            flat_objs_rc[rc]["objects"][obj] = flat_sub_objs[obj]
    return flat_objs_rc


def get_flatten_objects_properties_recursive(
    *obj_list_semi_flat,
    style_kwargs=None,
    colorsequence=None,
    color_cycle=None,
    parent_legendgroup=None,
    parent_color=None,
    parent_label=None,
    parent_showlegend=None,
):
    """returns a flat dict -> (obj: display_props, ...) from nested collections"""
    if color_cycle is None:
        color_cycle = cycle(colorsequence)
    flat_objs = {}
    for subobj in dict.fromkeys(obj_list_semi_flat):
        isCollection = getattr(subobj, "children", None) is not None
        style_kwargs = {} if style_kwargs is None else style_kwargs
        style = get_style(subobj, default_settings, **style_kwargs)
        if style.label is None:
            style.label = str(type(subobj).__name__)
        legendgroup = f"{subobj}" if parent_legendgroup is None else parent_legendgroup
        label = (
            get_legend_label(subobj, style=style)
            if parent_label is None
            else parent_label
        )
        if parent_color is not None and style.color is None:
            style.color = parent_color
        elif style.color is None:
            style.color = next(color_cycle)
        flat_objs[subobj] = {
            "legendgroup": legendgroup,
            "style": style,
            "legendtext": label,
            "showlegend": parent_showlegend,
        }
        if isCollection:
            new_ojbs = get_flatten_objects_properties_recursive(
                *subobj.children,
                colorsequence=colorsequence,
                color_cycle=color_cycle,
                parent_legendgroup=legendgroup,
                parent_color=style.color,
                parent_label=label,
                parent_showlegend=style.legend.show,
                style_kwargs=style_kwargs,
            )
            flat_objs = {**new_ojbs, **flat_objs}
    return flat_objs


def merge_mesh3d(*traces):
    """Merges a list of plotly mesh3d dictionaries. The `i,j,k` index parameters need to cumulate
    the indices of each object in order to point to the right vertices in the concatenated
    vertices. `x,y,z,i,j,k` are mandatory fields, the `intensity` and `facecolor` parameters also
    get concatenated if they are present in all objects. All other parameter found in the
    dictionary keys are taken from the first object, other keys from further objects are ignored.
    """
    merged_trace = {}
    L = np.array([0] + [len(b["x"]) for b in traces[:-1]]).cumsum()
    for k in "ijk":
        if k in traces[0]:
            merged_trace[k] = np.hstack([b[k] + l for b, l in zip(traces, L)])
    for k in "xyz":
        merged_trace[k] = np.concatenate([b[k] for b in traces])
    for k in ("intensity", "facecolor"):
        if k in traces[0] and traces[0][k] is not None:
            merged_trace[k] = np.hstack([b[k] for b in traces])
    for k, v in traces[0].items():
        if k not in merged_trace:
            merged_trace[k] = v
    return merged_trace


def merge_scatter3d(*traces):
    """Merges a list of plotly scatter3d. `x,y,z` are mandatory fields and are concatenated with a
    `None` vertex to prevent line connection between objects to be concatenated. Keys are taken
    from the first object, other keys from further objects are ignored.
    """
    if len(traces) == 1:
        return traces[0]
    mode = traces[0].get("mode")
    mode = "" if mode is None else mode
    if not mode:
        traces[0]["mode"] = "markers"
    no_gap = "line" not in mode

    merged_trace = {}
    for k in "xyz":
        if no_gap:
            stack = [b[k] for b in traces]
        else:
            stack = [pts for b in traces for pts in [[None], b[k]]]
        merged_trace[k] = np.hstack(stack)
    for k, v in traces[0].items():
        if k not in merged_trace:
            merged_trace[k] = v
    return merged_trace


def aggregate_by_trace_type(traces):
    """aggregate traces by type"""
    result_dict = defaultdict(list)
    for item in traces:
        result_dict[item["type"]].append(item)
    yield from result_dict.items()


def merge_traces(*traces):
    """Merges a list of plotly 3d-traces. Supported trace types are `mesh3d` and `scatter3d`.
    All traces have be of the same type when merging. Keys are taken from the first object, other
    keys from further objects are ignored.
    """
    new_traces = []
    for ttype, tlist in aggregate_by_trace_type(traces):
        if len(tlist) > 1:
            if ttype == "mesh3d":
                new_traces.append(merge_mesh3d(*tlist))
            elif ttype == "scatter3d":
                new_traces.append(merge_scatter3d(*tlist))
            else:  # pragma: no cover
                new_traces.extend(tlist)
        elif len(tlist) == 1:
            new_traces.append(tlist[0])
    return new_traces


def getIntensity(vertices, axis) -> np.ndarray:
    """Calculates the intensity values for vertices based on the distance of the vertices to
    the mean vertices position in the provided axis direction. It can be used for plotting
    fields on meshes. If `mag` See more infos here:https://plotly.com/python/3d-mesh/

    Parameters
    ----------
    vertices : ndarray, shape (n,3)
        The n vertices of the mesh object.
    axis : ndarray, shape (3,)
        Direction vector.

    Returns
    -------
    Intensity values: ndarray, shape (n,)
    """
    p = np.array(vertices).T
    pos = np.mean(p, axis=1)
    m = np.array(axis)
    intensity = (p[0] - pos[0]) * m[0] + (p[1] - pos[1]) * m[1] + (p[2] - pos[2]) * m[2]
    # normalize to interval [0,1] (necessary for when merging mesh3d traces)
    ptp = np.ptp(intensity)
    ptp = ptp if ptp != 0 else 1
    intensity = (intensity - np.min(intensity)) / ptp
    return intensity


@lru_cache(maxsize=32)
def getColorscale(
    color_transition=0,
    color_north="#E71111",  # 'red'
    color_middle="#DDDDDD",  # 'grey'
    color_south="#00B050",  # 'green'
):
    """Provides the colorscale for a plotly mesh3d trace. The colorscale must be an array
    containing arrays mapping a normalized value to an rgb, rgba, hex, hsl, hsv, or named
    color string. At minimum, a mapping for the lowest (0) and highest (1) values is required.
    For example, `[[0, 'rgb(0,0,255)'], [1,'rgb(255,0,0)']]`. In this case the colorscale
    is created depending on the north/middle/south poles colors. If the middle color is
    None, the colorscale will only have north and south pole colors.

    Parameters
    ----------
    color_transition : float, default=0.1
        A value between 0 and 1. Sets the smoothness of the color transitions from adjacent colors
        visualization.
    color_north : str, default=None
        Magnetic north pole color.
    color_middle : str, default=None
        Color of area between south and north pole.
    color_south : str, default=None
        Magnetic north pole color.

    Returns
    -------
    colorscale: list
        Colorscale as list of tuples.
    """
    if color_middle is False:
        colorscale = (
            (0.0, color_south),
            (0.5 * (1 - color_transition), color_south),
            (0.5 * (1 + color_transition), color_north),
            (1, color_north),
        )
    else:
        colorscale = (
            (0.0, color_south),
            (0.2 - 0.2 * (color_transition), color_south),
            (0.2 + 0.3 * (color_transition), color_middle),
            (0.8 - 0.3 * (color_transition), color_middle),
            (0.8 + 0.2 * (color_transition), color_north),
            (1.0, color_north),
        )
    return colorscale


def get_scene_ranges(*traces, zoom=0) -> np.ndarray:
    """
    Returns 3x2 array of the min and max ranges in x,y,z directions of input traces. Traces can be
    any plotly trace object or a dict, with x,y,z numbered parameters.
    """
    ranges_rc = {}
    tr_dim_count = {}
    for tr in traces:
        coords = "xyz"
        rc = tr.get("row", 1), tr.get("col", 1)
        if "constructor" in tr:
            verts, *_ = get_vertices_from_model(
                model_args=tr.get("args", None),
                model_kwargs=tr.get("kwargs", None),
                coordsargs=tr.get("coordsargs", None),
            )
            kwex = tr["kwargs_extra"]
            tr = dict(zip("xyz", verts))
            rc = kwex["row"], kwex["col"]
        if rc not in ranges_rc:
            ranges_rc[rc] = {k: [] for k in "xyz"}
            tr_dim_count[rc] = {"2D": 0, "3D": 0}
        if "z" not in tr:  # only extend range for 3d traces
            tr_dim_count[rc]["2D"] += 1
        else:
            tr_dim_count[rc]["3D"] += 1
            pts = np.array([tr[k] for k in coords], dtype="float64").T
            try:  # for mesh3d, use only vertices part of faces for range calculation
                inds = np.array([tr[k] for k in "ijk"], dtype="int64").T
                pts = pts[inds]
            except KeyError:
                # for 2d meshes, nothing special needed
                pass
            pts = pts.reshape(-1, 3)
            if pts.size != 0:
                min_max = np.nanmin(pts, axis=0), np.nanmax(pts, axis=0)
                for v, min_, max_ in zip(ranges_rc[rc].values(), *min_max):
                    v.extend([min_, max_])
    for rc, ranges in ranges_rc.items():
        if tr_dim_count[rc]["3D"]:
            zo = zoom[rc] if isinstance(zoom, dict) else zoom
            # SET 3D PLOT BOUNDARIES
            # collect min/max from all elements
            r = np.array([[np.nanmin(v), np.nanmax(v)] for v in ranges.values()])
            size = np.diff(r, axis=1)
            m = size.max() / 2
            m = 1 if m == 0 else m
            center = r.mean(axis=1)
            ranges = np.array([center - m * (1 + zo), center + m * (1 + zo)]).T
        else:
            ranges = np.array([[-1.0, 1.0]] * 3)
        ranges_rc[rc] = ranges
    if not ranges_rc:
        ranges_rc[(1, 1)] = np.array([[-1.0, 1.0]] * 3)
    return ranges_rc


def rescale_traces(traces, factors):
    """Rescale traces based on scale factors by (row,col) index"""
    for ind, tr in enumerate(traces):
        if "constructor" in tr:
            kwex = tr["kwargs_extra"]
            rc = kwex["row"], kwex["col"]
            kwargs, args = place_and_orient_model3d(
                model_kwargs=tr.get("kwargs", None),
                model_args=tr.get("args", None),
                coordsargs=tr.get("coordsargs", None),
                length_factor=factors[rc],
                return_model_args=True,
            )
            tr["kwargs"].update(kwargs)
            tr["args"] = args
        if "z" in tr:  # rescale only 3d traces
            rc = tr.get("row", 1), tr.get("col", 1)
            traces[ind] = place_and_orient_model3d(tr, length_factor=factors[rc])
    return traces


def group_traces(*traces):
    """Group and merge mesh traces with similar properties. This drastically improves
    browser rendering performance when displaying a lot of mesh3d objects."""
    mesh_groups = {}
    common_keys = ["legendgroup", "opacity", "row", "col", "color"]
    spec_keys = {
        "mesh3d": ["colorscale", "color", "facecolor"],
        "scatter3d": [
            "marker",
            "line_dash",
            "line_color",
            "line_width",
            "marker_color",
            "marker_symbol",
            "marker_size",
            "mode",
        ],
    }
    for tr in traces:
        tr = linearize_dict(
            tr,
            separator="_",
        )
        gr = [tr["type"]]
        for k in [*common_keys, *spec_keys.get(tr["type"], [])]:
            if k == "facecolor":
                v = tr.get(k, None) is None
            else:
                v = tr.get(k, "")
            gr.append(str(v))
        gr = "".join(gr)
        if gr not in mesh_groups:
            mesh_groups[gr] = []
        mesh_groups[gr].append(tr)

    traces = []
    for group in mesh_groups.values():
        traces.extend(merge_traces(*group))
    return traces


def subdivide_mesh_by_facecolor(trace):
    """Subdivide a mesh into a list of meshes based on facecolor"""
    facecolor = trace["facecolor"] = np.array(trace["facecolor"])
    subtraces = []
    # pylint: disable=singleton-comparison
    facecolor[facecolor == np.array(None)] = "black"
    for color in np.unique(facecolor):
        mask = facecolor == color
        new_trace = trace.copy()
        uniq = np.unique(np.hstack([np.array(trace[k])[mask] for k in "ijk"]))
        new_inds = np.arange(len(uniq))
        mapping_ar = np.zeros(uniq.max() + 1, dtype=new_inds.dtype)
        mapping_ar[uniq] = new_inds
        for k in "ijk":
            new_trace[k] = mapping_ar[np.array(trace[k])[mask]]
        for k in "xyz":
            new_trace[k] = new_trace[k][uniq]
        new_trace["color"] = color
        new_trace.pop("facecolor")
        subtraces.append(new_trace)
    return subtraces


def process_show_input_objs(objs, **kwargs):
    """Extract max_rows and max_cols from obj list of dicts"""
    defaults = DEFAULT_ROW_COL_PARAMS.copy()
    identifiers = ("row", "col")
    unique_fields = tuple(k for k in defaults if k not in identifiers)
    sources_and_sensors_only = []
    new_objs = []
    for obj in objs:
        # add missing kwargs
        if isinstance(obj, dict):
            obj = {**defaults, **obj, **kwargs}
        else:
            obj = {**defaults, "objects": obj, **kwargs}

        # extend objects list
        obj["objects"] = format_obj_input(
            obj["objects"], allow="sources+sensors+collections"
        )
        sources_and_sensors_only.extend(
            format_obj_input(obj["objects"], allow="sources+sensors")
        )
        new_objs.append(obj)

    row_col_dict = merge_dicts_with_conflict_check(
        new_objs,
        target="objects",
        identifiers=identifiers,
        unique_fields=unique_fields,
    )

    # create subplot specs grid
    row_cols = [*row_col_dict]
    max_rows, max_cols = np.max(row_cols, axis=0).astype(int) if row_cols else (1, 1)
    # convert to int to avoid np.int32 type conflicting with plolty subplot specs
    max_rows, max_cols = int(max_rows), int(max_cols)
    specs = np.array([[{"type": "scene"}] * max_cols] * max_rows)
    for rc, obj in row_col_dict.items():
        if obj["output"] != "model3d":
            specs[rc[0] - 1, rc[1] - 1] = {"type": "xy"}
    if max_rows == 1 and max_cols == 1:
        max_rows = max_cols = None

    for obj in row_col_dict.values():
        check_input_zoom(obj.get("zoom", None))

    return (
        list(row_col_dict.values()),
        list(dict.fromkeys(sources_and_sensors_only)),
        max_rows,
        max_cols,
        specs,
    )


def triangles_area(triangles):
    """Return area of triangles of shape (n,3,3) into an array of shape n"""
    norm = np.cross(
        triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0], axis=1
    )
    return np.linalg.norm(norm, axis=1) / 2


def slice_mesh_with_plane(
    verts, tris, plane_orig=(0.0, 0.0, 0.0), plane_axis=(1.0, 0.0, 0.0)
):
    """Slice a mesh obj defined by vertices an triangles by a plane defined by its
    origin and axis. Returns two (verts, tris) tuples for left and right side."""
    dists = np.dot(verts - plane_orig, plane_axis)

    if np.any(dists == 0):
        # if planes passes some vertices shift vertices slightly
        # IMPROVE-> make special case without a hack like this
        verts += np.array([129682, -986394, 123495]) * 1e-16
        dists = np.dot(verts - plane_orig, plane_axis)
    all_dists = dists[tris]

    mask_left = np.all(all_dists < 0, axis=1)
    mask_right = np.all(all_dists > 0, axis=1)
    mask_cut = np.any(all_dists < 0, axis=1) & np.any(all_dists > 0, axis=1)
    tri_cut = mask_cut.nonzero()[0]

    d = all_dists.copy()[mask_cut]
    t = tris.copy()[tri_cut]

    s = d[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 3, 2)  # pairs of distances

    # make sure the first two edges are the one intersected, if not cycle it
    im = np.prod(s, axis=2) < 0  # edge intersects if product of dist<0
    m1 = im[:, [0, 2]].sum(axis=1) == 2
    m2 = im[:, [1, 2]].sum(axis=1) == 2
    if np.any(m1):
        t[m1] = t[m1][:, [2, 0, 1]]
        s[m1] = s[m1][:, [2, 0, 1]]
        d[m1] = d[m1][:, [2, 0, 1]]
    if np.any(m2):
        t[m2] = t[m2][:, [1, 2, 0]]
        s[m2] = s[m2][:, [1, 2, 0]]
        d[m2] = d[m2][:, [1, 2, 0]]
    f = verts[t]

    p = np.abs(s).sum(axis=2)  # projected dists to plane

    e = f[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 3, 2, 3)  # edges
    v = np.squeeze(np.diff(e, axis=2))  # edges vectors

    pts = (f + v * (np.abs(d) / p).reshape(-1, 3, 1))[:, :2]

    f5 = np.concatenate([f, pts], axis=1)
    f1 = f5[:, [[3, 1, 4]]]
    f2 = f5[:, [[0, 3, 2], [3, 4, 2]]]

    fl1 = f1[d[:, 0] > 0].reshape(-1, 3, 3)
    fr1 = f1[d[:, 0] < 0].reshape(-1, 3, 3)
    fl2 = f2[d[:, 0] < 0].reshape(-1, 3, 3)
    fr2 = f2[d[:, 0] > 0].reshape(-1, 3, 3)

    fl0 = verts[tris[mask_left]]
    fr0 = verts[tris[mask_right]]

    fl = np.concatenate([fl0, fl1, fl2]).reshape((-1, 3))
    fr = np.concatenate([fr0, fr1, fr2]).reshape((-1, 3))

    vr, tr = np.unique(fr, axis=0, return_inverse=True)
    tr = tr.reshape((-1, 3))

    vl, tl = np.unique(fl, axis=0, return_inverse=True)
    tl = tl.reshape((-1, 3))
    return (vl, tl), (vr, tr)


def slice_mesh_from_colorscale(trace, axis, colorscale):
    """Slice mesh3d obj by axis and colorsale. Return single mesh dict with according
    facecolor argument."""
    cs = colorscale
    origs = np.array(list(dict.fromkeys([v[0] for v in cs])))[1:-1]
    colors = list(dict.fromkeys([v[1] for v in cs]))
    vr = np.array([v for k, v in trace.items() if k in "xyz"]).T
    tr = np.array([v for k, v in trace.items() if k in "ijk"]).T
    axis = axis / np.linalg.norm(axis)
    dists = np.dot(vr + np.mean(vr, axis=0), axis)
    ptp = np.ptp(dists)
    shift = np.mean([vr[np.argmin(dists)], vr[np.argmax(dists)]], axis=0)
    origs = np.vstack((origs - 0.5) * ptp) * axis + shift

    traces = []
    for ind, color in enumerate(colors):
        if ind < len(origs):
            (vl, tl), (vr, tr) = slice_mesh_with_plane(vr, tr, origs[ind], axis)
        else:
            vl, tl = vr, tr
        trace_temp = dict(zip("xyzijk", [*vl.T, *tl.T]))
        trace_temp.update(facecolor=np.array([color] * len(tl)))
        traces.append(trace_temp)
    return {**trace, **merge_mesh3d(*traces)}


def create_null_dim_trace(color=None, **kwargs):
    """Returns a simple trace with single markers"""
    trace = {
        "type": "scatter3d",
        "x": [0],
        "y": [0],
        "z": [0],
        "mode": "markers",
        "marker_size": 10,
    }
    if color is not None:
        trace["marker_color"] = color
    return {**trace, **kwargs}
