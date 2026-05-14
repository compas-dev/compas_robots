from typing import Any
from typing import Optional

import bpy
import compas_blender
import mathutils
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Transformation
from compas_blender.scene import BlenderSceneObject

from compas_robots.scene import BaseRobotModelObject


class RobotModelObject(BlenderSceneObject, BaseRobotModelObject):
    """Scene object for drawing robot models in Blender.

    Parameters
    ----------
    **kwargs : dict, optional
        Additional keyword arguments.
        For more info,
        see [BlenderSceneObject][compas_blender.scene.BlenderSceneObject] and [BaseRobotModelObject][compas_robots.scene.BaseRobotModelObject].

    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def transform(self, native_mesh: bpy.types.Object, transformation: Transformation) -> None:
        """Transform the mesh of a robot model.

        Parameters
        ----------
        native_mesh
            A mesh scene object.
        transformation
            A transformation matrix.

        Returns
        -------
        None

        """
        native_mesh.matrix_world = mathutils.Matrix(transformation.matrix) @ native_mesh.matrix_world

    def create_geometry(
        self,
        geometry: Mesh,
        name: Optional[str] = None,
        color: Optional[Color] = None,
    ) -> bpy.types.Object:
        """Create the scene object representing the robot geometry.

        Parameters
        ----------
        geometry
            Instance of a mesh data structure
        name
            The name of the mesh to draw.
        color
            The color of the object.

        Returns
        -------
        bpy.types.Object

        """
        color = color.rgb if color else None

        # Imported colors take priority over a the parameter color
        if "mesh_color.diffuse" in geometry.attributes:
            color = geometry.attributes["mesh_color.diffuse"]

        # If we have a color, we'll discard alpha because draw_mesh is hard coded for a=1
        if color:
            color = color[:3]
        else:
            color = (1.0, 1.0, 1.0)

        v, f = geometry.to_vertices_and_faces(triangulated=False)

        native_mesh = compas_blender.draw_mesh(
            vertices=v,
            faces=f,
            name=name,
            color=color,
            centroid=False,
            collection=self.collection,
        )
        native_mesh.hide_set(True)
        return native_mesh

    def _ensure_geometry(self):
        if len(self.collection.objects) == 0:
            self.create()

    def draw(self) -> list[bpy.types.Object]:
        """Draw the robot model.

        Returns
        -------
        list[bpy.types.Object]

        """
        self._ensure_geometry()
        return self.draw_visual()

    def draw_visual(self) -> list[bpy.types.Object]:
        """Draw the robot model.

        Returns
        -------
        list[bpy.types.Object]

        """
        self._ensure_geometry()
        visuals = super(RobotModelObject, self).draw_visual()
        for visual in visuals:
            visual.hide_set(False)
        return visuals

    def draw_collision(self) -> list[bpy.types.Object]:
        """Draw the collision mesh of the robot model.

        Returns
        -------
        list[bpy.types.Object]

        """
        self._ensure_geometry()
        collisions = super(RobotModelObject, self).draw_collision()
        for collision in collisions:
            collision.hide_set(False)
        return collisions

    def draw_attached_meshes(self) -> list[bpy.types.Object]:
        """Draw the meshes attached to the robot model, if any.

        Returns
        -------
        list[bpy.types.Object]

        """
        self._ensure_geometry()
        meshes = super(RobotModelObject, self).draw_attached_meshes()
        for mesh in meshes:
            mesh.hide_set(False)
        return meshes
