""" Display function codes"""

import warnings
from contextlib import contextmanager
from importlib import import_module

from matplotlib.axes import Axes as mplAxes
from matplotlib.figure import Figure as mplFig

from magpylib._src.defaults.defaults_utility import _DefaultValue
from magpylib._src.defaults.defaults_utility import get_defaults_dict
from magpylib._src.display.traces_generic import MagpyMarkers
from magpylib._src.display.traces_generic import get_frames
from magpylib._src.display.traces_utility import DEFAULT_ROW_COL_PARAMS
from magpylib._src.display.traces_utility import process_show_input_objs
from magpylib._src.input_checks import check_format_input_backend
from magpylib._src.input_checks import check_format_input_vector
from magpylib._src.input_checks import check_input_animation
from magpylib._src.input_checks import check_input_canvas_update
from magpylib._src.utility import check_path_format

disp_args = set(get_defaults_dict("display"))


class RegisteredBackend:
    """Base class for display backends"""

    backends = {}

    def __init__(
        self,
        *,
        name,
        show_func,
        supports_animation,
        supports_subplots,
        supports_colorgradient,
        supports_animation_output,
    ):
        self.name = name
        self.show_func = show_func
        self.supports = {
            "animation": supports_animation,
            "subplots": supports_subplots,
            "colorgradient": supports_colorgradient,
            "animation_output": supports_animation_output,
        }
        self._register_backend(name)

    def _register_backend(self, name):
        self.backends[name] = self

    @classmethod
    def show(
        cls,
        *objs,
        backend,
        title=None,
        max_rows=None,
        max_cols=None,
        subplot_specs=None,
        **kwargs,
    ):
        """Display function of the current backend"""
        self = cls.backends[backend]
        fallback = {
            "animation": {"animation": False},
            "subplots": {"row": None, "col": None},
            "animation_output": {"animation_output": None},
        }
        for name, params in fallback.items():
            condition = not all(kwargs.get(k, v) == v for k, v in params.items())
            if condition and not self.supports[name]:
                supported = [k for k, v in self.backends.items() if v.supports[name]]
                supported_str = (
                    f"one of {supported!r}"
                    if len(supported) > 1
                    else f"{supported[0]!r}"
                )
                warnings.warn(
                    f"The {backend!r} backend does not support {name!r}, "
                    f"you need to use {supported_str} instead."
                    f"\nFalling back to: {params}"
                )
                kwargs.update(params)
        display_kwargs = {
            k: v
            for k, v in kwargs.items()
            if any(k.startswith(arg) for arg in disp_args)
        }
        kwargs = {k: v for k, v in kwargs.items() if k not in display_kwargs}
        backend_kwargs = {
            k[len(backend) + 1 :]: v
            for k, v in kwargs.items()
            if k.startswith(f"{backend.lower()}_")
        }
        backend_kwargs = {**kwargs.pop(backend, {}), **backend_kwargs}
        kwargs = {k: v for k, v in kwargs.items() if not k.startswith(backend)}
        fig_kwargs = {
            **kwargs.pop("fig", {}),
            **{k[4:]: v for k, v in kwargs.items() if k.startswith("fig_")},
            **backend_kwargs.pop("fig", {}),
            **{k[4:]: v for k, v in backend_kwargs.items() if k.startswith("fig_")},
        }
        show_kwargs = {
            **kwargs.pop("show", {}),
            **{k[5:]: v for k, v in kwargs.items() if k.startswith("show_")},
            **backend_kwargs.pop("show", {}),
            **{k[5:]: v for k, v in backend_kwargs.items() if k.startswith("show_")},
        }
        kwargs = {
            k: v
            for k, v in kwargs.items()
            if not (k.startswith("fig") or k.startswith("show"))
        }
        data = get_frames(
            objs,
            supports_colorgradient=self.supports["colorgradient"],
            backend=backend,
            title=title,
            **display_kwargs,
        )
        return self.show_func(
            data,
            max_rows=max_rows,
            max_cols=max_cols,
            subplot_specs=subplot_specs,
            fig_kwargs=fig_kwargs,
            show_kwargs=show_kwargs,
            **kwargs,
        )


def get_show_func(backend):
    """Return the backend show function"""
    # defer import to show call. Importerror should only fail if unavalaible backend is called
    return lambda *args, backend=backend, **kwargs: getattr(
        import_module(f"magpylib._src.display.backend_{backend}"), f"display_{backend}"
    )(*args, **kwargs)


