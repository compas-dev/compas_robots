********************************************************************************
compas_robots.resources
********************************************************************************

.. currentmodule:: compas_robots.resources

.. rst-class:: lead

Model descriptions usually do not contain embedded geometry information but only
descriptions, filenames or URLs for externally hosted resources.
For that purpose, this package provides various loader classes that help automate
the processing of these resources.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    AbstractMeshLoader
    DefaultMeshLoader
    GithubPackageMeshLoader
    LocalPackageMeshLoader
