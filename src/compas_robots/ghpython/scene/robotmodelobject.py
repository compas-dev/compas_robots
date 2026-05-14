from typing import Optional

from compas.colors import Color
from compas.datastructures import Mesh
from compas_ghpython.drawing import draw_mesh
from compas_ghpython.scene import GHSceneObject
from compas_rhino.conversions import transformation_to_rhino

from compas_robots.scene import BaseRobotModelObject


class RobotModelObject(GHSceneObject, BaseRobotModelObject):
    """Scene object for drawing robot models.

    Parameters
    ----------
    **kwargs : dict, optional
        Additional keyword arguments.
        See [GHSceneObject][compas_ghpython.scene.GHSceneObject] and [BaseRobotModelObject][compas_robots.scene.BaseRobotModelObject] for more info.

    """

    def __init__(self, **kwargs):
        super(RobotModelObject, self).__init__(**kwargs)

    def transform(self, native_mesh, transformation):
        T = transformation_to_rhino(transformation)
        native_mesh.Transform(T)

    def create_geometry(self, geometry: Mesh, name: Optional[str] = None, color: Optional[Color] = None):
        """Create the scene objecy representing the robot geometry.

        Parameters
        ----------
        geometry
            Instance of a mesh data structure
        name
            The name of the mesh to draw.
        color
            The color of the object.`

        Returns
        -------
        `Rhino.Geometry.Mesh`
        """
        color = color.rgba255 if color else None

        vertices, faces = geometry.to_vertices_and_faces(triangulated=False)
        mesh = draw_mesh(vertices, faces, color=color)

        # Try to fix invalid meshes
        if not mesh.IsValid:
            mesh.FillHoles()

        return mesh

    def draw(self):
        """Draw the visual meshes of the robot model.

        Returns
        -------
        list[`Rhino.Geometry.Mesh`]

        """
        return self.draw_visual()
