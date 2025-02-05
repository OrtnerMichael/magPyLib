from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np
import plotly
import pytest
import pyvista

import magpylib as magpy
from magpylib._src.display.traces_utility import draw_arrow_from_vertices
from magpylib._src.display.traces_utility import get_orientation_from_vec
from magpylib._src.display.traces_utility import merge_scatter3d
from magpylib._src.exceptions import MagpylibBadUserInput


def test_draw_arrow_from_vertices():
    """tests also the edge case when a vertex is in -y direction"""
    vertices = np.array(
        [
            [-1.0, 1.0, 1.0],
            [-1.0, -1.0, 1.0],
            [-1.0, -1.0, -1.0],
            [-1.0, 1.0, -1.0],
            [-1.0, 1.0, 1.0],
        ]
    )
    result = draw_arrow_from_vertices(vertices, sign=1, arrow_size=1)
    expected = np.array(
        [
            [-1.0, 1.0, 1.0],
            [-1.0, 0.0, 1.0],
            [-0.88, 0.2, 1.0],
            [-1.0, 0.0, 1.0],
            [-1.12, 0.2, 1.0],
            [-1.0, 0.0, 1.0],
            [-1.0, -1.0, 1.0],
            [-1.0, -1.0, 1.0],
            [-1.0, -1.0, 0.0],
            [-1.12, -1.0, 0.2],
            [-1.0, -1.0, 0.0],
            [-0.88, -1.0, 0.2],
            [-1.0, -1.0, 0.0],
            [-1.0, -1.0, -1.0],
            [-1.0, -1.0, -1.0],
            [-1.0, 0.0, -1.0],
            [-1.12, -0.2, -1.0],
            [-1.0, 0.0, -1.0],
            [-0.88, -0.2, -1.0],
            [-1.0, 0.0, -1.0],
            [-1.0, 1.0, -1.0],
            [-1.0, 1.0, -1.0],
            [-1.0, 1.0, 0.0],
            [-1.12, 1.0, -0.2],
            [-1.0, 1.0, 0.0],
            [-0.88, 1.0, -0.2],
            [-1.0, 1.0, 0.0],
            [-1.0, 1.0, 1.0],
        ]
    )

    np.testing.assert_allclose(
        result, expected, err_msg="draw arrow from vertices failed"
    )


def test_bad_backend():
    """test bad plotting input name"""
    with pytest.raises(MagpylibBadUserInput):
        c = magpy.magnet.Cuboid(polarization=(0, 0, 1), dimension=(1, 1, 1))
        c.show(backend="asdf")


@pytest.mark.parametrize(
    "canvas,is_notebook_result,backend",
    [
        (None, True, "plotly"),
        (None, False, "matplotlib"),
        (plt.subplot(projection="3d"), True, "matplotlib"),
        (plt.subplot(projection="3d"), False, "matplotlib"),
        (plotly.graph_objects.Figure(), True, "plotly"),
        (plotly.graph_objects.Figure(), False, "plotly"),
        (plotly.graph_objects.FigureWidget(), True, "plotly"),
        (plotly.graph_objects.FigureWidget(), False, "plotly"),
        (pyvista.Plotter(), True, "pyvista"),
        (pyvista.Plotter(), False, "pyvista"),
    ],
)
def test_infer_backend(canvas, is_notebook_result, backend):
    """test inferring auto backend"""
    with patch("magpylib._src.utility.is_notebook", return_value=is_notebook_result):
        # pylint: disable=import-outside-toplevel
        from magpylib._src.display.display import infer_backend

        assert infer_backend(canvas) == backend


def test_merge_scatter3d():
    """test_merge_scatter3d"""

    def get_traces(n):
        return [{"type": "scatter3d", "x": [i], "y": [i], "z": [i]} for i in range(n)]

    merge_scatter3d(*get_traces(1))
    merge_scatter3d(*get_traces(3))


def test_get_orientation_from_vec():
    """test get_orientation_from_vec"""
    # should return ref axis non null vectors and invalid inputs
    # antiparallel to the ref_axis should return valid 180 rotation
    ref_axis = (0, 0, 1)
    vec = np.array(
        [
            [0, 0, 1],
            [0, 1, 0],
            [0, 0, 1],
            [np.nan, 0, 0],
            [0, 0, 0],
            [0, 0, -1],
            [1, 2, 3],
            [4, 5, 6],
        ]
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        vec = (vec.T / np.linalg.norm(vec, axis=1)).T
    hasnan = np.isnan(vec).any(axis=1)
    orient = get_orientation_from_vec(vec, ref_axis=ref_axis)
    vec[hasnan] = ref_axis
    np.testing.assert_allclose(vec, orient.apply(ref_axis), atol=1e-8)
