""" input checks code"""

# pylint: disable=import-outside-toplevel
# pylint: disable=cyclic-import
# pylint: disable=too-many-positional-arguments

import inspect
import numbers

import numpy as np
from scipy.spatial.transform import Rotation

from magpylib import _src
from magpylib._src.defaults.defaults_classes import default_settings
from magpylib._src.defaults.defaults_utility import SUPPORTED_PLOTTING_BACKENDS
from magpylib._src.exceptions import MagpylibBadUserInput
from magpylib._src.exceptions import MagpylibMissingInput
from magpylib._src.utility import format_obj_input
from magpylib._src.utility import wrong_obj_msg

# pylint: disable=no-member

#################################################################
#################################################################
# FUNDAMENTAL CHECKS


def all_same(lst: list) -> bool:
    """test if all list entries are the same"""
    return lst[1:] == lst[:-1]


def check_array_like(inp, msg: str):
    """test if inp is array_like: type list, tuple or ndarray
    inp: test object
    msg: str, error msg
    """
    if not isinstance(inp, (list, tuple, np.ndarray)):
        raise MagpylibBadUserInput(msg)


def make_float_array(inp, msg: str):
    """transform inp to array with dtype=float, throw error with bad input
    inp: test object
    msg: str, error msg
    """
    try:
        inp_array = np.array(inp, dtype=float)
    except Exception as err:
        raise MagpylibBadUserInput(msg + f"{err}") from err
    return inp_array


def check_array_shape(inp: np.ndarray, dims: tuple, shape_m1: int, length=None, msg=""):
    """check if inp shape is allowed
    inp: test object
    dims: list, list of allowed dims
    shape_m1: shape of lowest level, if 'any' allow any shape
    msg: str, error msg
    """
    if inp.ndim in dims:
        if length is None:
            if inp.shape[-1] == shape_m1:
                return None
            if shape_m1 == "any":
                return None
        elif len(inp) == length:
            return None
    raise MagpylibBadUserInput(msg)


def check_input_zoom(inp):
    """check show zoom input"""
    if not (isinstance(inp, numbers.Number) and inp >= 0):
        raise MagpylibBadUserInput(
            "Input parameter `zoom` must be a positive number or zero.\n"
            f"Instead received {inp!r}."
        )


def check_input_animation(inp):
    """check show animation input"""
    ERR_MSG = (
        "Input parameter `animation` must be boolean or a positive number.\n"
        f"Instead received {inp!r}."
    )
    if not isinstance(inp, numbers.Number):
        raise MagpylibBadUserInput(ERR_MSG)
    if inp < 0:
        raise MagpylibBadUserInput(ERR_MSG)


#################################################################
#################################################################
# SIMPLE CHECKS


def check_start_type(inp):
    """start input must be int or str"""
    if not (
        isinstance(inp, (int, np.integer)) or (isinstance(inp, str) and inp == "auto")
    ):
        raise MagpylibBadUserInput(
            f"Input parameter `start` must be integer value or 'auto'.\n"
            f"Instead received {inp!r}."
        )


def check_degree_type(inp):
    """degrees input must be bool"""
    if not isinstance(inp, bool):
        raise MagpylibBadUserInput(
            "Input parameter `degrees` must be boolean (`True` or `False`).\n"
            f"Instead received {inp!r}."
        )


def check_field_input(inp):
    """check field input"""
    allowed = tuple("BHMJ")
    if not (isinstance(inp, str) and inp in allowed):
        raise MagpylibBadUserInput(
            f"`field` input can only be one of {allowed}.\n"
            f"Instead received {inp!r}."
        )


