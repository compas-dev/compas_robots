from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas_ghpython
from compas_ghpython.scene import GHSceneObject

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

    # # again not really sure why this is here
    # def transform(self, native_mesh, transformation):
    #     xtransform(native_mesh, transformation)

    # same here
    # there is no reference to self...
    def create_geometry(self, geometry, name=None, color=None):
        print("Creating geometry", name, color)
        vertices, faces = geometry.to_vertices_and_faces(triangulated=False)

        mesh = compas_ghpython.draw_mesh(vertices, faces, color=color)
        # Try to fix invalid meshes
        if not mesh.IsValid:
            mesh.FillHoles()
        print("mesh", mesh)
        return mesh

    def draw(self):
        """Draw the visual meshes of the robot model.

        Returns
        -------
        list[:rhino:`Rhino.Geometry.Mesh`]

        """
        return self.draw_visual()
