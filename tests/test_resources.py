import os

import compas_robots
from compas_robots.resources import LocalPackageMeshLoader
from compas_robots.resources import mesh_import


def test_build_path():
    loader_with_support_package = LocalPackageMeshLoader("meshes", "ur_description")
    assert os.path.join("meshes", "ur_description", "urdf", "some.urdf") == loader_with_support_package.build_path("urdf", "some.urdf")

    loader_without_support_package = LocalPackageMeshLoader("meshes")
    assert os.path.join("meshes", "urdf", "some.urdf") == loader_without_support_package.build_path("urdf", "some.urdf")


def test_mesh_import_namespaced_collada():
    filename = compas_robots.get("ur_description/meshes/ur5e/visual/base.dae")

    meshes = mesh_import(filename, filename)

    assert len(meshes) == 2
    assert meshes[0].number_of_vertices() == 1337
    assert meshes[0].number_of_faces() == 2598
    assert meshes[1].number_of_vertices() == 1158
    assert meshes[1].number_of_faces() == 2240
