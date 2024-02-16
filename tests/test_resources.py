import os

from compas_robots.resources import LocalPackageMeshLoader


def test_build_path():
    loader_with_support_package = LocalPackageMeshLoader("meshes", "ur_description")
    assert os.path.join("meshes", "ur_description", "urdf", "some.urdf") == loader_with_support_package.build_path(
        "urdf", "some.urdf"
    )

    loader_without_support_package = LocalPackageMeshLoader("meshes")
    assert os.path.join("meshes", "urdf", "some.urdf") == loader_without_support_package.build_path("urdf", "some.urdf")
