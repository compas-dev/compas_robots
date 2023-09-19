from compas.plugins import plugin
from compas.artists import Artist

from compas_robots.robots import RobotModel
from .robotmodelartist import RobotModelArtist


@plugin(category="factories", requires=["bpy"])
def register_artists():
    Artist.register(RobotModel, RobotModelArtist, context="Blender")
    print("Blender Robot Artists registered.")


__all__ = [
    "RobotModelArtist",
]