def infer_backend(canvas):
    """Infers the plotting backend from canvas and environment"""
    # pylint: disable=import-outside-toplevel
    backend = "matplotlib"
    in_notebook = False
    plotly_available = False
    try:
        import plotly  # pylint: disable=unused-import

        from magpylib._src.utility import is_notebook

        plotly_available = True
        in_notebook = is_notebook()
        if in_notebook:
            backend = "plotly"
    except ImportError:  # pragma: no cover
        pass
    if isinstance(canvas, (mplAxes, mplFig)):
        backend = "matplotlib"
    elif plotly_available and isinstance(
        canvas, (plotly.graph_objects.Figure, plotly.graph_objects.FigureWidget)
    ):
        backend = "plotly"
    else:
        try:
            import pyvista  # pylint: disable=unused-import

            if isinstance(canvas, pyvista.Plotter):
                backend = "pyvista"
        except ImportError:  # pragma: no cover
            pass
    return backend


def _show(
    *objects,
    animation=False,
    markers=None,
    canvas=None,
    canvas_update=None,
    backend=None,
    **kwargs,
):
    """Display objects and paths graphically.

    See `show` function for docstring details.
    """

    # process input objs
    objects, obj_list_flat, max_rows, max_cols, subplot_specs = process_show_input_objs(
        objects,
        **{k: v for k, v in kwargs.items() if k in DEFAULT_ROW_COL_PARAMS},
    )
    kwargs = {k: v for k, v in kwargs.items() if k not in DEFAULT_ROW_COL_PARAMS}
    canvas_update = check_input_canvas_update(canvas_update, canvas)
    # test if every individual obj_path is good
    check_path_format(obj_list_flat)

    # input checks
    backend = check_format_input_backend(backend)
    check_input_animation(animation)
    check_format_input_vector(
        markers,
        dims=(2,),
        shape_m1=3,
        sig_name="markers",
        sig_type="array_like of shape (n,3)",
        allow_None=True,
    )

    if markers:
        objects.append({"objects": [MagpyMarkers(*markers)], **DEFAULT_ROW_COL_PARAMS})

    if backend == "auto":
        backend = infer_backend(canvas)

    return RegisteredBackend.show(
        backend=backend,
        *objects,
        animation=animation,
        canvas=canvas,
        canvas_update=canvas_update,
        subplot_specs=subplot_specs,
        max_rows=max_rows,
        max_cols=max_cols,
        **kwargs,
    )


