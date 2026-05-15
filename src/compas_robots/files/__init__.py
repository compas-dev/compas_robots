"""
This package provides the URDF file format parser used to load robot models
from standard URDF descriptions.
"""

from __future__ import absolute_import

from .urdf import URDF
from .urdf import URDFElement
from .urdf import URDFGenericElement
from .urdf import URDFParser

__all__ = [
    "URDF",
    "URDFElement",
    "URDFGenericElement",
    "URDFParser",
]
