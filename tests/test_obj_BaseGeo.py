import re

import numpy as np
import pytest
from scipy.spatial.transform import Rotation as R

import magpylib as magpy
from magpylib._src.obj_classes.class_BaseGeo import BaseGeo

# pylint: disable=no-member


def test_BaseGeo_basics():
    """fundamental usage test"""

    ptest = np.array(
        [
            [0, 0, 0],
            [1, 2, 3],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0.67545246, -0.6675014, -0.21692852],
        ]
    )

    otest = np.array(
        [
            [0, 0, 0],
            [0.1, 0.2, 0.3],
            [0.1, 0.2, 0.3],
            [0, 0, 0],
            [0.20990649, 0.41981298, 0.62971947],
            [0, 0, 0],
            [0.59199676, 0.44281248, 0.48074693],
        ]
    )

    poss, rots = [], []

    bgeo = BaseGeo((0, 0, 0), None)
    poss += [bgeo.position.copy()]
    rots += [bgeo.orientation.as_rotvec()]

    bgeo.position = (1, 2, 3)
    bgeo.orientation = R.from_rotvec((0.1, 0.2, 0.3))
    poss += [bgeo.position.copy()]
    rots += [bgeo.orientation.as_rotvec()]

    bgeo.move((-1, -2, -3))
    poss += [bgeo.position.copy()]
    rots += [bgeo.orientation.as_rotvec()]

    rot = R.from_rotvec((-0.1, -0.2, -0.3))
    bgeo.rotate(rotation=rot, start=-1)
    poss += [bgeo.position.copy()]
    rots += [bgeo.orientation.as_rotvec()]

    bgeo.rotate_from_angax(angle=45, axis=(1, 2, 3))
    poss += [bgeo.position.copy()]
    rots += [bgeo.orientation.as_rotvec()]

    bgeo.rotate_from_angax(-np.pi / 4, (1, 2, 3), degrees=False)
    poss += [bgeo.position.copy()]
    rots += [bgeo.orientation.as_rotvec()]

    rot = R.from_rotvec((0.1, 0.2, 0.3))
    bgeo.rotate(rot, anchor=(3, 2, 1), start=-1)
    bgeo.rotate_from_angax(33, (3, 2, 1), anchor=0, start=-1)
    poss += [bgeo.position.copy()]
    rots += [bgeo.orientation.as_rotvec()]

    poss = np.array(poss)
    rots = np.array(rots)

    # avoid generating different zeros in macos CI tests (atol=1e-6)
    np.testing.assert_allclose(
        poss,
        ptest,
        atol=1e-6,
        err_msg="test_BaseGeo bad position",
    )
    np.testing.assert_allclose(
        rots,
        otest,
        atol=1e-6,
        err_msg="test_BaseGeo bad orientation",
    )


def test_rotate_vs_rotate_from():
    """testing rotate vs rotate_from_angax"""
    roz = [
        (0.1, 0.2, 0.3),
        (-0.1, -0.1, -0.1),
        (0.2, 0, 0),
        (0.3, 0, 0),
        (0, 0, 0.4),
        (0, -0.2, 0),
    ]

    bg1 = BaseGeo(position=(3, 4, 5), orientation=R.from_quat((0, 0, 0, 1)))
    for ro in roz:
        rroz = R.from_rotvec((ro,))
        bg1.rotate(rotation=rroz, anchor=(-3, -2, 1))
    pos1 = bg1.position
    ori1 = bg1.orientation.as_quat()

    bg2 = BaseGeo(position=(3, 4, 5), orientation=R.from_quat((0, 0, 0, 1)))
    angs = np.linalg.norm(roz, axis=1)
    for ang, ax in zip(angs, roz):
        bg2.rotate_from_angax(angle=[ang], degrees=False, axis=ax, anchor=(-3, -2, 1))
    pos2 = bg2.position
    ori2 = bg2.orientation.as_quat()

    np.testing.assert_allclose(pos1, pos2)
    np.testing.assert_allclose(ori1, ori2)


