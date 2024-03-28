from compas.plugins import plugin
from compas.scene import register

from compas_robots import RobotModel


@plugin(category="factories", requires=["compas_viewer"])
def register_scene_objects():
    from .robotmodelobject import RobotModelObject

    register(RobotModel, RobotModelObject, context="Viewer")


__all__ = [
    "RobotModelObject",
]
