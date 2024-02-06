"""
********************************************************************************
compas_robots
********************************************************************************

.. currentmodule:: compas_robots


.. toctree::
    :maxdepth: 1


"""

from __future__ import print_function

import os

__author__ = ["Gonzalo Casas"]
__copyright__ = "COMPAS Association"
__license__ = "MIT License"
__email__ = "casas@arch.ethz.ch"
__version__ = "0.2.2"


from .configuration import Configuration
from .model.robot import RobotModel
from .model.tool import ToolModel

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "data"))


def _find_resource(filename):
    filename = filename.strip("/")
    return os.path.abspath(os.path.join(DATA, filename))


def get(filename):
    return _find_resource(filename)


__all__ = ["Configuration", "RobotModel", "ToolModel", "get"]

__all_plugins__ = [
    "compas_robots.blender.scene",
    "compas_robots.ghpython.scene",
    "compas_robots.rhino.scene",
    "compas_robots.rhino.install",
]
