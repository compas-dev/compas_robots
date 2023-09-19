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
__copyright__ = "compas-dev"
__license__ = "MIT License"
__email__ = "casas@arch.ethz.ch"
__version__ = "0.1.0"


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all__ = ["HOME", "DATA", "DOCS", "TEMP"]


__all_plugins__ = [
    "compas_robots.blender.artists",
    "compas_robots.ghpython.artists",
    "compas_robots.rhino.artists",
]
