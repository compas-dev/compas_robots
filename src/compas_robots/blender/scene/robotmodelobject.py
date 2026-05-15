from typing import Any
from typing import Optional

import bpy
import mathutils
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Transformation
from compas_blender.conversions import mesh_to_blender
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
        # BaseRobotModelObject.__init__ calls self.create() before BlenderSceneObject.__init__
        # finishes, so these attributes must exist by the time create_geometry runs.
        self.objects = []
        self.collection = kwargs.get("collection")
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

    def _root_collection_name(self) -> str:
        if isinstance(self.collection, str) and self.collection:
            return self.collection
        return self.model.name

    def _collection_path_for(self, name: Optional[str]) -> str:
        """Return the ``::``-separated collection path for a mesh.

        Mesh names follow the pattern ``model.visual_or_collision.link_name.index``.
        The resulting hierarchy is ``root::visual_or_collision::link_name``,
        where *root* is ``self.collection`` (if a non-empty string) or the model name.
        """
        parts = (name or "").split(".")
        if len(parts) >= 3:
            mesh_type = parts[1]  # "visual" or "collision"
            link_name = ".".join(parts[2:-1]) if len(parts) > 3 else parts[2]
        else:
            mesh_type = "visual"
            link_name = "unknown"

        return f"{self._root_collection_name()}::{mesh_type}::{link_name}"

    @staticmethod
    def _apply_collection_flags(collection_name: str, hide_viewport: bool, hide_render: bool) -> None:
        """Set the data-level viewport and render flags on a collection.

        ``Collection.hide_viewport`` and ``Collection.hide_render`` cascade to all
        child collections and their objects, so one call covers the whole subtree.
        """
        if collection_name in bpy.data.collections:
            coll = bpy.data.collections[collection_name]
            coll.hide_viewport = hide_viewport
            coll.hide_render = hide_render

    def set_object_color(self, obj: bpy.types.Object, color: Color) -> None:
        super().set_object_color(obj, color)
        # NOTE: compas_blender sets diffuse_color but not the node graph, so renders appear grey.
        # Remove this override once fixed upstream in compas_blender.
        material = obj.active_material
        if material:
            material.use_nodes = True  # activating this creates node_tree if absent
            bsdf = material.node_tree.nodes.get("Principled BSDF") if material.node_tree else None
            if bsdf:
                bsdf.inputs["Base Color"].default_value = color.rgba

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
        if color is None:
            color = Color(1.0, 1.0, 1.0)

        mesh_data = mesh_to_blender(geometry)
        native_mesh = self.create_object(mesh_data, name=name)
        collection_path = self._collection_path_for(name)
        # update_object's `collection` is annotated `Optional[str]` upstream but accepts a Collection at runtime.
        self.update_object(native_mesh, color=color, collection=collection_path)  # type: ignore[arg-type]

        # Hide the visual/collision parent collection (e.g. "ur5e::visual") so all
        # meshes under it start hidden. Idempotent — fine to call once per mesh type.
        # Collision meshes are also excluded from renders by default.
        parts = collection_path.split("::")
        parent_path = "::".join(parts[:2])
        is_collision = len(parts) > 1 and parts[1] == "collision"
        self._apply_collection_flags(parent_path, hide_viewport=True, hide_render=is_collision)

        return native_mesh

    def _ensure_geometry(self):
        # BlenderSceneObject.__init__ resets self.objects = [] *after* BaseRobotModelObject.__init__
        # has already populated it via self.create(), so self.objects can't be trusted here.
        # Check the model's link state instead.
        for link in self.model.iter_links():
            for item in link.visual:
                if item.native_geometry:
                    return
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
        self._apply_collection_flags(f"{self._root_collection_name()}::visual", hide_viewport=False, hide_render=False)
        return visuals

    def draw_collision(self) -> list[bpy.types.Object]:
        """Draw the collision mesh of the robot model.

        Returns
        -------
        list[bpy.types.Object]

        """
        self._ensure_geometry()
        collisions = super(RobotModelObject, self).draw_collision()
        # Show in viewport but keep excluded from renders.
        self._apply_collection_flags(f"{self._root_collection_name()}::collision", hide_viewport=False, hide_render=True)
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
