"""Custom class code"""

from magpylib._src.obj_classes.class_BaseExcitations import BaseSource


class CustomSource(BaseSource):
    """User-defined custom source.

    Can be used as `sources` input for magnetic field computation.

    When `position=(0,0,0)` and `orientation=None` local object coordinates
    coincide with the global coordinate system.

    SI units are used for all inputs and outputs.

    Parameters
    ----------

    position: array_like, shape (3,) or (m,3), default=`(0,0,0)`
        Object position(s) in the global coordinates in units of m. For m>1, the
        `position` and `orientation` attributes together represent an object path.

    orientation: scipy `Rotation` object with length 1 or m, default=`None`
        Object orientation(s) in the global coordinates. `None` corresponds to
        a unit-rotation. For m>1, the `position` and `orientation` attributes
        together represent an object path.

    field_func: callable, default=`None`
        The function for B- and H-field computation must have the two positional arguments
        `field` and `observers`. With `field='B'` or `field='H'` the B- or H-field in units
        of T or A/m must be returned respectively. The `observers` argument must
        accept numpy ndarray inputs of shape (n,3), in which case the returned fields must
        be numpy ndarrays of shape (n,3) themselves.

    parent: `Collection` object or `None`
        The object is a child of it's parent collection.

    style: dict
        Object style inputs must be in dictionary form, e.g. `{'color':'red'}` or
        using style underscore magic, e.g. `style_color='red'`.

    Returns
    -------
    source: `CustomSource` object

    Examples
    --------
    With version 4 `CustomSource` objects enable users to define their own source
    objects, and to embedded them in the Magpylib object oriented interface. In this example
    we create a source that generates a constant field and evaluate the field at observer
    position (0.01,0.01,0.01) given in meters:

    >>> import numpy as np
    >>> import magpylib as magpy
    >>> def funcBH(field, observers):
    ...     return np.array([(.01 if field=='B' else .08,0,0)]*len(observers))
    >>> src = magpy.misc.CustomSource(field_func=funcBH)
    >>> H = src.getH((.01,.01,.01))
    >>> print(H)
    [0.08 0.   0.  ]
    """

    _editable_field_func = True

    def __init__(
        self,
        position=(0, 0, 0),
        orientation=None,
        field_func=None,
        style=None,
        **kwargs,
    ):
        # init inheritance
        super().__init__(position, orientation, field_func, style, **kwargs)
