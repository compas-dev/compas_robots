from __future__ import absolute_import

from compas.plugins import plugin
from compas.artists import Artist

from compas_robots.robots import RobotModel
from .robotmodelartist import RobotModelArtist


@plugin(category="factories", requires=["Rhino"])
def register_artists():
    Artist.register(RobotModel, RobotModelArtist, context="Rhino")
    print("Rhino Robot Artists registered.")


__all__ = [
    "RobotModelArtist",
]
