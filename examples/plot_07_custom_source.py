"""
=============
Custom Source
=============
"""

# %%
# The magpylib library provides a custom class which enables the user to define its own source with
# an arbitrary field function. The user field function must return a position-dependent value in
# the local coordinate system of the source. The custom source instance is then treated the same as
# any other built-in source and can be moved or rotated. Coordinate transformations are taken care
# of by the library. The field values in the global coordinate system can be obtained with ``getB``
# or ``getH`` as long as a respective field function has been provided.
#
# The custom source class can for example be used to manipulate data originating from a 3d-vector
# field from measured or exported FEM data. In this case, the field function must be an
# interpolation function of the data. In this example, the source data comes directly from the field
# calculation provided by magpylib itself, but the same procedure can be applied to aforementioned
# dataset types.


import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import RegularGridInterpolator
import magpylib as magpy
# %%
# Define interpolating function
# -----------------------------
def interpolate_field(data, method="linear", bounds_error=False, fill_value=np.nan):
    """ Creates a 3d-vector field interpolation of a rasterized data from a regular grid

    Parameters
    ----------
    data: numpy.ndarray or array-like
        array of shape (n,6). In order to be a regular grid, the first dimension n
        corresponds to the product of the unique values in x,y,z-directions.
        The second dimension must have the following ordering on the second axis:
            ``x, y, z, field_x, field_y, field_z``

    method : str, optional
        The method of interpolation to perform. Supported are "linear" and
        "nearest". This parameter will become the default for the object's
        ``__call__`` method. Default is "linear".

    bounds_error : bool, optional
        If True, when interpolated values are requested outside of the
        domain of the input data, a ValueError is raised.
        If False, then `fill_value` is used.

    fill_value : number, optional
        If provided, the value to use for points outside of the
        interpolation domain. If None, values outside
        the domain are extrapolated.

    Returns
    -------
        callable: interpolating function for field values
    """
    data = np.array(data)
    idx = np.lexsort((data[:, 2], data[:, 1], data[:, 0]))  # sort data by x,y,z
    x, y, z, *field_vec = data[idx].T
    X, Y, Z = np.unique(x), np.unique(y), np.unique(z)
    nx, ny, nz = len(X), len(Y), len(Z)
    kwargs = dict(bounds_error=bounds_error, fill_value=fill_value, method=method)
    field_interp = []
    for k, kn in zip((X, Y, Z), "xyz"):
        assert (
            np.unique(np.diff(k)).shape[0] == 1
        ), f"not a regular grid in {kn}-direction"
    for field in field_vec:
        rgi = RegularGridInterpolator((X, Y, Z), field.reshape(nx, ny, nz), **kwargs)
        field_interp.append(rgi)
    return lambda x: np.array([field(x) for field in field_interp]).T


# %%
# Create virtual measured data
# ----------------------------

# %%
# create a source
cube = magpy.magnet.Cuboid(
    magnetization=(0, 0, 1000), position=(-10, 0, 0), dimension=(10, 10, 10)
)
dim = [4, 4, 4]
Nelem = [2, 2, 2]
slices = [slice(-d / 2, d / 2, N * 1j) for d, N in zip(dim, Nelem)]
positions = np.mgrid[slices].reshape(len(slices), -1).T

# %%
# get data from a regular grid of positions
Bcube = cube.getB(positions)
# Bcube *= 1 + np.random.random_sample(B.shape)*0.01 # add 1% white noise
Bdata = np.hstack([positions, Bcube])

# %%
# Check field function values vs magpylib Cuboid field values
field_B_lambda = interpolate_field(Bdata)
print(Bcube)

# %%
print(field_B_lambda(positions))

# %%
# create custom source with interpolation field
interp_cube = magpy.misc.CustomSource(field_B_lambda=field_B_lambda)

# %%
# add a graphical representation to the custom object, in this case a transparent cube
mesh_data = {
    "type": "mesh3d",
    "i": np.array([7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7]),
    "j": np.array([0, 7, 1, 2, 6, 7, 1, 2, 5, 5, 2, 2]),
    "k": np.array([3, 4, 2, 3, 5, 6, 5, 5, 0, 1, 7, 6]),
    "x": np.array([-1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0]) * 0.5 * dim[0],
    "y": np.array([-1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0]) * 0.5 * dim[1],
    "z": np.array([-1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0]) * 0.5 * dim[2],
    "opacity": 0.2,
}
interp_cube.style.mesh3d = dict(data=mesh_data, show=True, replace=True)
interp_cube.style.name = 'Interpolated cuboid field'

# %%
# Testing the accuracy of the interpolation
# -----------------------------------------
# .. warning::
#    if ``getB`` gets called for positions outside the interpolated field boudaries, the
#    interpolation function will return ``np.nan``. Note that the edges of the domain are
#    susceptible to floating point errors when manipulating an object by rotation and calling
#    positions exactly on the interpolation boundaries may yield ``np.nan`` values.

# %%
# define a sensor inside the interpolation boundaries
sens = magpy.Sensor(pixel=positions * 0.5, style=dict(pixel_size=0.5))

# %%
# rotate all object by a common random rotation with common anchor
rotation = dict(
    angle=-35, axis=(-1, 5, 0.8), anchor=(1, 80, -4)
)  # random rotation parameters
interp_cube.rotate_from_angax(**rotation)
sens.rotate_from_angax(**rotation)
cube.rotate_from_angax(**rotation)

# %%
# display system
fig = go.Figure()
magpy.display(cube, sens, interp_cube, canvas=fig, backend='plotly')
fig

# %%
# compare the interpolated field with the original source
Bcube = sens.getB(cube)
Binterp = sens.getB(interp_cube)
print("Field interpolation error [%]:\n", ((Bcube - Binterp) / Bcube * 100).round(3))

# %%
# .. note::
#    The interpolation performance can be in fact arbitrary precise and in this example only 2
#    points per dimension, so that print outputs can be shown entirely.