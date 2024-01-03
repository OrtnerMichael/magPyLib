"""
Implementation for the magnetic field of homogeneously
magnetized tetrahedra. Computation details in function docstrings.
"""
import numpy as np

from magpylib._src.fields.field_BH_triangle import triangle_field
from magpylib._src.input_checks import check_field_input
from magpylib._src.utility import convert_HBMJ


def check_chirality(points: np.ndarray) -> np.ndarray:
    """
    Checks if quadruple of points (p0,p1,p2,p3) that forms tetrahedron is arranged in a way
    that the vectors p0p1, p0p2, p0p3 form a right-handed system

    Parameters
    -----------
    points: 3d-array of shape (m x 4 x 3)
            m...number of tetrahedrons

    Returns
    ----------
    new list of points, where p2 and p3 are possibly exchanged so that all
    tetrahedron is given in a right-handed system.
    """

    vecs = np.zeros((len(points), 3, 3))
    vecs[:, :, 0] = points[:, 1, :] - points[:, 0, :]
    vecs[:, :, 1] = points[:, 2, :] - points[:, 0, :]
    vecs[:, :, 2] = points[:, 3, :] - points[:, 0, :]

    dets = np.linalg.det(vecs)
    dets_neg = dets < 0

    if np.any(dets_neg):
        points[dets_neg, 2:, :] = points[dets_neg, 3:1:-1, :]

    return points


def point_inside(points: np.ndarray, vertices: np.ndarray) -> np.ndarray:
    """
    Takes points, as well as the vertices of a tetrahedra.
    Returns boolean array indicating whether the points are inside the tetrahedra.
    """
    mat = vertices[:, 1:].swapaxes(0, 1) - vertices[:, 0]
    mat = np.transpose(mat.swapaxes(0, 1), (0, 2, 1))

    tetra = np.linalg.inv(mat)
    newp = np.matmul(tetra, np.reshape(points - vertices[:, 0, :], (*points.shape, 1)))
    inside = (
        np.all(newp >= 0, axis=1)
        & np.all(newp <= 1, axis=1)
        & (np.sum(newp, axis=1) <= 1)
    ).flatten()

    return inside


# CORE
def magnet_tetrahedron_field(
    *,
    field: str,
    observers: np.ndarray,
    vertices: np.ndarray,
    polarization: np.ndarray,
    in_out="auto",
) -> np.ndarray:
    """
    Magnetic field generated by a homogeneously magnetized tetrahedra.

    SI units are used for all inputs and outputs.

    Parameters
    ----------
    field: str, default=`'B'`
        If `field='B'` return B-field in units of T, if `field='H'` return H-field
        in units of A/m.

    observers: ndarray, shape (n,3)
        Observer positions (x,y,z) in Cartesian coordinates in units of m.

    vertices: ndarray, shape (n,4,3)
        Vertices of the individual tetrahedrons [(pos1a, pos1b, pos1c, pos1d),
        (pos2a, pos2b, pos2c, pos2d), ...] given in units of m.

    polarization: ndarray, shape (n,3)
        Magnetic polarization vectors in units of T.

    in_out: {'auto', 'inside', 'outside'}
        Specify the location of the observers relative to the magnet body, affecting the calculation
        of the magnetic field. The options are:
        - 'auto': The location (inside or outside the cuboid) is determined automatically for each
          observer.
        - 'inside': All observers are considered to be inside the cuboid; use this for performance
          optimization if applicable.
        - 'outside': All observers are considered to be outside the cuboid; use this for performance
          optimization if applicable.
        Choosing 'auto' is fail-safe but may be computationally intensive if the mix of observer
        locations is unknown.

    Returns
    -------
    B-field or H-field: ndarray, shape (n,3)
        B- or H-field of source in Cartesian coordinates in units of T or A/m.

    Examples
    --------
    Compute the B-field of two different tetrahedron-observer instances

    >>> import numpy as np
    >>> import magpylib as magpy
    >>> B = magpy.core.magnet_tetrahedron_field(
    ...     field='B',
    ...     observers=np.array([(1,2,3), (2,3,4)]),
    ...     vertices=np.array([((-1,0,0), (1,-1,0), (1,1,0), (0,0,1))]*2),
    ...     polarization=np.array([(222,333,444), (111,112,113)]),
    ... )
    >>> print(B)
    [[0.19075398 0.8240532  1.18170862]
     [0.03125701 0.08445416 0.1178967 ]]

    Notes
    -----
    Advanced unit use: The input unit of magnetization and polarization
    gives the output unit of H and B. All results are independent of the
    length input units. One must be careful, however, to use consistently
    the same length unit throughout a script.

    The tetrahedron is built up via 4 faces applying the Triangle class, making sure that
    all normal vectors point outwards, and providing inside-outside evaluation to
    distinguish between B- and H-field.
    """

    check_field_input(field)

    n = len(observers)

    vertices = check_chirality(vertices)
    mask_inside = None
    if in_out == "auto" and field != "H":
        mask_inside = point_inside(observers, vertices)
    elif in_out != "auto":
        val = in_out == "inside"
        mask_inside = np.full(len(observers), val)

    if field in "MJ":
        return convert_HBMJ(
            output_field_type=field,
            polarization=polarization,
            mask_inside=mask_inside,
        )

    tri_vertices = np.concatenate(
        (
            vertices[:, (0, 2, 1), :],
            vertices[:, (0, 1, 3), :],
            vertices[:, (1, 2, 3), :],
            vertices[:, (0, 3, 2), :],
        ),
        axis=0,
    )
    tri_fields = triangle_field(
        field=field,
        observers=np.tile(observers, (4, 1)),
        vertices=tri_vertices,
        polarization=np.tile(polarization, (4, 1)),
    )
    tetra_field = (  # slightly faster than reshape + sum
        tri_fields[:n]
        + tri_fields[n : 2 * n]
        + tri_fields[2 * n : 3 * n]
        + tri_fields[3 * n :]
    )

    if field == "H":
        return tetra_field

    # if B, and inside magnet add polarization vector
    tetra_field[mask_inside] += polarization[mask_inside]
    return tetra_field