def validate_field_func(val):
    """test if field function for custom source is valid
    - needs to be a callable
    - input and output shape must match
    """
    if val is None:
        return None

    if not callable(val):
        raise MagpylibBadUserInput(
            "Input parameter `field_func` must be a callable.\n"
            f"Instead received {type(val).__name__!r}."
        )

    fn_args = inspect.getfullargspec(val).args
    if fn_args[:2] != ["field", "observers"]:
        raise MagpylibBadUserInput(
            "Input parameter `field_func` must have two positional args"
            " called 'field' and 'observers'.\n"
            f"Instead received a callable where the first two args are: {fn_args[:2]!r}"
        )

    for field in ["B", "H"]:
        out = val(field, np.array([[1, 2, 3], [4, 5, 6]]))
        if out is not None:
            if not isinstance(out, np.ndarray):
                raise MagpylibBadUserInput(
                    "Input parameter `field_func` must be a callable that returns B- and H-field"
                    " as numpy ndarray.\n"
                    f"Instead it returns type {type(out)!r} for {field}-field."
                )
            if out.shape != (2, 3):
                raise MagpylibBadUserInput(
                    "Input parameter `field_func` must be a callable that returns B- and H-field"
                    " as numpy ndarray with shape (n,3), when `observers` input is shape (n,3).\n"
                    f"Instead it returns shape {out.shape} for {field}-field for input shape "
                    "(2,3)"
                )

    return None


#################################################################
#################################################################
# CHECK - FORMAT


def check_format_input_orientation(inp, init_format=False):
    """checks orientation input returns in formatted form
    - inp must be None or Rotation object
    - transform None to unit rotation as quat (0,0,0,1)
    if init_format: (for move method)
        return inp and inpQ
    else: (for init and setter)
        return inpQ in shape (-1,4)

    This function is used for setter and init only -> shape (1,4) and (4,) input
    creates same behavior.
    """
    # check type
    if not isinstance(inp, (Rotation, type(None))):
        raise MagpylibBadUserInput(
            f"Input parameter `orientation` must be `None` or scipy `Rotation` object.\n"
            f"Instead received type {type(inp)!r}."
        )
    # handle None input and compute inpQ
    if inp is None:
        inpQ = np.array((0, 0, 0, 1))
        inp = Rotation.from_quat(inpQ)
    else:
        inpQ = inp.as_quat()
    # return
    if init_format:
        return np.reshape(inpQ, (-1, 4))
    return inp, inpQ


def check_format_input_anchor(inp):
    """checks rotate anchor input and return in formatted form
    - input must be array_like or None or 0
    """
    if isinstance(inp, numbers.Number) and inp == 0:
        return np.array((0.0, 0.0, 0.0))

    return check_format_input_vector(
        inp,
        dims=(1, 2),
        shape_m1=3,
        sig_name="anchor",
        sig_type="`None` or `0` or array_like (list, tuple, ndarray) with shape (3,)",
        allow_None=True,
    )


def check_format_input_axis(inp):
    """check rotate_from_angax axis input and return in formatted form
    - input must be array_like or str
    - if string 'x'->(1,0,0), 'y'->(0,1,0), 'z'->(0,0,1)
    - convert inp to ndarray with dtype float
    - inp shape must be (3,)
    - axis must not be (0,0,0)
    - return as ndarray shape (3,)
    """
    if isinstance(inp, str):
        if inp == "x":
            return np.array((1, 0, 0))
        if inp == "y":
            return np.array((0, 1, 0))
        if inp == "z":
            return np.array((0, 0, 1))
        raise MagpylibBadUserInput(
            "Input parameter `axis` must be array_like shape (3,) or one of ['x', 'y', 'z'].\n"
            f"Instead received string {inp!r}.\n"
        )

    inp = check_format_input_vector(
        inp,
        dims=(1,),
        shape_m1=3,
        sig_name="axis",
        sig_type="array_like (list, tuple, ndarray) with shape (3,) or one of ['x', 'y', 'z']",
    )

    if np.all(inp == 0):
        raise MagpylibBadUserInput("Input parameter `axis` must not be (0,0,0).\n")
    return inp


def check_format_input_angle(inp):
    """check rotate_from_angax angle input and return in formatted form
    - must be scalar (int/float) or array_like
    - if scalar
        - return float
    - if array_like
        - convert inp to ndarray with dtype float
        - inp shape must be (n,)
        - return as ndarray
    """
    if isinstance(inp, numbers.Number):
        return float(inp)

    return check_format_input_vector(
        inp,
        dims=(1,),
        shape_m1="any",
        sig_name="angle",
        sig_type="int, float or array_like (list, tuple, ndarray) with shape (n,)",
    )