def test_BaseGeo_reset_path():
    """testing reset path"""
    # pylint: disable=protected-access
    bg = BaseGeo((0, 0, 0), R.from_quat((0, 0, 0, 1)))
    bg.move([(1, 1, 1)] * 11)

    assert len(bg._position) == 12, "bad path generation"

    bg.reset_path()
    assert len(bg._position) == 1, "bad path reset"


def test_BaseGeo_anchor_None():
    """testing rotation with None anchor"""
    pos = np.array([1, 2, 3])
    bg = BaseGeo(pos, R.from_quat((0, 0, 0, 1)))
    bg.rotate(R.from_rotvec([(0.1, 0.2, 0.3), (0.2, 0.4, 0.6)]))

    pos3 = np.array([pos] * 3)
    rot3 = np.array([(0, 0, 0), (0.1, 0.2, 0.3), (0.2, 0.4, 0.6)])
    np.testing.assert_allclose(
        bg.position,
        pos3,
        err_msg="None rotation changed position",
    )
    np.testing.assert_allclose(
        bg.orientation.as_rotvec(),
        rot3,
        err_msg="None rotation did not adjust rot",
    )


def evall(obj):
    """return pos and orient of object"""
    # pylint: disable=protected-access
    pp = obj._position
    rr = obj._orientation.as_quat()
    rr = np.array([r / max(r) for r in rr])
    return (pp, rr)


def test_attach():
    """test attach functionality"""
    bg = BaseGeo([0, 0, 0], R.from_rotvec((0, 0, 0)))
    rot_obj = R.from_rotvec([(x, 0, 0) for x in np.linspace(0, 10, 11)])
    bg.rotate(rot_obj, start=-1)

    bg2 = BaseGeo([0, 0, 0], R.from_rotvec((0, 0, 0)))
    roto = R.from_rotvec(((1, 0, 0),))
    for _ in range(10):
        bg2.rotate(roto)

    np.testing.assert_allclose(
        bg.position,
        bg2.position,
        err_msg="attach p",
    )
    np.testing.assert_allclose(
        bg.orientation.as_quat(),
        bg2.orientation.as_quat(),
        err_msg="attach o",
    )


def test_path_functionality1():
    """testing path functionality in detail"""
    pos0 = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5.0]])
    rot0 = R.from_quat(
        [(1, 0, 0, 1), (2, 0, 0, 1), (4, 0, 0, 1), (5, 0, 0, 1), (10, 0, 0, 1.0)]
    )
    inpath = np.array([(0.1, 0.1, 0.1), (0.2, 0.2, 0.2), (0.3, 0.3, 0.3)])

    b1, b2, b3, b4, b5 = pos0
    c1, c2, c3 = inpath
    q1, q2, q3, q4, q5 = np.array(
        [(1, 0, 0, 1), (1, 0, 0, 0.5), (1, 0, 0, 0.25), (1, 0, 0, 0.2), (1, 0, 0, 0.1)]
    )

    pos, ori = evall(BaseGeo(pos0, rot0))
    P = np.array([b1, b2, b3, b4, b5])
    Q = np.array([q1, q2, q3, q4, q5])
    np.testing.assert_allclose(pos, P)
    np.testing.assert_allclose(ori, Q)

    pos, ori = evall(BaseGeo(pos0, rot0).move(inpath, start=0))
    P = np.array([b1 + c1, b2 + c2, b3 + c3, b4, b5])
    Q = np.array([q1, q2, q3, q4, q5])
    np.testing.assert_allclose(pos, P)
    np.testing.assert_allclose(ori, Q)

    pos, ori = evall(BaseGeo(pos0, rot0).move(inpath, start=1))
    P = np.array([b1, b2 + c1, b3 + c2, b4 + c3, b5])
    Q = np.array([q1, q2, q3, q4, q5])
    np.testing.assert_allclose(pos, P)
    np.testing.assert_allclose(ori, Q)

    pos, ori = evall(BaseGeo(pos0, rot0).move(inpath, start=2))
    P = np.array([b1, b2, b3 + c1, b4 + c2, b5 + c3])
    Q = np.array([q1, q2, q3, q4, q5])
    np.testing.assert_allclose(pos, P)
    np.testing.assert_allclose(ori, Q)


