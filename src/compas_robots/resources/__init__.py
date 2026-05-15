"""
Model descriptions rarely embed geometry directly; instead, they reference it
through filenames or URLs pointing to externally hosted resources. This package
provides loader classes that automate fetching and processing those resources.
"""

from __future__ import absolute_import

from .mesh_importer import get_file_format
from .mesh_importer import mesh_import
from .basic import AbstractMeshLoader
from .basic import DefaultMeshLoader
from .basic import LocalPackageMeshLoader
from .github import GithubPackageMeshLoader

__all__ = [
    "AbstractMeshLoader",
    "DefaultMeshLoader",
    "LocalPackageMeshLoader",
    "GithubPackageMeshLoader",
    "get_file_format",
    "mesh_import",
]