def show(
    *objects,
    # pylint: disable=unused-argument
    backend=_DefaultValue,
    canvas=_DefaultValue,
    animation=_DefaultValue,
    zoom=_DefaultValue,
    markers=_DefaultValue,
    return_fig=_DefaultValue,
    canvas_update=_DefaultValue,
    row=_DefaultValue,
    col=_DefaultValue,
    output=_DefaultValue,
    sumup=_DefaultValue,
    pixel_agg=_DefaultValue,
    style=_DefaultValue,
    **kwargs,
):
    """Display objects and paths graphically.

    Global graphic styles can be set with kwargs as style dictionary or using
    style underscore magic.

    Parameters
    ----------
    objects: Magpylib objects (sources, collections, sensors)
        Objects to be displayed.

    backend: string, default=`None`
        Define plotting backend. Must be one of `['auto', 'matplotlib', 'plotly', 'pyvista']`.
        If not set, parameter will default to `magpylib.defaults.display.backend` which is
        `'auto'` by installation default. With `'auto'`, the backend defaults to `'plotly'` if
        plotly is installed and the function is called in an `IPython` environment, otherwise
        defaults to `'matplotlib'` which comes installed with magpylib. If the `canvas` is set,
        the backend defaults to the one corresponding to the canvas object (see canvas parameter).

    canvas: matplotlib.pyplot `AxesSubplot` or plotly `Figure` object, default=`None`
        Display graphical output on a given canvas:
        - with matplotlib: `matplotlib.axes.Axes` with `projection=3d.
        - with plotly: `plotly.graph_objects.Figure` or `plotly.graph_objects.FigureWidget`.
        - with pyvista: `pyvista.Plotter`.
        By default a new canvas is created and immediately displayed.

    animation: bool or float, default=`False`
        If `True` and at least one object has a path, the paths are rendered.
        If input is a positive float, the animation time is set to the given value.
        This feature is only available for the plotly backend.

    zoom: float, default=`0`
        Adjust plot zoom-level. When zoom=0 3D-figure boundaries are tight.

    markers: array_like, shape (n,3), default=`None`
        Display position markers in the global coordinate system.

    return_fig: bool, default=False
        If True, the function call returns the figure object.

        - with matplotlib: `matplotlib.figure.Figure`.
        - with plotly: `plotly.graph_objects.Figure` or `plotly.graph_objects.FigureWidget`.
        - with pyvista: `pyvista.Plotter`.

    canvas_update: bool, default="auto".
        When no canvas is provided, Magpylib creates one and sets the layout to internally defined
        settings (e.g. camera angle, aspect ratio). If a canvas is provided, no changes to the
        layout are made. One can however explicitly force a behavior by setting `canvas_update`
        to True or False.

    row: int or None,
        If provided specifies the row in which the objects will be displayed.

    col: int or None,
        If provided specifies the column in which the objects will be displayed.

    output: tuple or string, default="model3d"
        Can be a string or a tuple of strings specifying the plot output type. By default
        `output='model3d'` displays the 3D representations of the objects. If output is a tuple of
        strings it must be a combination of 'B', 'H', 'M' or 'J' and 'x', 'y' and/or 'z'. When
        having multiple coordinates, the field value is the combined vector length
        (e.g. `('Bx', 'Hxy', 'Byz')`) 'Bxy' is equivalent to sqrt(|Bx|^2 + |By|^2). A 2D line plot
        is then represented accordingly if the objects contain at least one source and one sensor.

    sumup: bool, default=True
        If True, sums the field values of the sources. Applies only if `output` is not `'model3d'`.

    pixel_agg: bool, default="mean"
        Reference to a compatible numpy aggregator function like `'min'` or `'mean'`,
        which is applied to observer output values, e.g. mean of all sensor pixel outputs.
        Applies only if `output` is not `'model3d'`.

    style: dict
        Object style inputs must be in dictionary form, e.g. `{'color':'red'}` or
        using style underscore magic, e.g. `style_color='red'`. Applies to all objects matching the
        given style properties.

    Returns
    -------
    `None` or figure object

    Examples
    --------

    Display multiple objects, object paths, markers in 3D using Matplotlib or Plotly:

    >>> import magpylib as magpy
    >>> src = magpy.magnet.Sphere(polarization=(0,0,1), diameter=1)
    >>> src.move([(0.1*x,0,0) for x in range(50)])
    Sphere...
    >>> src.rotate_from_angax(angle=[*range(0,400,10)], axis='z', anchor=0, start=11)
    Sphere...
    >>> ts = [-.4,0,.4]
    >>> sens = magpy.Sensor(position=(0,0,2), pixel=[(x,y,0) for x in ts for y in ts])
    >>> magpy.show(src, sens) # doctest: +SKIP
    >>> magpy.show(src, sens, backend='plotly') # doctest: +SKIP
    >>> # graphic output

    Display output on your own canvas (here a Matplotlib 3d-axes):

    >>> import matplotlib.pyplot as plt
    >>> import magpylib as magpy
    >>> my_axis = plt.axes(projection='3d')
    >>> magnet = magpy.magnet.Cuboid(polarization=(1,1,1), dimension=(1,2,3))
    >>> sens = magpy.Sensor(position=(0,0,3))
    >>> magpy.show(magnet, sens, canvas=my_axis, zoom=1)
    >>> plt.show() # doctest: +SKIP
    >>> # graphic output

    Use sophisticated figure styling options accessible from defaults, as individual object styles
    or as global style arguments in display.

    >>> import magpylib as magpy
    >>> src1 = magpy.magnet.Sphere(position=[(0,0,0), (0,0,3)], diameter=1, polarization=(1,1,1))
    >>> src2 = magpy.magnet.Sphere(
    ...     position=[(1,0,0), (1,0,3)],
    ...     diameter=1,
    ...     polarization=(1,1,1),
    ...     style_path_show=False
    ... )
    >>> magpy.defaults.display.style.magnet.magnetization.size = 2
    >>> src1.style.magnetization.size = 1
    >>> magpy.show(src1, src2, style_color='r') # doctest: +SKIP
    >>> # graphic output

    Use a context manager to jointly animate 3d and 2d subplots

    >>> import magpylib as magpy
    >>> import numpy as np
    >>> import plotly.graph_objects as go
    >>> path_len = 40
    >>> sensor = magpy.Sensor()
    >>> cyl1 = magpy.magnet.Cylinder(
    ...    polarization=(.1, 0, 0),
    ...    dimension=(1, 2),
    ...    position=(4, 0, 0),
    ...    style_label="Cylinder1",
    ... )
    >>> sensor.move(np.linspace((0, 0, -3), (0, 0, 3), path_len), start=0)
    Sensor(id=...)
    >>> cyl1.rotate_from_angax(angle=np.linspace(0, 300, path_len), start=0, axis="z", anchor=0)
    Cylinder(id=...)
    >>> cyl2 = cyl1.copy().move((0, 0, 5))
    >>> fig = go.Figure()
    >>> with magpy.show_context(cyl1, cyl2, sensor, canvas=fig, backend="plotly", animation=True):
    ...    magpy.show(col=1, output="model3d")
    ...    magpy.show(col=2, output="Bxy", sumup=True)
    ...    magpy.show(col=3, output="Bz", sumup=False)
    >>> fig.show() # doctest: +SKIP
    >>> # graphic output
    """
    kwargs.update(
        {
            k: v
            for k, v in locals().items()
            if v is not _DefaultValue and k not in ("objects", "kwargs")
        }
    )
    if ctx.isrunning:
        rco = {k: v for k, v in kwargs.items() if k in DEFAULT_ROW_COL_PARAMS}
        ctx.kwargs.update(
            {k: v for k, v in kwargs.items() if k not in DEFAULT_ROW_COL_PARAMS}
        )
        ctx_objects = tuple({**o, **rco} for o in ctx.objects_from_ctx)
        objects, *_ = process_show_input_objs(ctx_objects + objects, **rco)
        ctx.objects += tuple(objects)
        return None
    return _show(*objects, **kwargs)