def test_path_functionality2():
    """testing path functionality in detail"""
    pos0 = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5.0]])
    rot0 = R.from_quat(
        [(1, 0, 0, 1), (2, 0, 0, 1), (4, 0, 0, 1), (5, 0, 0, 1), (10, 0, 0, 1.0)]
    )
    inpath = np.array([(0.1, 0.1, 0.1), (0.2, 0.2, 0.2), (0.3, 0.3, 0.3)])

    b1, b2, b3, b4, b5 = pos0
    c1, c2, c3 = inpath
    q1, q2, q3, q4, q5 = np.array(
        [(1, 0, 0, 1), (1, 0, 0, 0.5), (1, 0, 0, 0.25), (1, 0, 0, 0.2), (1, 0, 0, 0.1)]
    )

    pos, ori = evall(BaseGeo(pos0, rot0).move(inpath, start=3))
    P = np.array([b1, b2, b3, b4 + c1, b5 + c2, b5 + c3])
    Q = np.array([q1, q2, q3, q4, q5, q5])
    np.testing.assert_allclose(pos, P)
    np.testing.assert_allclose(ori, Q)

    pos, ori = evall(BaseGeo(pos0, rot0).move(inpath, start=4))
    P = np.array([b1, b2, b3, b4, b5 + c1, b5 + c2, b5 + c3])
    Q = np.array([q1, q2, q3, q4, q5, q5, q5])
    np.testing.assert_allclose(pos, P)
    np.testing.assert_allclose(ori, Q)

    pos, ori = evall(BaseGeo(pos0, rot0).move(inpath, start=5))
    P = np.array([b1, b2, b3, b4, b5, b5 + c1, b5 + c2, b5 + c3])
    Q = np.array([q1, q2, q3, q4, q5, q5, q5, q5])
    np.testing.assert_allclose(pos, P)
    np.testing.assert_allclose(ori, Q)

    pos, ori = evall(BaseGeo(pos0, rot0).move(inpath, start=5))
    P = np.array([b1, b2, b3, b4, b5, b5 + c1, b5 + c2, b5 + c3])
    Q = np.array([q1, q2, q3, q4, q5, q5, q5, q5])
    np.testing.assert_allclose(pos, P)
    np.testing.assert_allclose(ori, Q)

    pos, ori = evall(BaseGeo(pos0, rot0).move(inpath))
    P = np.array([b1, b2, b3, b4, b5, b5 + c1, b5 + c2, b5 + c3])
    Q = np.array([q1, q2, q3, q4, q5, q5, q5, q5])
    np.testing.assert_allclose(pos, P)
    np.testing.assert_allclose(ori, Q)


def test_path_functionality3():
    """testing path functionality in detail"""
    pos0 = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5.0]])
    rot0 = R.from_quat(
        [(1, 0, 0, 1), (2, 0, 0, 1), (4, 0, 0, 1), (5, 0, 0, 1), (10, 0, 0, 1.0)]
    )
    inpath = np.array([(0.1, 0.1, 0.1), (0.2, 0.2, 0.2), (0.3, 0.3, 0.3)])

    pos1, ori1 = evall(BaseGeo(pos0, rot0).move(inpath, start=4))
    pos2, ori2 = evall(BaseGeo(pos0, rot0).move(inpath, start=-1))
    np.testing.assert_allclose(pos1, pos2)
    np.testing.assert_allclose(ori1, ori2)

    pos1, ori1 = evall(BaseGeo(pos0, rot0).move(inpath, start=3))
    pos2, ori2 = evall(BaseGeo(pos0, rot0).move(inpath, start=-2))
    np.testing.assert_allclose(pos1, pos2)
    np.testing.assert_allclose(ori1, ori2)

    pos1, ori1 = evall(BaseGeo(pos0, rot0).move(inpath, start=2))
    pos2, ori2 = evall(BaseGeo(pos0, rot0).move(inpath, start=-3))
    np.testing.assert_allclose(pos1, pos2)
    np.testing.assert_allclose(ori1, ori2)

    pos1, ori1 = evall(BaseGeo(pos0, rot0).move(inpath, start=1))
    pos2, ori2 = evall(BaseGeo(pos0, rot0).move(inpath, start=-4))
    np.testing.assert_allclose(pos1, pos2)
    np.testing.assert_allclose(ori1, ori2)

    pos1, ori1 = evall(BaseGeo(pos0, rot0).move(inpath, start=0))
    pos2, ori2 = evall(BaseGeo(pos0, rot0).move(inpath, start=-5))
    np.testing.assert_allclose(pos1, pos2)
    np.testing.assert_allclose(ori1, ori2)


