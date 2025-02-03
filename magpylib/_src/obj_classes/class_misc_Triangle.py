# pylint: disable=too-many-positional-arguments

"""Magnet Triangle class"""

import numpy as np

from magpylib._src.display.traces_core import make_Triangle
from magpylib._src.fields.field_BH_triangle import BHJM_triangle
from magpylib._src.input_checks import check_format_input_vector
from magpylib._src.obj_classes.class_BaseExcitations import BaseMagnet
from magpylib._src.style import TriangleStyle


class Triangle(BaseMagnet):
    """Triangular surface with homogeneous magnetic surface charge.

    Can be used as `sources` input for magnetic field computation.

    When `position=(0,0,0)` and `orientation=None` the local object coordinates of the
    Triangle vertices coincide with the global coordinate system. The geometric
    center of the Triangle is determined by its vertices.

    SI units are used for all inputs and outputs.

    Parameters
    ----------
    position: array_like, shape (3,) or (m,3)
        Object position(s) in the global coordinates in units of m. For m>1, the
        `position` and `orientation` attributes together represent an object path.

    orientation: scipy `Rotation` object with length 1 or m, default=`None`
        Object orientation(s) in the global coordinates. `None` corresponds to
        a unit-rotation. For m>1, the `position` and `orientation` attributes
        together represent an object path.

    vertices: ndarray, shape (3,3)
        Triple of vertices in the local object coordinates.

    polarization: array_like, shape (3,), default=`None`
        Magnetic polarization vector J = mu0*M in units of T,
        given in the local object coordinates (rotates with object).The homogeneous surface
        charge of the Triangle is given by the projection of the polarization on the
        Triangle normal vector (right-hand-rule).

    magnetization: array_like, shape (3,), default=`None`
        Magnetization vector M = J/mu0 in units of A/m,
        given in the local object coordinates (rotates with object).The homogeneous surface
        charge of the Triangle is given by the projection of the magnetization on the
        Triangle normal vector (right-hand-rule).

    parent: `Collection` object or `None`
        The object is a child of it's parent collection.

    style: dict
        Object style inputs must be in dictionary form, e.g. `{'color':'red'}` or
        using style underscore magic, e.g. `style_color='red'`.

    Attributes
    ----------
    barycenter: array_like, shape (3,)
        Read only property that returns the geometric barycenter (=center of mass)
        of the object.

    Returns
    -------
    magnet source: `Triangle` object

    Examples
    --------
    `Triangle` objects are magnetic field sources. Below we compute the H-field in A/m of a
    Triangle object with polarization (0.01,0.02,0.03) in units of T, dimensions defined
    through the vertices (0,0,0), (0.01,0,0) and (0,0.01,0) in units of m at the
    observer position (0.01,0.01,0.01) given in units of m:

    >>> import numpy as np
    >>> import magpylib as magpy
    >>> verts = [(0,0,0), (.01,0,0), (0,.01,0)]
    >>> src = magpy.misc.Triangle(polarization=(.1,.2,.3), vertices=verts)
    >>> H = src.getH((.1,.1,.1))
    >>> with np.printoptions(precision=3):
    ...     print(H)
    [18.889 18.889 19.546]
    """

    _field_func = staticmethod(BHJM_triangle)
    _field_func_kwargs_ndim = {"polarization": 2, "vertices": 2}
    get_trace = make_Triangle
    _style_class = TriangleStyle

    def __init__(
        self,
        position=(0, 0, 0),
        orientation=None,
        vertices=None,
        polarization=None,
        magnetization=None,
        style=None,
        **kwargs,
    ):
        self.vertices = vertices

        # init inheritance
        super().__init__(
            position, orientation, magnetization, polarization, style, **kwargs
        )

    # property getters and setters
    @property
    def vertices(self):
        """Object faces"""
        return self._vertices

    @vertices.setter
    def vertices(self, val):
        """Set face vertices (a,b,c), shape (3,3), meter."""
        self._vertices = check_format_input_vector(
            val,
            dims=(2,),
            shape_m1=3,
            sig_name="Triangle.vertices",
            sig_type="array_like (list, tuple, ndarray) of shape (3,3)",
            allow_None=True,
        )

    @property
    def _barycenter(self):
        """Object barycenter."""
        return self._get_barycenter(self._position, self._orientation, self._vertices)

    @property
    def barycenter(self):
        """Object barycenter."""
        return np.squeeze(self._barycenter)

    @staticmethod
    def _get_barycenter(position, orientation, vertices):
        """Returns the barycenter of the Triangle object."""
        centroid = (
            np.array([0.0, 0.0, 0.0]) if vertices is None else np.mean(vertices, axis=0)
        )
        barycenter = orientation.apply(centroid) + position
        return barycenter

    @property
    def _default_style_description(self):
        """Default style description text"""
        if self.vertices is None:
            return "no vertices"
        return ""