@contextmanager
def show_context(
    *objects,
    # pylint: disable=unused-argument
    backend=_DefaultValue,
    canvas=_DefaultValue,
    animation=_DefaultValue,
    zoom=_DefaultValue,
    markers=_DefaultValue,
    return_fig=_DefaultValue,
    canvas_update=_DefaultValue,
    row=_DefaultValue,
    col=_DefaultValue,
    output=_DefaultValue,
    sumup=_DefaultValue,
    pixel_agg=_DefaultValue,
    style=_DefaultValue,
    **kwargs,
):
    """Context manager to temporarily set display settings in the `with` statement context.

    You need to invoke as ``show_context(pattern1=value1, pattern2=value2)``.

    See the `magpylib.show` docstrings for the parameter definitions.
    """
    # pylint: disable=protected-access
    kwargs.update(
        {
            k: v
            for k, v in locals().items()
            if v is not _DefaultValue and k not in ("objects", "kwargs")
        }
    )
    try:
        ctx.isrunning = True
        rco = {k: v for k, v in kwargs.items() if k in DEFAULT_ROW_COL_PARAMS}
        objects, *_ = process_show_input_objs(objects, **rco)
        ctx.objects_from_ctx += tuple(objects)
        ctx.kwargs.update(
            {k: v for k, v in kwargs.items() if k not in DEFAULT_ROW_COL_PARAMS}
        )
        yield ctx
        ctx.show_return_value = _show(*ctx.objects, **ctx.kwargs)
    finally:
        ctx.reset(reset_show_return_value=False)


class DisplayContext:
    """Display context class"""

    show = staticmethod(show)

    def __init__(self, isrunning=False):
        self.isrunning = isrunning
        self.objects = ()
        self.objects_from_ctx = ()
        self.kwargs = {}
        self.show_return_value = None

    def reset(self, reset_show_return_value=True):
        """Reset display context"""
        self.isrunning = False
        self.objects = ()
        self.objects_from_ctx = ()
        self.kwargs = {}
        if reset_show_return_value:
            self.show_return_value = None


ctx = DisplayContext()


RegisteredBackend(
    name="matplotlib",
    show_func=get_show_func("matplotlib"),
    supports_animation=True,
    supports_subplots=True,
    supports_colorgradient=False,
    supports_animation_output=False,
)


RegisteredBackend(
    name="plotly",
    show_func=get_show_func("plotly"),
    supports_animation=True,
    supports_subplots=True,
    supports_colorgradient=True,
    supports_animation_output=False,
)

RegisteredBackend(
    name="pyvista",
    show_func=get_show_func("pyvista"),
    supports_animation=True,
    supports_subplots=True,
    supports_colorgradient=True,
    supports_animation_output=True,
)
