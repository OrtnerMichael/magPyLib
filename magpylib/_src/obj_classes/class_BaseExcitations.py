"""BaseHomMag class code"""
# pylint: disable=cyclic-import
from magpylib._src.fields.field_wrap_BH import getBH_level2
from magpylib._src.input_checks import check_format_input_scalar
from magpylib._src.input_checks import check_format_input_vector
from magpylib._src.input_checks import validate_field_func
from magpylib._src.obj_classes.class_BaseDisplayRepr import BaseDisplayRepr
from magpylib._src.obj_classes.class_BaseGeo import BaseGeo
from magpylib._src.style import CurrentStyle
from magpylib._src.style import MagnetStyle
from magpylib._src.utility import format_star_input


class BaseSource(BaseGeo, BaseDisplayRepr):
    """Base class for all types of sources. Provides getB and getH methods for source objects
    and corresponding field function"""

    _field_func = None
    _field_func_kwargs_ndim = {}
    _editable_field_func = False

    def __init__(self, position, orientation, field_func=None, style=None, **kwargs):
        if field_func is not None:
            self.field_func = field_func
        BaseGeo.__init__(self, position, orientation, style=style, **kwargs)
        BaseDisplayRepr.__init__(self)

    @property
    def field_func(self):
        """
        The function for B- and H-field computation must have the two positional arguments
        `field` and `observers`. With `field='B'` or `field='H'` the B- or H-field in units
        of mT or kA/m must be returned respectively. The `observers` argument must
        accept numpy ndarray inputs of shape (n,3), in which case the returned fields must
        be numpy ndarrays of shape (n,3) themselves.
        """
        return self._field_func

    @field_func.setter
    def field_func(self, val):
        if self._editable_field_func:
            validate_field_func(val)
        else:
            raise AttributeError(
                "The `field_func` attribute should not be edited for original Magpylib sources."
            )
        self._field_func = val

    def getB(self, *observers, squeeze=True, pixel_agg=None, output="ndarray"):
        """Compute the B-field in units of mT generated by the source.

        Parameters
        ----------
        observers: array_like or (list of) `Sensor` objects
            Can be array_like positions of shape (n1, n2, ..., 3) where the field
            should be evaluated, a `Sensor` object with pixel shape (n1, n2, ..., 3) or a list
            of such sensor objects (must all have similar pixel shapes). All positions
            are given in units of mm.

        squeeze: bool, default=`True`
            If `True`, the output is squeezed, i.e. all axes of length 1 in the output (e.g.
            only a single source) are eliminated.

        pixel_agg: str, default=`None`
            Reference to a compatible numpy aggregator function like `'min'` or `'mean'`,
            which is applied to observer output values, e.g. mean of all sensor pixel outputs.
            With this option, observers input with different (pixel) shapes is allowed.

        output: str, default='ndarray'
            Output type, which must be one of `('ndarray', 'dataframe')`. By default a multi-
            dimensional array ('ndarray') is returned. If 'dataframe' is chosen, the function
            returns a 2D-table as a `pandas.DataFrame` object (the Pandas library must be
            installed).

        Returns
        -------
        B-field: ndarray, shape squeeze(m, k, n1, n2, ..., 3) or DataFrame
            B-field at each path position (m) for each sensor (k) and each sensor pixel
            position (n1,n2,...) in units of mT. Sensor pixel positions are equivalent
            to simple observer positions. Paths of objects that are shorter than m will be
            considered as static beyond their end.

        Examples
        --------
        Compute the B-field of a spherical magnet at three positions:

        >>> import magpylib as magpy
        >>> src = magpy.magnet.Sphere((0,0,1000), 1)
        >>> B = src.getB(((0,0,0), (1,0,0), (2,0,0)))
        >>> print(B)
        [[  0.           0.         666.66666667]
         [  0.           0.         -41.66666667]
         [  0.           0.          -5.20833333]]

        Compute the B-field at two sensors, each one with two pixels

        >>> sens1 = magpy.Sensor(position=(1,0,0), pixel=((0,0,.1), (0,0,-.1)))
        >>> sens2 = sens1.copy(position=(2,0,0))
        >>> B = src.getB(sens1, sens2)
        >>> print(B)
        [[[ 12.19288783   0.         -39.83010025]
          [-12.19288783   0.         -39.83010025]]
        <BLANKLINE>
         [[  0.77638847   0.          -5.15004352]
          [ -0.77638847   0.          -5.15004352]]]
        """
        observers = format_star_input(observers)
        return getBH_level2(
            self,
            observers,
            sumup=False,
            squeeze=squeeze,
            pixel_agg=pixel_agg,
            output=output,
            field="B",
        )

    def getH(self, *observers, squeeze=True, pixel_agg=None, output="ndarray"):
        """Compute the H-field in units of kA/m generated by the source.

        Parameters
        ----------
        observers: array_like or (list of) `Sensor` objects
            Can be array_like positions of shape (n1, n2, ..., 3) where the field
            should be evaluated, a `Sensor` object with pixel shape (n1, n2, ..., 3) or a list
            of such sensor objects (must all have similar pixel shapes). All positions
            are given in units of mm.

        squeeze: bool, default=`True`
            If `True`, the output is squeezed, i.e. all axes of length 1 in the output (e.g.
            only a single source) are eliminated.

        pixel_agg: str, default=`None`
            Reference to a compatible numpy aggregator function like `'min'` or `'mean'`,
            which is applied to observer output values, e.g. mean of all sensor pixel outputs.
            With this option, observers input with different (pixel) shapes is allowed.

        output: str, default='ndarray'
            Output type, which must be one of `('ndarray', 'dataframe')`. By default a multi-
            dimensional array ('ndarray') is returned. If 'dataframe' is chosen, the function
            returns a 2D-table as a `pandas.DataFrame` object (the Pandas library must be
            installed).

        Returns
        -------
        H-field: ndarray, shape squeeze(m, k, n1, n2, ..., 3) or DataFrame
            H-field at each path position (m) for each sensor (k) and each sensor pixel
            position (n1,n2,...) in units of kA/m. Sensor pixel positions are equivalent
            to simple observer positions. Paths of objects that are shorter than m will be
            considered as static beyond their end.

        Examples
        --------
        Compute the H-field of a spherical magnet at three positions:

        >>> import magpylib as magpy

        >>> src = magpy.magnet.Sphere((0,0,1000), 1)
        >>> H = src.getH(((0,0,0), (1,0,0), (2,0,0)))
        >>> print(H)
        [[   0.            0.         -265.25823849]
         [   0.            0.          -33.15727981]
         [   0.            0.           -4.14465998]]

        Compute the H-field at two sensors, each one with two pixels

        >>> sens1 = magpy.Sensor(position=(1,0,0), pixel=((0,0,.1), (0,0,-.1)))
        >>> sens2 = sens1.copy(position=(2,0,0))
        >>> H = src.getH(sens1, sens2)
        >>> print(H)
        [[[  9.70279185   0.         -31.69578669]
          [ -9.70279185   0.         -31.69578669]]
        <BLANKLINE>
         [[  0.61783031   0.          -4.09827441]
          [ -0.61783031   0.          -4.09827441]]]
        """
        observers = format_star_input(observers)
        return getBH_level2(
            self,
            observers,
            sumup=False,
            squeeze=squeeze,
            pixel_agg=pixel_agg,
            output=output,
            field="H",
        )


