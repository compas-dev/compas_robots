from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Frame
from compas.geometry import Transformation

from .joint import Joint
from .link import Link
from .link import Material
from .robot import RobotModel


class ToolModel(RobotModel):
    """Represents a tool to be attached to the robot's flange.

    Attributes
    ----------
    frame : :class:`~compas.geometry.Frame`
        The frame of the tool in reference to the tool0 frame.
    connected_to : str
        The name of the `Link` to which the tool is attached (ie. connected) to.  Defaults to ``None``.

    Examples
    --------
    >>> import compas
    >>> from compas.datastructures import Mesh
    >>> from compas.geometry import Frame
    >>> mesh = Mesh.from_stl(compas.get('cone.stl'))
    >>> frame = Frame([0.14, 0, 0], [0, 1, 0], [0, 0, 1])
    >>> tool = ToolModel(mesh, frame)

    """

    def __init__(
        self,
        visual,
        frame_in_tool0_frame,
        collision=None,
        name="attached_tool",
        connected_to=None,
    ):
        super(ToolModel, self).__init__(name)
        self.frame = frame_in_tool0_frame
        self.connected_to = connected_to

        if visual:
            collision = collision or visual
            self.add_link("attached_tool_link", visual_mesh=visual, collision_mesh=collision)

            self._rebuild_tree()
            self._create(self.root, Transformation())

    @classmethod
    def from_robot_model(cls, robot, frame_in_tool0_frame, connected_to=None):
        """Creates a ``ToolModel`` from a :class:`~compas_robots.RobotModel` instance.

        Parameters
        ----------
        robot : :class:`~compas_robots.RobotModel`
        frame_in_tool0_frame : str
            The frame of the tool in tool0 frame.
        connected_to : str
            The name of the `Link` to which the tool is attached.
            Defaults to ``None``.

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

        To be used in conjunction with the :meth:`to_data` method.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`ToolModel`
            The constructed `ToolModel`.

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

    def from_tcf_to_t0cf(self, frames_tcf):
        """Converts a list of frames at the robot's tool tip (tcf frame) to frames at the robot's flange (tool0 frame).

        Parameters
        ----------
        frames_tcf : list[:class:`~compas.geometry.Frame`]
            Frames (in WCF) at the robot's tool tip (tcf).

        Returns
        -------
        list[:class:`~compas.geometry.Frame`]
            Frames (in WCF) at the robot's flange (tool0).

        Examples
        --------
        >>> import compas
        >>> from compas.datastructures import Mesh
        >>> from compas.geometry import Frame
        >>> mesh = Mesh.from_stl(compas.get('cone.stl'))
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

    def from_t0cf_to_tcf(self, frames_t0cf):
        """Converts frames at the robot's flange (tool0 frame) to frames at the robot's tool tip (tcf frame).

        Parameters
        ----------
        frames_t0cf : list[:class:`~compas.geometry.Frame`]
            Frames (in WCF) at the robot's flange (tool0).

        Returns
        -------
        list[:class:`~compas.geometry.Frame`]
            Frames (in WCF) at the robot's tool tip (tcf).

        Examples
        --------
        >>> import compas
        >>> from compas.datastructures import Mesh
        >>> from compas.geometry import Frame
        >>> mesh = Mesh.from_stl(compas.get('cone.stl'))
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
