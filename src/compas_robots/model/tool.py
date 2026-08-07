from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from compas.geometry import Frame
from compas.geometry import Transformation

from .joint import Joint
from .link import Link
from .link import Material
from .robot import RobotModel

if TYPE_CHECKING:
    from typing import Optional


class ToolModel(RobotModel):
    """Represents a tool to be attached to the robot's flange.
    Typical modeling convention for the tool geometry should follow: 
    - Origin (of the tool geometry) coincide with the center of the robot tool flange.
    - XY plane (of the tool geometry) coplanar with the robot tool flange. 
    - Z-axis-positive (of the tool geometry) pointing from robot flange towards the tool's mounting flange.

    Parameters
    ----------
    visual
        The visual mesh of the tool.
    frame_in_tool0_frame
        The frame of the tool tip (TCF), see `base_frame` for the
        coordinate system it is expressed in.
    collision
        The collision mesh of the tool. Defaults to the visual mesh.
    name
        The name of the tool. Defaults to ``'attached_tool'``.
    connected_to
        The name of the `Link` to which the tool is attached. Defaults to `None`.
    base_frame
        The frame of the tool geometry that mounts (will coincide) with the robot's flange.
        Only to be defined if the tool geometry is not modelled according to the typical convention
        (flange on XY plane and Z-axis-positive pointing from robot flange towards the tool).
        Expressed in the coordinate system the geometry was modelled in. 

        Defaults to `None`, meaning the geometry is already modelled in the tool's
        base frame, i.e. the flange sits at its origin.

    Attributes
    ----------
    frame : compas.geometry.Frame
        The frame of the tool in reference to the tool0 frame.
    connected_to : str
        The name of the `Link` to which the tool is attached (ie. connected) to.  Defaults to `None`.

    Examples
    --------
    >>> import compas
    >>> from compas.datastructures import Mesh
    >>> from compas.geometry import Frame
    >>> mesh = Mesh.from_stl(compas.get("cone.stl"))
    >>> frame = Frame([0.14, 0, 0], [0, 1, 0], [0, 0, 1])
    >>> tool = ToolModel(mesh, frame)

    A tool modelled along the Z axis of the document it was drawn in, mounted so
    that the Z axis of the drawing points away from the robot:

    >>> base_frame = Frame([0, 0, 0], [0, 0, 1], [1, 0, 0])
    >>> tool = ToolModel(mesh, Frame([0, 0, 0.14], [0, 1, 0], [1, 0, 0]), base_frame=base_frame)
    >>> tool.frame.point
    Point(x=0.140, y=0.000, z=0.000)

    """

    def __init__(
        self,
        visual,
        frame_in_tool0_frame,
        collision=None,
        name="attached_tool",
        connected_to=None,
        base_frame=None,
    ):
        super(ToolModel, self).__init__(name)
        self.frame = frame_in_tool0_frame
        self.connected_to = connected_to

        if visual:
            collision = collision or visual
            self.add_link("attached_tool_link", visual_mesh=visual, collision_mesh=collision)

            self._rebuild_tree()
            self._create(self.root, Transformation())

        if base_frame:
            self.reframe_base(base_frame)

    def reframe_base(self, base_frame: Frame) -> None:
        """Re-express the tool relative to the frame the robot's flange takes hold of it at.

        Everything the tool is made of — its geometry, its TCF, and the joints
        leaving its base link — is currently expressed relative to the tool's base
        frame. This states that the flange actually sits at `base_frame` instead of
        at the origin, and re-expresses all of it accordingly.

        Use it to model a tool wherever is convenient (a mesh drawn in a CAD document,
        say) and declare separately where the robot takes hold of it, rather than
        having to model it in its own base frame.

        Nothing is baked into the geometry: the frame is folded into the `origin` of
        the base link's visual and collision elements, and of the joints attached to
        it, which is the same mechanism URDF uses. Calling this again re-frames the
        tool again, relative to its current base.

        Parameters
        ----------
        base_frame
            The frame at which the robot's flange takes hold of the tool, expressed
            in the tool's current coordinate system.

        Examples
        --------
        >>> import compas
        >>> from compas.datastructures import Mesh
        >>> from compas.geometry import Frame
        >>> mesh = Mesh.from_stl(compas.get("cone.stl"))
        >>> tool = ToolModel(mesh, Frame([0, 0, 0.14], [0, 1, 0], [1, 0, 0]))
        >>> tool.reframe_base(Frame([0, 0, 0], [0, 0, 1], [1, 0, 0]))
        >>> tool.frame.point
        Point(x=0.140, y=0.000, z=0.000)

        """
        transformation = Transformation.from_frame(base_frame).inverted()

        self.frame = base_frame.to_local_coordinates(self.frame)

        if self.root:
            # The geometry of the base link, and the joints hanging off it, are placed
            # relative to the base link's frame, which is what is being moved here.
            for item in itertools.chain(self.root.visual, self.root.collision, self.root.joints):
                item.origin = self._reframed_origin(item.origin, transformation)

            self._rebuild_tree()
            self._create(self.root, Transformation())

    @staticmethod
    def _reframed_origin(origin: Optional[Frame], transformation: Transformation) -> Frame:
        """Compose `transformation` onto an origin that may not be set yet (i.e. identity)."""
        if not origin:
            return Frame.from_transformation(transformation)
        return Frame.from_transformation(transformation * Transformation.from_frame(origin))

    @classmethod
    def from_robot_model(cls, robot: RobotModel, frame_in_tool0_frame: Frame, connected_to: Optional[str] = None) -> ToolModel:
        """Creates a `ToolModel` from a [RobotModel][compas_robots.RobotModel] instance.

        Parameters
        ----------
        robot
            The robot model the tool is built from.
        frame_in_tool0_frame
            The frame of the tool in tool0 frame.
        connected_to
            The name of the `Link` to which the tool is attached.
            Defaults to `None`.

        """
        data = robot.__data__
        data["frame"] = frame_in_tool0_frame.__data__
        data["connected_to"] = connected_to
        return cls.__from_data__(data)

    @property
    def __dtype__(self):
        return "compas_robots/ToolModel"

    @property
    def __data__(self):
        """Returns the data dictionary that represents the tool.

        Returns
        -------
        dict
            The tool data.

        """
        data = RobotModel.__data__.fget(self)
        data["frame"] = self.frame.__data__
        data["connected_to"] = self.connected_to
        return data

    @classmethod
    def __from_data__(cls, data):
        """Construct a `ToolModel` from its data representation.

        To be used in conjunction with the `__data__` property.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        ToolModel
            The newly created instance of tool model.

        """
        tool = cls(
            None,
            frame_in_tool0_frame=Frame.__from_data__(data["frame"]),
            name=data["name"],
            connected_to=data.get("connected_to"),
        )
        tool.joints = [Joint.__from_data__(d) for d in data.get("joints", [])]
        tool.links = [Link.__from_data__(d) for d in data.get("links", [])]
        tool.materials = [Material.__from_data__(d) for d in data.get("materials", [])]
        tool._rebuild_tree()
        tool._create(tool.root, Transformation())

        return tool

    def from_tcf_to_t0cf(self, frames_tcf: list[Frame]) -> list[Frame]:
        """Converts a list of frames at the robot's tool tip (tcf frame) to frames at the robot's flange (tool0 frame).

        Parameters
        ----------
        frames_tcf
            Frames (in WCF) at the robot's tool tip (tcf).

        Returns
        -------
        list[Frame]
            Frames (in WCF) at the robot's flange (`tool0`).

        Examples
        --------
        >>> import compas
        >>> from compas.datastructures import Mesh
        >>> from compas.geometry import Frame
        >>> mesh = Mesh.from_stl(compas.get("cone.stl"))
        >>> frame = Frame([0.14, 0, 0], [0, 1, 0], [0, 0, 1])
        >>> tool = ToolModel(mesh, frame)
        >>> frames_tcf = [Frame((-0.309, -0.046, -0.266), (0.276, 0.926, -0.256), (0.879, -0.136, 0.456))]
        >>> t0cf_frame = tool.from_tcf_to_t0cf(frames_tcf)[0]
        >>> t0cf_frame.point
        Point(x=-0.363, y=0.003, z=-0.147)
        >>> t0cf_frame.xaxis
        Vector(x=0.388, y=-0.351, z=-0.852)
        >>> t0cf_frame.yaxis
        Vector(x=0.276, y=0.926, z=-0.256)

        """
        Te = Transformation.from_frame_to_frame(self.frame, Frame.worldXY())
        return [Frame.from_transformation(Transformation.from_frame(f) * Te) for f in frames_tcf]

    def from_t0cf_to_tcf(self, frames_t0cf: list[Frame]) -> list[Frame]:
        """Converts frames at the robot's flange (tool0 frame) to frames at the robot's tool tip (tcf frame).

        Parameters
        ----------
        frames_t0cf
            Frames (in WCF) at the robot's flange (tool0).

        Returns
        -------
        list[Frame]
            Frames (in WCF) at the robot's tool tip (tcf).

        Examples
        --------
        >>> import compas
        >>> from compas.datastructures import Mesh
        >>> from compas.geometry import Frame
        >>> mesh = Mesh.from_stl(compas.get("cone.stl"))
        >>> frame = Frame([0.14, 0, 0], [0, 1, 0], [0, 0, 1])
        >>> tool = ToolModel(mesh, frame)
        >>> frames_t0cf = [Frame((-0.363, 0.003, -0.147), (0.388, -0.351, -0.852), (0.276, 0.926, -0.256))]
        >>> tcf_frame = tool.from_t0cf_to_tcf(frames_t0cf)[0]
        >>> tcf_frame.point
        Point(x=-0.309, y=-0.046, z=-0.266)
        >>> tcf_frame.xaxis
        Vector(x=0.276, y=0.926, z=-0.256)
        >>> tcf_frame.yaxis
        Vector(x=0.879, y=-0.136, z=0.456)

        """
        Te = Transformation.from_frame_to_frame(Frame.worldXY(), self.frame)
        return [Frame.from_transformation(Transformation.from_frame(f) * Te) for f in frames_t0cf]