class BaseMagnet(BaseSource):
    """provides the magnetization attribute  for homogeneously magnetized magnets"""

    _style_class = MagnetStyle

    def __init__(self, position, orientation, magnetization, style, **kwargs):
        super().__init__(position, orientation, style=style, **kwargs)
        self.magnetization = magnetization

    @property
    def magnetization(self):
        """Object magnetization attribute getter and setter."""
        return self._magnetization

    @magnetization.setter
    def magnetization(self, mag):
        """Set magnetization vector, array_like, shape (3,), unit (mT)."""
        self._magnetization = check_format_input_vector(
            mag,
            dims=(1,),
            shape_m1=3,
            sig_name="magnetization",
            sig_type="array_like (list, tuple, ndarray) with shape (3,)",
            allow_None=True,
        )


class BaseCurrent(BaseSource):
    """provides scalar current attribute"""

    _style_class = CurrentStyle

    def __init__(self, position, orientation, current, style, **kwargs):
        super().__init__(position, orientation, style=style, **kwargs)
        self.current = current

    @property
    def current(self):
        """Object current attribute getter and setter."""
        return self._current

    @current.setter
    def current(self, current):
        """Set current value, scalar, unit (A)."""
        # input type and init check
        self._current = check_format_input_scalar(
            current,
            sig_name="current",
            sig_type="`None` or a number (int, float)",
            allow_None=True,
        )