def test_scipy_from_methods():
    """test all rotation methods inspired from scipy implemented in BaseTransform"""

    def cube():
        return magpy.magnet.Cuboid(polarization=(11, 22, 33), dimension=(1, 1, 1))

    angs_deg = np.linspace(0, 360, 10)
    angs = np.deg2rad(angs_deg)
    rot = R.from_rotvec((np.array([[0, 0, 1]] * 10).T * angs).T)
    anchor = (1, 2, 3)
    cube0 = cube().rotate(rot, anchor=anchor)

    from_rotvec = cube().rotate_from_rotvec(
        rot.as_rotvec(degrees=True), anchor=anchor, degrees=True
    )
    np.testing.assert_allclose(
        cube0.position,
        from_rotvec.position,
        rtol=1e-05,
        atol=1e-08,
        err_msg="from_rotvec failed on position",
    )
    np.testing.assert_allclose(
        cube0.orientation.as_rotvec(),
        from_rotvec.orientation.as_rotvec(),
        err_msg="from_rotvec failed on orientation",
    )

    from_angax = cube().rotate_from_angax(angs_deg, "z", anchor=anchor, degrees=True)
    np.testing.assert_allclose(
        cube0.position,
        from_angax.position,
        err_msg="from_angax failed on position",
    )
    np.testing.assert_allclose(
        cube0.orientation.as_rotvec(),
        from_angax.orientation.as_rotvec(),
        err_msg="from_rotvec failed on orientation",
    )

    from_euler = cube().rotate_from_euler(angs_deg, "z", anchor=anchor, degrees=True)
    np.testing.assert_allclose(
        cube0.position,
        from_euler.position,
        rtol=1e-05,
        atol=1e-08,
        err_msg="from_euler failed on position",
    )
    np.testing.assert_allclose(
        cube0.orientation.as_rotvec(),
        from_euler.orientation.as_rotvec(),
        err_msg="from_rotvec failed on orientation",
    )

    from_matrix = cube().rotate_from_matrix(rot.as_matrix(), anchor=anchor)
    np.testing.assert_allclose(
        cube0.position,
        from_matrix.position,
        rtol=1e-05,
        atol=1e-08,
        err_msg="from_matrix failed on position",
    )
    np.testing.assert_allclose(
        cube0.orientation.as_rotvec(),
        from_matrix.orientation.as_rotvec(),
        err_msg="from_rotvec failed on orientation",
    )

    from_mrp = cube().rotate_from_mrp(rot.as_mrp(), anchor=anchor)
    np.testing.assert_allclose(
        cube0.position,
        from_mrp.position,
        rtol=1e-05,
        atol=1e-08,
        err_msg="from_mrp failed on position",
    )
    np.testing.assert_allclose(
        cube0.orientation.as_rotvec(),
        from_mrp.orientation.as_rotvec(),
        err_msg="from_rotvec failed on orientation",
    )

    from_quat = cube().rotate_from_quat(rot.as_quat(), anchor=anchor)
    np.testing.assert_allclose(
        cube0.position,
        from_quat.position,
        rtol=1e-05,
        atol=1e-08,
        err_msg="from_quat failed on position",
    )
    np.testing.assert_allclose(
        cube0.orientation.as_rotvec(),
        from_quat.orientation.as_rotvec(),
        err_msg="from_rotvec failed on orientation",
    )


def test_style():
    """test when setting wrong style class"""
    bg = BaseGeo((0, 0, 0), None)
    bg.style = {"color": "red"}
    bg.style = {"label": "mylabel"}
    assert bg.style.color == "red"
    assert bg.style.label == "mylabel"
    with pytest.raises(ValueError):
        bg.style = "wrong class"


def test_kwargs():
    """test kwargs inputs, only relevant for styles"""
    bg = BaseGeo((0, 0, 0), None, style={"label": "label_01"}, style_label="label_02")
    assert bg.style.label == "label_02"

    with pytest.raises(TypeError):
        BaseGeo((0, 0, 0), None, styl_label="label_02")