def check_format_input_scalar(
    inp, sig_name, sig_type, allow_None=False, forbid_negative=False
):
    """check scalar input and return in formatted form
    - must be scalar or None (if allowed)
    - must be float compatible
    - transform into float
    """
    if allow_None:
        if inp is None:
            return None

    ERR_MSG = (
        f"Input parameter `{sig_name}` must be {sig_type}.\n"
        f"Instead received {inp!r}."
    )

    if not isinstance(inp, numbers.Number):
        raise MagpylibBadUserInput(ERR_MSG)

    inp = float(inp)

    if forbid_negative:
        if inp < 0:
            raise MagpylibBadUserInput(ERR_MSG)
    return inp


def check_format_input_vector(
    inp,
    dims,
    shape_m1,
    sig_name,
    sig_type,
    length=None,
    reshape=False,
    allow_None=False,
    forbid_negative0=False,
):
    """checks vector input and returns in formatted form
    - inp must be array_like
    - convert inp to ndarray with dtype float
    - inp shape must be given by dims and shape_m1
    - print error msg with signature arguments
    - if reshape=True: returns shape (n,3) - required for position init and setter
    - if allow_None: return None
    - if extend_dim_to2: add a dimension if input is only (1,2,3) - required for sensor pixel
    """
    if allow_None:
        if inp is None:
            return None

    check_array_like(
        inp,
        f"Input parameter `{sig_name}` must be {sig_type}.\n"
        f"Instead received type {type(inp)!r}.",
    )
    inp = make_float_array(
        inp,
        f"Input parameter `{sig_name}` must contain only float compatible entries.\n",
    )
    check_array_shape(
        inp,
        dims=dims,
        shape_m1=shape_m1,
        length=length,
        msg=(
            f"Input parameter `{sig_name}` must be {sig_type}.\n"
            f"Instead received array_like with shape {inp.shape}."
        ),
    )
    if isinstance(reshape, tuple):
        return np.reshape(inp, reshape)

    if forbid_negative0:
        if np.any(inp <= 0):
            raise MagpylibBadUserInput(
                f"Input parameter `{sig_name}` cannot have values <= 0."
            )
    return inp


def check_format_input_vector2(
    inp,
    shape,
    param_name,
):
    """checks vector input and returns in formatted form
    - inp must be array_like
    - convert inp to ndarray with dtype float
    - make sure that inp.ndim = target_ndim, None dimensions are ignored
    """
    check_array_like(
        inp,
        f"Input parameter `{param_name}` must be array_like.\n"
        f"Instead received type {type(inp)!r}.",
    )
    inp = make_float_array(
        inp,
        f"Input parameter `{param_name}` must contain only float compatible entries.\n",
    )
    for d1, d2 in zip(inp.shape, shape):
        if d2 is not None:
            if d1 != d2:
                raise ValueError(f"Input parameter `{param_name}` has bad shape.")
    return inp


def check_format_input_vertices(inp):
    """checks vertices input and returns in formatted form
    - vector check with dim = (n,3) but n must be >=2
    """
    inp = check_format_input_vector(
        inp,
        dims=(2,),
        shape_m1=3,
        sig_name="vertices",
        sig_type="`None` or array_like (list, tuple, ndarray) with shape (n,3)",
        allow_None=True,
    )

    if inp is not None:
        if inp.shape[0] < 2:
            raise MagpylibBadUserInput(
                "Input parameter `vertices` must have more than one vertex."
            )
    return inp


