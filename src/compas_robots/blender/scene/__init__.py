from compas.plugins import plugin
from compas.scene import register

from compas_robots import RobotModel

from .robotmodelobject import RobotModelObject


@plugin(category="factories", requires=["bpy"])
def register_scene_objects():
    register(RobotModel, RobotModelObject, context="Blender")
    print("Blender Robot Object registered.")


__all__ = [
    "RobotModelObject",
]
