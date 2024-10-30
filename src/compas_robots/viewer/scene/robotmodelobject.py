from typing import Optional

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Transformation
from compas_viewer.scene import MeshObject
from compas_viewer.scene import ViewerSceneObject

from compas_robots import Configuration
from compas_robots.scene import BaseRobotModelObject


class RobotModelObject(BaseRobotModelObject, ViewerSceneObject):
    """Viewer scene object for displaying COMPAS Robot geometry.

    Parameters
    ----------
    model : :class:`compas_robots.RobotModel`
        The robot model.
    configuration : :class:`compas_robots.Configuration`, optional
        The initial configuration of the robot. Defaults to the zero configuration.
    show_visual : bool, optional
        Toggle the visibility of the visual geometry. Defaults to True.
    show_collision : bool, optional
        Toggle the visibility of the collision geometry. Defaults to False.
    hide_coplanaredges : bool, optional
        True to hide the coplanar edges. It will override the value in the config file.
    use_vertexcolors : bool, optional
        True to use vertex color. It will override the value in the config file.
    **kwargs : dict, optional
        Additional keyword arguments.
        For more info, see :class:`compas_viewer.scene.ViewerSceneObject`.

    See Also
    --------
    :class:`compas_robots.scene.BaseRobotModelObject`
    :class:`compas_viewer.scene.ViewerSceneObject`
    """

    def __init__(
        self,
        configuration: Optional[Configuration] = None,
        show_visual: Optional[bool] = None,
        show_collision: Optional[bool] = None,
        hide_coplanaredges: Optional[bool] = None,
        use_vertexcolors: Optional[bool] = None,
        **kwargs,
    ):
        self.kwargs = kwargs
        self.use_vertexcolors = use_vertexcolors
        self.hide_coplanaredges = hide_coplanaredges
        self._show_visual = show_visual or True
        self._show_collision = show_collision or False

        super(RobotModelObject, self).__init__(**kwargs)
        self.configuration: Configuration = configuration or self.model.zero_configuration()

        self.visual_objects: list[MeshObject] = self.draw_visual()
        self.collision_objects: list[MeshObject] = self.draw_collision()

    @property
    def viewer(self):
        from compas_viewer import Viewer

        return Viewer()

    @property
    def show_visual(self):
        return self._show_visual

    @show_visual.setter
    def show_visual(self, value: bool):
        if value == self._show_visual:
            return
        self._show_visual = value
        for i, visual_object in enumerate(self.visual_objects):
            if value:
                parent = self
                if i > 0:
                    parent = self.visual_objects[i - 1]
                self.scene.add(visual_object, parent)
                self.scene.instance_colors[visual_object.instance_color.rgb255] = visual_object
            else:
                self.scene.remove(visual_object)

    @property
    def show_collision(self):
        return self._show_collision

    @show_collision.setter
    def show_collision(self, value: bool):
        if value == self._show_collision:
            return
        self._show_collision = value
        for i, collision_object in enumerate(self.collision_objects):
            if value:
                parent = self
                if i > 0:
                    parent = self.visual_objects[i - 1]
                self.scene.add(collision_object, parent)
                self.scene.instance_colors[collision_object.instance_color.rgb255] = collision_object
            else:
                self.scene.remove(collision_object)

    def init(self):
        """Initialize the robot object with creating the visual and collision objects."""
        self.instance_color = Color.from_rgb255(*next(self.viewer.scene._instance_colors_generator))
        self.viewer.scene.instance_colors[self.instance_color.rgb255] = self

        def add_objects(objects, show_flag):
            """Helper function to initialize and add objects to the scene."""
            parent = self
            for i, obj in enumerate(objects):
                obj.init()
                if show_flag:
                    if i > 0:
                        parent = objects[i - 1]
                    self.viewer.scene.add(obj, parent)
                    self.viewer.scene.instance_colors[obj.instance_color.rgb255] = obj

        add_objects(self.visual_objects, self.show_visual)
        add_objects(self.collision_objects, self.show_collision)

    def transform(self, geometry, transformation: Transformation):
        """Transform the geometry by a given transformation.

        See Also
        --------
        :class:`compas_robots.scene.AbstractRobotModelObject`
        """
        geometry.transformation = transformation * geometry.transformation

    def create_geometry(self, item: Mesh, name: Optional[str] = None, color: Optional[Color] = None) -> MeshObject:
        """Create a mesh object from a given geometry.

        See Also
        --------
        :class:`compas_robots.scene.AbstractRobotModelObject`
        """
        kwargs = self.kwargs.copy()
        del kwargs["item"], kwargs["facecolor"]

        mesh_object = MeshObject(
            item=item,
            name=name,
            facecolor=color,
            **kwargs,
            hide_coplanaredges=self.hide_coplanaredges,
            use_vertexcolors=self.use_vertexcolors,
        )
        mesh_object.transformation = Transformation()

        return mesh_object

    def update_joints(self, joint_state: Configuration):
        """Update the robot joints."""

        self.configuration = joint_state or self.configuration
        super().update(self.configuration, self.show_visual, self.show_collision)

        if self.show_visual:
            for obj in self.visual_objects:
                obj._update_matrix()

        if self.show_collision:
            for obj in self.collision_objects:
                obj._update_matrix()

        self.viewer.renderer.update()