def check_format_input_cylinder_segment(inp):
    """checks vertices input and returns in formatted form
    - vector check with dim = (5) or none
    - check if d1<d2, phi1<phi2
    - check if phi2-phi1 > 360
    - return error msg
    """
    inp = check_format_input_vector(
        inp,
        dims=(1,),
        shape_m1=5,
        sig_name="CylinderSegment.dimension",
        sig_type=(
            "array_like of the form (r1, r2, h, phi1, phi2) with r1<r2,"
            "phi1<phi2 and phi2-phi1<=360"
        ),
        allow_None=True,
    )

    if inp is None:
        return None

    r1, r2, h, phi1, phi2 = inp
    case2 = r1 > r2
    case3 = phi1 > phi2
    case4 = (phi2 - phi1) > 360
    case5 = (r1 < 0) | (r2 <= 0) | (h <= 0)
    if case2 | case3 | case4 | case5:
        raise MagpylibBadUserInput(
            f"Input parameter `CylinderSegment.dimension` must be array_like of the form"
            f" (r1, r2, h, phi1, phi2) with 0<=r1<r2, h>0, phi1<phi2 and phi2-phi1<=360,"
            f"\nInstead received {inp!r}."
        )
    return inp


def check_format_input_backend(inp):
    """checks show-backend input and returns Non if bad input value"""
    backends = [*SUPPORTED_PLOTTING_BACKENDS, "auto"]
    if inp is None:
        inp = default_settings.display.backend
    if inp in backends:
        return inp
    raise MagpylibBadUserInput(
        f"Input parameter `backend` must be one of `{backends+[None]}`."
        f"\nInstead received {inp!r}."
    )


def check_format_input_observers(inp, pixel_agg=None):
    """
    checks observers input and returns a list of sensor objects
    """
    # pylint: disable=raise-missing-from
    from magpylib._src.obj_classes.class_Collection import Collection
    from magpylib._src.obj_classes.class_Sensor import Sensor

    # make bare Sensor, bare Collection into a list
    if isinstance(inp, (Collection, Sensor)):
        inp = (inp,)

    # note: bare pixel is automatically made into a list by Sensor

    # any good input must now be list/tuple/array
    if not isinstance(inp, (list, tuple, np.ndarray)):
        raise MagpylibBadUserInput(wrong_obj_msg(inp, allow="observers"))

    # empty list
    if len(inp) == 0:
        raise MagpylibBadUserInput(wrong_obj_msg(inp, allow="observers"))

    # now inp can still be [pos_vec, sens, coll] or just a pos_vec

    try:  # try if input is just a pos_vec
        inp = np.array(inp, dtype=float)
        pix_shapes = [(1, 3) if inp.shape == (3,) else inp.shape]
        return [_src.obj_classes.class_Sensor.Sensor(pixel=inp)], pix_shapes
    except (TypeError, ValueError):  # if not, it must be [pos_vec, sens, coll]
        sensors = []
        for obj in inp:
            if isinstance(obj, Sensor):
                sensors.append(obj)
            elif isinstance(obj, Collection):
                child_sensors = format_obj_input(obj, allow="sensors")
                if not child_sensors:
                    raise MagpylibBadUserInput(wrong_obj_msg(obj, allow="observers"))
                sensors.extend(child_sensors)
            else:  # if its not a Sensor or a Collection it can only be a pos_vec
                try:
                    obj = np.array(obj, dtype=float)
                    sensors.append(_src.obj_classes.class_Sensor.Sensor(pixel=obj))
                except Exception:  # or some unwanted crap
                    raise MagpylibBadUserInput(wrong_obj_msg(obj, allow="observers"))

        # all pixel shapes must be the same
        pix_shapes = [
            (1, 3) if (s.pixel is None or s.pixel.shape == (3,)) else s.pixel.shape
            for s in sensors
        ]
        if pixel_agg is None and not all_same(pix_shapes):
            raise MagpylibBadUserInput(
                "Different observer input shape detected."
                " All observer inputs must be of similar shape, unless a"
                " numpy pixel aggregator is provided, e.g. `pixel_agg='mean'`!"
            )
        return sensors, pix_shapes


