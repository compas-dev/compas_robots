from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_robots import RobotModel

from compas.plugins import plugin
from compas.scene.context import register

from .baserobotmodelobject import AbstractRobotModelObject
from .baserobotmodelobject import BaseRobotModelObject

@plugin(category="factories", pluggable_name="register_scene_objects")
def register_scene_objects_base():
    register(RobotModel, BaseRobotModelObject, context=None)

__all__ = [
    "AbstractRobotModelObject",
    "BaseRobotModelObject",
]
