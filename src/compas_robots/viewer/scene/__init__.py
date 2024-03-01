from compas.plugins import plugin
from compas.scene import register

from compas_robots import RobotModel

from .robotmodelobject import RobotModelObject


@plugin(category="factories", requires=["compas_viewer"])
def register_scene_objects():
    register(RobotModel, RobotModelObject, context="Viewer")


__all__ = [
    "RobotModelObject",
]
