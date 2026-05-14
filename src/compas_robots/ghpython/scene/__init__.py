"""
This package provides functionality for visualizing robot models in Grasshopper.
"""

from compas.plugins import plugin
from compas.scene import register

from compas_robots import RobotModel

from .robotmodelobject import RobotModelObject


@plugin(category="factories", requires=["Rhino"])
def register_scene_objects():
    register(RobotModel, RobotModelObject, context="Grasshopper")
    print("GH Robot Object registered.")


__all__ = [
    "RobotModelObject",
]
