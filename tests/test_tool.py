import os

import compas
import pytest
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Cone
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import allclose

from compas_robots import ToolModel
from compas_robots.model import Joint

BASE_FOLDER = os.path.dirname(__file__)


def unproxied(origin):
    """Link origins are wrapped in a URDF `FrameProxy`, which proxies attributes
    but not equality, so unwrap before comparing."""
    return Frame(origin.point, origin.xaxis, origin.yaxis)


@pytest.fixture
def mesh():
    return Mesh.from_stl(compas.get("cone.stl"))


@pytest.fixture
def cone_along_z():
    """A cone modelled along +Z, 0.1 long with a radius of 0.02, the way a tool
    tends to come out of a CAD document."""
    return Mesh.from_shape(Cone(radius=0.02, height=0.1))


@pytest.fixture
def kinematic_gripper():
    """A tool with joints: a body plus two jaws sliding apart along Y, modelled
    reaching along +Z the way a gripper tends to come out of a CAD document."""
    tool = ToolModel(Mesh.from_shape(Box(0.04)), Frame([0, 0, 0.1], [0, 1, 0], [1, 0, 0]), name="gripper")
    base = tool.root
    for index, side in enumerate([1, -1]):
        jaw = tool.add_link("jaw_{}".format(index), visual_mesh=Mesh.from_shape(Box(0.01)))
        tool.add_joint(
            "jaw_joint_{}".format(index),
            Joint.PRISMATIC,
            base,
            jaw,
            origin=Frame([0, side * 0.02, 0.05], [1, 0, 0], [0, 1, 0]),
            axis=Vector(0, side, 0),
            limit=(0.0, 0.02),
        )
    return tool


@pytest.fixture
def cone_tool_json():
    return os.path.join(BASE_FOLDER, "fixtures", "cone_tool.json")


@pytest.fixture
def frame():
    return Frame([0.14, 0, 0], [0, 1, 0], [0, 0, 1])


def test_basic_tool_model(mesh, frame):
    tool = ToolModel(mesh, frame)
    assert tool.name == "attached_tool"


def test_without_a_base_frame_the_modelling_coordinates_are_the_base(mesh, frame):
    tool = ToolModel(mesh, frame)
    assert tool.frame == frame
    assert all(item.origin is None for item in tool.root.visual + tool.root.collision)


def test_base_frame_re_expresses_geometry_and_tcf(cone_along_z):
    """A tool modelled along +Z, mounted so that +Z of the drawing points away
    from the robot: the tool's own frame ends up with the tip on +X.
    """
    base_frame = Frame([0, 0, 0], [0, 0, 1], [1, 0, 0])
    tcf_as_modelled = Frame([0, 0, 0.1], [0, 1, 0], [1, 0, 0])

    tool = ToolModel(cone_along_z, tcf_as_modelled, base_frame=base_frame)

    assert allclose(tool.frame.point, Point(0.1, 0, 0), tol=1e-9)

    # The geometry is not baked, it carries the origin like a URDF <origin> would
    for item in tool.root.visual + tool.root.collision:
        assert allclose(unproxied(item.origin), Frame([0, 0, 0], [0, 1, 0], [0, 0, 1]), tol=1e-9)

    # ...and the origin is honoured by the meshes handed to consumers: the cone is
    # modelled 0.1 long along +Z, and comes back 0.1 long along +X
    collision_mesh = tool.get_link_collision_meshes(tool.root)[0]
    points = [Point(*collision_mesh.vertex_coordinates(v)) for v in collision_mesh.vertices()]
    assert min(p.x for p in points) == pytest.approx(0.0, abs=1e-9)
    assert max(p.x for p in points) == pytest.approx(0.1, abs=1e-9)
    assert max(abs(p.y) for p in points) == pytest.approx(0.02, abs=1e-9)
    assert max(abs(p.z) for p in points) == pytest.approx(0.02, abs=1e-9)


def test_reframe_base_moves_a_kinematic_tool_as_a_whole(kinematic_gripper):
    """Re-framing a tool with joints must move the whole mechanism, not just the
    base geometry: the jaws, their joint axes, and the TCF all have to follow.
    """
    configuration = kinematic_gripper.zero_configuration()
    configuration.joint_values = [0.01, 0.01]

    base_frame = Frame([0, 0, 0], [0, 0, 1], [1, 0, 0])
    before = list(kinematic_gripper.transformed_frames(configuration))
    tcf_before = kinematic_gripper.frame

    kinematic_gripper.reframe_base(base_frame)

    after = list(kinematic_gripper.transformed_frames(configuration))
    assert len(after) == len(before)
    # Every link ends up where it was, read in the new base frame
    for frame_before, frame_after in zip(before, after):
        assert allclose(frame_after, base_frame.to_local_coordinates(frame_before), tol=1e-9)
    assert allclose(kinematic_gripper.frame, base_frame.to_local_coordinates(tcf_before), tol=1e-9)

    # The comparison above is what catches a joint left behind, or an axis rotated a
    # second time by re-initializing the tree. This adds that the jaws still articulate.
    closed = kinematic_gripper.zero_configuration()
    closed.joint_values = [0.0, 0.0]
    travel = [Point(*opened.point).distance_to_point(Point(*shut.point)) for opened, shut in zip(after, kinematic_gripper.transformed_frames(closed))]
    assert max(travel) == pytest.approx(0.01, abs=1e-9)


def test_base_frame_survives_serialization(cone_along_z):
    base_frame = Frame([0.1, 0, 0], [0, 0, 1], [1, 0, 0])
    tool = ToolModel(cone_along_z, Frame([0, 0, 0.14], [0, 1, 0], [1, 0, 0]), base_frame=base_frame)

    other = ToolModel.__from_data__(tool.__data__)

    assert other.frame == tool.frame
    for item, other_item in zip(tool.root.visual, other.root.visual):
        assert allclose(unproxied(item.origin), unproxied(other_item.origin), tol=1e-9)


def test_from_json(cone_tool_json):
    tool = ToolModel.from_json(cone_tool_json)
    assert [link.name for link in tool.iter_links()] == ["attached_tool_link"]
    assert tool.name == "attached_tool"


def test_from_t0cf_to_tcf(mesh, frame):
    tool = ToolModel(mesh, frame)
    frames_t0cf = [Frame((-0.363, 0.003, -0.147), (0.388, -0.351, -0.852), (0.276, 0.926, -0.256))]
    result = tool.from_t0cf_to_tcf(frames_t0cf)
    expected = [
        Frame(
            Point(-0.309, -0.046, -0.266),
            Vector(0.276, 0.926, -0.256),
            Vector(0.879, -0.136, 0.456),
        )
    ]
    assert allclose(result[0], expected[0], tol=1e-03)


def test_from_tcf_to_t0cf(mesh, frame):
    tool = ToolModel(mesh, frame)
    frames_tcf = [Frame((-0.309, -0.046, -0.266), (0.276, 0.926, -0.256), (0.879, -0.136, 0.456))]
    result = tool.from_tcf_to_t0cf(frames_tcf)
    expected = [
        Frame(
            Point(-0.363, 0.003, -0.147),
            Vector(0.388, -0.351, -0.852),
            Vector(0.276, 0.926, -0.256),
        )
    ]
    assert allclose(result[0], expected[0], tol=1e-03)