def test_copy():
    """test copying object"""
    bg1 = BaseGeo((0, 0, 0), None, style_label="label1")  # has style
    bg2 = BaseGeo((1, 2, 3), None)  # has no style
    bg3 = BaseGeo((4, 6, 8), style_color="blue")  # has style but label is None
    bg1c = bg1.copy()
    bg2c = bg2.copy(position=(10, 0, 0), style={"color": "red"}, style_color="orange")
    bg3c = bg3.copy()

    # original object should not be affected"
    np.testing.assert_allclose(bg1.position, (0, 0, 0))
    np.testing.assert_allclose(bg2.position, (1, 2, 3))

    # check if label suffix iterated correctly
    assert bg1c.style.label == "label2"
    assert bg2c.style.label is None
    assert bg3c.style.label == "BaseGeo_01"

    # check if style is passed correctly
    assert bg2c.style.color == "orange"


def test_copy_parents():
    """make sure that parents are not copied"""
    x1 = magpy.Sensor()
    x2 = magpy.Sensor()
    x3 = magpy.Sensor()

    c = x1 + x2 + x3

    y = x1.copy()

    assert x1.parent.parent == c
    assert y.parent is None


def test_copy_order():
    """Make sure copying objects of a collection does not affect order of children (#530)"""

    thing1 = magpy.magnet.Cuboid(style_label="t1")
    thing2 = magpy.magnet.Cuboid(style_label="t2")
    thing3 = magpy.magnet.Cuboid(style_label="t3")
    coll = magpy.Collection(thing1, thing2, thing3)

    desc_before = coll.describe(format="label", return_string=True)

    thing1.copy()

    desc_after = coll.describe(format="label", return_string=True)

    assert desc_after == desc_before


def match_string_up_to_id(s1, s2, /):
    """Checks if 2 inputs (first is list, second string) match as long as id= follows a
    series of numbers"""
    patt = "id=[0-9]*[0-9]", "id=Regex"
    assert re.sub(*patt, "\n".join(s1)).split("\n") == re.sub(*patt, s2).split("\n")


def test_describe_with_label():
    """testing describe method"""
    # print("test = [\n    " + '",\n    '.join(f'"{s}' for s in desc.split("\n")) + '",\n]')
    # pylint: disable=protected-access
    x = magpy.magnet.Cuboid(style_label="x1")

    # describe calls print by default -> no return value
    desc = x.describe()
    assert desc is None

    # describe string
    test = [
        "Cuboid(id=2743358534352, label='x1')",
        "  • parent: None",
        "  • position: [0. 0. 0.] m",
        "  • orientation: [0. 0. 0.] deg",
        "  • dimension: None m",
        "  • magnetization: None A/m",
        "  • polarization: None T",
    ]
    match_string_up_to_id(test, x.describe(return_string=True))

    # describe html string
    test_html = ("<pre>" + "\n".join(test) + "</pre>").split("\n")
    match_string_up_to_id(test_html, x._repr_html_().replace("<br>", "\n"))


def test_describe_with_parent():
    """testing describe method"""
    # print("test = [\n    " + '",\n    '.join(f'"{s}' for s in desc.split("\n")) + '",\n]')
    x = magpy.magnet.Cuboid(style_label="x1")
    magpy.Collection(x)  # add parent
    test = [
        "Cuboid(id=1687262797456, label='x1')",
        "  • parent: Collection(id=1687262859280)",
        "  • position: [0. 0. 0.] m",
        "  • orientation: [0. 0. 0.] deg",
        "  • dimension: None m",
        "  • magnetization: None A/m",
        "  • polarization: None T",
    ]
    match_string_up_to_id(test, x.describe(return_string=True))


def test_describe_with_path():
    """testing describe method"""
    # print("test = [\n    " + '",\n    '.join(f'"{s}' for s in desc.split("\n")) + '",\n]')
    x = magpy.Sensor(position=[(1, 2, 3)] * 3)
    test = [
        "Sensor(id=2743359152656)",
        "  • parent: None",
        "  • path length: 3",
        "  • position (last): [1. 2. 3.] m",
        "  • orientation (last): [0. 0. 0.] deg",
        "  • handedness: right",
        "  • pixel: None",
    ]
    match_string_up_to_id(test, x.describe(return_string=True))


