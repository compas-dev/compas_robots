from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.plugins import plugin


@plugin(category="install")
def installable_rhino_packages():
    return ["compas_robots"]