def check_format_input_obj(
    inp,
    allow: str,
    recursive=True,
    typechecks=False,
) -> list:
    """
    Returns a flat list of all wanted objects in input.
    Parameters
    ----------
    input: can be
        - objects
    allow: str
        Specify which object types are wanted, separate by +,
        e.g. sensors+collections+sources
    recursive: bool
        Flatten Collection objects
    """
    from magpylib._src.obj_classes.class_BaseExcitations import BaseSource
    from magpylib._src.obj_classes.class_Collection import Collection
    from magpylib._src.obj_classes.class_Sensor import Sensor

    # select wanted
    wanted_types = ()
    if "sources" in allow.split("+"):
        wanted_types += (BaseSource,)
    if "sensors" in allow.split("+"):
        wanted_types += (Sensor,)
    if "collections" in allow.split("+"):
        wanted_types += (Collection,)

    obj_list = []
    for obj in inp:
        # add to list if wanted type
        if isinstance(obj, wanted_types):
            obj_list.append(obj)

        # recursion
        if isinstance(obj, Collection) and recursive:
            obj_list += check_format_input_obj(
                obj,
                allow=allow,
                recursive=recursive,
                typechecks=typechecks,
            )

        # typechecks
        # pylint disable possibly-used-before-assignment
        if typechecks and not isinstance(obj, (BaseSource, Sensor, Collection)):
            raise MagpylibBadUserInput(
                f"Input objects must be {allow} or a flat list thereof.\n"
                f"Instead received {type(obj)!r}."
            )

    return obj_list


############################################################################################
############################################################################################
# SHOW AND GETB CHECKS


def check_dimensions(sources):
    """check if all sources have dimension (or similar) initialized"""
    for src in sources:
        for arg in ("dimension", "diameter", "vertices"):
            if hasattr(src, arg):
                if getattr(src, arg) is None:
                    raise MagpylibMissingInput(
                        f"Parameter `{arg}` of {src} must be set."
                    )
                break


def check_excitations(sources):
    """check if all sources have excitation initialized"""
    for src in sources:
        for arg in ("polarization", "current", "moment"):
            if hasattr(src, arg):
                if getattr(src, arg) is None:
                    raise MagpylibMissingInput(
                        f"Parameter `{arg}` of {src} must be set."
                    )
                break


def check_format_pixel_agg(pixel_agg):
    """
    check if pixel_agg input is acceptable
    return the respective numpy function
    """

    PIXEL_AGG_ERR_MSG = (
        "Input `pixel_agg` must be a reference to a numpy callable that reduces"
        " an array shape like 'mean', 'std', 'median', 'min', ..."
        f"\nInstead received {pixel_agg!r}."
    )

    if pixel_agg is None:
        return None

    # test numpy reference
    try:
        pixel_agg_func = getattr(np, pixel_agg)
    except AttributeError as err:
        raise AttributeError(PIXEL_AGG_ERR_MSG) from err

    # test pixel agg function reduce
    x = np.array([[[(1, 2, 3)] * 2] * 3] * 4)
    if not isinstance(pixel_agg_func(x), numbers.Number):
        raise AttributeError(PIXEL_AGG_ERR_MSG)

    return pixel_agg_func


def check_getBH_output_type(output):
    """check if getBH output is acceptable"""
    acceptable = ("ndarray", "dataframe")
    if output not in acceptable:
        raise ValueError(
            f"The `output` argument must be one of {acceptable}."
            f"\nInstead received {output!r}."
        )
    if output == "dataframe":
        try:
            # pylint: disable=import-outside-toplevel
            # pylint: disable=unused-import
            import pandas
        except ImportError as missing_module:  # pragma: no cover
            raise ModuleNotFoundError(
                "In order to use the `dataframe` output type, you need to install pandas "
                "via pip or conda, "
                "see https://pandas.pydata.org/docs/getting_started/install.html"
            ) from missing_module

    return output


def check_input_canvas_update(canvas_update, canvas):
    """chekc if canvas_update is acceptable also depending on canvas input"""
    acceptable = (True, False, "auto", None)
    if canvas_update not in acceptable:
        raise ValueError(
            f"The `canvas_update` must be one of {acceptable}"
            f"\nInstead received {canvas_update!r}."
        )
    return canvas is None if canvas_update in (None, "auto") else canvas_update
