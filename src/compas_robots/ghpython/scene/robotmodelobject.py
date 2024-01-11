from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas_ghpython
from compas_ghpython.scene import GHSceneObject
from compas_rhino.conversions import transformation_to_rhino

from compas_robots.scene import BaseRobotModelObject


class RobotModelObject(GHSceneObject, BaseRobotModelObject):
    """Scene object for drawing robot models.

    Parameters
    ----------
    model : :class:`~compas_robots.RobotModel`
        Robot model.
    **kwargs : dict, optional
        Additional keyword arguments.
        See :class:`~compas_ghpython.scene.GHSceneObject` and :class:`~compas_robots.scene.BaseRobotModelObject` for more info.

    """

    def __init__(self, model, **kwargs):
        super(RobotModelObject, self).__init__(model=model, **kwargs)

    def transform(self, native_mesh, transformation):
        T = transformation_to_rhino(transformation)
        native_mesh.Transform(T)

    def create_geometry(self, geometry, name=None, color=None):
        """Create the scene objecy representing the robot geometry.

        Parameters
        ----------
        geometry : :class:`~compas.datastructures.Mesh`
            Instance of a mesh data structure
        name : str, optional
            The name of the mesh to draw.
        color : :class:`~compas.colors.Color`
            The color of the object.`

        Returns
        -------
        :rhino:`Rhino.Geometry.Mesh`
        """
        color = color.rgba255 if color else None

        vertices, faces = geometry.to_vertices_and_faces(triangulated=False)
        mesh = compas_ghpython.draw_mesh(vertices, faces, color=color)

        # Try to fix invalid meshes
        if not mesh.IsValid:
            mesh.FillHoles()

        return mesh

    def draw(self):
        """Draw the visual meshes of the robot model.

        Returns
        -------
        list[:rhino:`Rhino.Geometry.Mesh`]

        """
        return self.draw_visual()