def test_describe_with_exclude_None():
    """testing describe method"""
    # print("test = [\n    " + '",\n    '.join(f'"{s}' for s in desc.split("\n")) + '",\n]')
    x = magpy.Sensor()
    test = [
        "Sensor(id=140534160166976)",
        "  • parent: None",
        "  • position: [0. 0. 0.] m",
        "  • orientation: [0. 0. 0.] deg",
        "  • handedness: right",
        "  • pixel: None",
        (
            "  • style: SensorStyle(arrows=ArrowCS(x=ArrowSingle(color=None, show=True),"
            " y=ArrowSingle(color=None, show=True), z=ArrowSingle(color=None, show=True)),"
            " color=None, description=Description(show=None, text=None), label=None,"
            " legend=Legend(show=None, text=None), model3d=Model3d(data=[], showdefault=True),"
            " opacity=None, path=Path(frames=None, line=Line(color=None, style=None, width=None),"
            " marker=Marker(color=None, size=None, symbol=None), numbering=None, show=None),"
            " pixel=Pixel(color=None, field=PixelField(colorscale=None, colorsource=None,"
            " shownull=None, sizemode=None, symbol=None, vectorsource=None), size=1,"
            " sizemode=None, symbol=None), size=None, sizemode=None)"
        ),
    ]
    match_string_up_to_id(test, x.describe(exclude=None, return_string=True))


def test_describe_with_many_pixels():
    """testing describe method"""
    # print("test = [\n    " + '",\n    '.join(f'"{s}' for s in desc.split("\n")) + '",\n]')
    x = magpy.Sensor(pixel=[[[(1, 2, 3)] * 5] * 5] * 3, handedness="left")
    test = [
        "Sensor(id=1687262996944)",
        "  • parent: None",
        "  • position: [0. 0. 0.] m",
        "  • orientation: [0. 0. 0.] deg",
        "  • handedness: left",
        "  • pixel: 75 (3x5x5)",
    ]
    match_string_up_to_id(test, x.describe(return_string=True))


def test_describe_with_triangularmesh():
    """testing describe method"""
    # print("test = [\n    " + '",\n    '.join(f'"{s}' for s in desc.split("\n")) + '",\n]')
    points = [
        (-1, -1, 0),
        (-1, 1, 0),
        (1, -1, 0),
        (1, 1, 0),
        (0, 0, 2),
    ]
    x = magpy.magnet.TriangularMesh.from_ConvexHull(
        polarization=(0, 0, 1),
        points=points,
        check_selfintersecting="skip",
    )
    test = [
        "TriangularMesh(id=1687257413648)",
        "  • parent: None",
        "  • position: [0. 0. 0.] m",
        "  • orientation: [0. 0. 0.] deg",
        "  • magnetization: [     0.              0.         795774.71545948] A/m",
        "  • polarization: [0. 0. 1.] T",
        "  • barycenter: [0.         0.         0.46065534]",
        "  • faces: shape(6, 3)",
        "  • mesh: shape(6, 3, 3)",
        "  • status_disconnected: False",
        "  • status_disconnected_data: 1 part",
        "  • status_open: False",
        "  • status_open_data: []",
        "  • status_reoriented: True",
        "  • status_selfintersecting: None",
        "  • status_selfintersecting_data: None",
        "  • vertices: shape(5, 3)",
    ]

    match_string_up_to_id(test, x.describe(return_string=True))


def test_unset_describe():
    """test describe completely unset objects"""
    objs = [
        magpy.magnet.Cuboid(),
        magpy.magnet.Cylinder(),
        magpy.magnet.CylinderSegment(),
        magpy.magnet.Sphere(),
        magpy.magnet.Tetrahedron(),
        # magpy.magnet.TriangularMesh(), not possible yet
        magpy.misc.Triangle(),
        magpy.misc.Dipole(),
        magpy.current.Polyline(),
        magpy.current.Circle(),
    ]

    for o in objs:
        o.describe()
