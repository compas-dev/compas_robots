from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.colors import Color
from compas.data import Data
from compas.geometry import Box
from compas.geometry import Capsule
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.geometry import Sphere
from compas.geometry import Transformation

from compas_robots.files import URDFElement
from compas_robots.files import URDFParser

from .base import ColorProxy
from .base import FrameProxy
from .base import _attr_from_data
from .base import _attr_to_data
from .geometry import BoxProxy
from .geometry import CapsuleProxy
from .geometry import CylinderProxy
from .geometry import LinkGeometry
from .geometry import Material
from .geometry import MeshDescriptor
from .geometry import SphereProxy
from .geometry import Texture


class Mass(Data):
    """Represents a value of mass usually related to a link."""

    def __init__(self, value):
        super(Mass, self).__init__()
        self.value = float(value)

    def __str__(self):
        return str(self.value)

    def get_urdf_element(self):
        attributes = {"value": self.value}
        return URDFElement("mass", attributes)

    @property
    def __data__(self):
        return {"value": self.value}


class Inertia(Data):
    """Rotational inertia matrix (3x3) represented in the inertia frame.

    Since the rotational inertia matrix is symmetric, only 6 above-diagonal
    elements of this matrix are specified here, using the attributes
    ``ixx``, ``ixy``, ``ixz``, ``iyy``, ``iyz``, ``izz``.

    """

    def __init__(self, ixx=0.0, ixy=0.0, ixz=0.0, iyy=0.0, iyz=0.0, izz=0.0):
        super(Inertia, self).__init__()
        self.ixx = float(ixx)
        self.ixy = float(ixy)
        self.ixz = float(ixz)
        self.iyy = float(iyy)
        self.iyz = float(iyz)
        self.izz = float(izz)

    def get_urdf_element(self):
        attributes = {
            "ixx": self.ixx,
            "ixy": self.ixy,
            "ixz": self.ixz,
            "iyy": self.iyy,
            "iyz": self.iyz,
            "izz": self.izz,
        }
        return URDFElement("inertia", attributes)

    @property
    def __data__(self):
        return {
            "ixx": self.ixx,
            "ixy": self.ixy,
            "ixz": self.ixz,
            "iyy": self.iyy,
            "iyz": self.iyz,
            "izz": self.izz,
        }

    @classmethod
    def __from_data__(cls, data):
        return cls(
            ixx=data.get("ixx", 0.0),
            ixy=data.get("ixy", 0.0),
            ixz=data.get("ixz", 0.0),
            iyy=data.get("iyy", 0.0),
            iyz=data.get("iyz", 0.0),
            izz=data.get("izz", 0.0),
        )


class Inertial(Data):
    """Inertial properties of a link.

    Attributes
    ----------
    origin
        This is the pose of the inertial reference frame,
        relative to the link reference frame.
    mass
        Mass of the link.
    inertia
        3x3 rotational inertia matrix, represented in the inertia frame.

    """

    def __init__(self, origin=None, mass=None, inertia=None):
        super(Inertial, self).__init__()
        self.origin = origin
        self.mass = mass
        self.inertia = inertia

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = FrameProxy.create_proxy(value)

    def get_urdf_element(self):
        elements = [self.origin, self.mass, self.inertia]
        return URDFElement("inertial", elements=elements)

    @property
    def __data__(self):
        return {
            "origin": self.origin.__data__ if self.origin else None,
            "mass": self.mass.__data__ if self.mass else None,
            "inertia": self.inertia.__data__ if self.inertia else None,
        }

    @classmethod
    def __from_data__(cls, data):
        origin = Frame.__from_data__(data["origin"]) if data["origin"] else None
        mass = Mass.__from_data__(data["mass"]) if data["mass"] else None
        inertia = Inertia.__from_data__(data["inertia"]) if data["inertia"] else None
        return cls(origin, mass, inertia)


class LinkItem(object):
    def __init__(self):
        self.init_transformation = None  # to store the init transformation
        self.current_transformation = None  # to store the current transformation
        self.native_geometry = None  # to store the link's CAD native geometry


class Visual(LinkItem, Data):
    """Visual description of a link.

    Attributes
    ----------
    geometry
        Shape of the visual element.
    origin
        Reference frame of the visual element with respect
        to the reference frame of the link.
    name
        Name of the visual element.
    material
        Material of the visual element.
    attr
        Non-standard attributes.

    """

    def __init__(self, geometry, origin=None, name=None, material=None, **kwargs):
        super(Visual, self).__init__()
        self.geometry = geometry
        self.origin = origin
        self.name = name
        self.material = material
        self.attr = kwargs

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = FrameProxy.create_proxy(value)

    def get_urdf_element(self):
        attributes = {}
        if self.name is not None:
            attributes["name"] = self.name
        attributes.update(self.attr)
        elements = [self.origin, self.geometry, self.material]
        return URDFElement("visual", attributes, elements)

    # Overriding the default name property, because sometimes the name really is `None`.
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def __data__(self):
        return {
            "geometry": self.geometry.__data__,
            "origin": self.origin.__data__ if self.origin else None,
            "name": self.name,
            "material": self.material.__data__ if self.material else None,
            "attr": _attr_to_data(self.attr),
            "init_transformation": self.init_transformation.__data__ if self.init_transformation else None,
            "current_transformation": self.current_transformation.__data__ if self.current_transformation else None,
        }

    @classmethod
    def __from_data__(cls, data):
        visual = cls(
            geometry=LinkGeometry.__from_data__(data["geometry"]),
            origin=Frame.__from_data__(data["origin"]) if data["origin"] else None,
            name=data["name"],
            material=Material.__from_data__(data["material"]) if data["material"] else None,
            **_attr_from_data(data["attr"]),
        )
        if data["init_transformation"]:
            visual.init_transformation = Transformation.__from_data__(data["init_transformation"])
        if data["current_transformation"]:
            visual.current_transformation = Transformation.__from_data__(data["current_transformation"])
        return visual

    def get_color(self):
        """Get the RGBA color array assigned to the link.

        Only if the link has a material assigned.

        Returns
        -------
        :class:`~compas.colors.Color`
            If the link has a material assigned, return its color.

        """
        if self.material:
            return self.material.get_color()
        else:
            return None

    @classmethod
    def from_primitive(cls, primitive, **kwargs):
        """Create visual link from a primitive shape.

        Parameters
        ----------
        primitive : :class:`compas.geometry.Shape`
            A primitive shape.
        **kwargs : dict[str, Any], optional
            The keyword arguments (kwargs) collected in a dict.
            These allow using non-standard attributes absent in the URDF specification.

        Returns
        -------
        :class:`~compas.datastructures.Mesh`
            A visual description object.
        """
        geometry = LinkGeometry()
        geometry.shape = primitive
        return cls(geometry, **kwargs)


class Collision(LinkItem, Data):
    """Collidable description of a link.

    Attributes
    ----------
    geometry
        Shape of the collidable element.
    origin
        Reference frame of the collidable element with respect
        to the reference frame of the link.
    name
        Name of the collidable element.
    attr
        Non-standard attributes.

    """

    def __init__(self, geometry, origin=None, name=None, **kwargs):
        super(Collision, self).__init__()
        self.geometry = geometry
        self.origin = origin
        self.name = name
        self.attr = kwargs

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = FrameProxy.create_proxy(value)

    def get_urdf_element(self):
        attributes = {}
        if self.name is not None:
            attributes["name"] = self.name
        attributes.update(self.attr)
        elements = [self.origin, self.geometry]
        return URDFElement("collision", attributes, elements)

    # Overriding the default name property, because sometimes the name really is `None`.
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def __data__(self):
        return {
            "geometry": self.geometry.__data__,
            "origin": self.origin.__data__ if self.origin else None,
            "name": self.name,
            "attr": _attr_to_data(self.attr),
            "init_transformation": self.init_transformation.__data__ if self.init_transformation else None,
            "current_transformation": self.current_transformation.__data__ if self.current_transformation else None,
        }

    @classmethod
    def __from_data__(cls, data):
        collision = cls(
            geometry=LinkGeometry.__from_data__(data["geometry"]),
            origin=Frame.__from_data__(data["origin"]) if data["origin"] else None,
            name=data["name"],
            attr=_attr_from_data(data["attr"]),
        )

        if data["init_transformation"]:
            collision.init_transformation = Transformation.__from_data__(data["init_transformation"])

        if data["current_transformation"]:
            collision.current_transformation = Transformation.__from_data__(data["current_transformation"])

        return collision

    @classmethod
    def from_primitive(cls, primitive, **kwargs):
        """Create collision link from a primitive shape.

        Parameters
        ----------
        primitive : :class:`compas.geometry.Shape`
            A primitive shape.
        **kwargs : dict[str, Any], optional
            The keyword arguments (kwargs) collected in a dict.
            These allow using non-standard attributes absent in the URDF specification.

        Returns
        -------
        :class:`~compas.datastructures.Mesh`
            A collision description object.
        """
        geometry = LinkGeometry()
        geometry.shape = primitive
        return cls(geometry, **kwargs)


class Link(Data):
    """Link represented as a rigid body with an inertia, visual, and collision features.

    Attributes
    ----------
    name
        Name of the link itself.
    type
        Link type. Undocumented in URDF, but used by PR2.
    visual
        Visual properties of the link.
    collision
        Collision properties of the link. This can be different
        from the visual properties of a link.
    inertial
        Inertial properties of the link.
    attr
        Non-standard attributes.
    joints
        A list of joints that are the link's children
    parent_joint
        The reference to a parent joint if it exists

    """

    def __init__(self, name, type=None, visual=(), collision=(), inertial=None, **kwargs):
        super(Link, self).__init__()
        self.name = name
        self.type = type
        self.visual = list(visual or [])
        self.collision = list(collision or [])
        self.inertial = inertial
        self.attr = kwargs
        self.joints = []
        self.parent_joint = None

    def get_urdf_element(self):
        attributes = {"name": self.name}
        if self.type is not None:
            attributes["type"] = self.type
        attributes.update(self.attr)
        elements = self.visual + self.collision + [self.inertial]
        return URDFElement("link", attributes, elements)

    @property
    def __data__(self):
        return {
            "name": self.name,
            "type": self.type,
            "visual": [visual.__data__ for visual in self.visual],
            "collision": [collision.__data__ for collision in self.collision],
            "inertial": self.inertial.__data__ if self.inertial else None,
            "attr": _attr_to_data(self.attr),
            "joints": [joint.__data__ for joint in self.joints],
        }

    @classmethod
    def __from_data__(cls, data):
        from .joint import Joint

        link = cls(
            name=data["name"],
            type=data["type"],
            visual=[Visual.__from_data__(d) for d in data["visual"]],
            collision=[Collision.__from_data__(d) for d in data["collision"]],
            inertial=Inertial.__from_data__(data["inertial"]) if data["inertial"] else None,
            **_attr_from_data(data["attr"]),
        )
        link.joints = [Joint.__from_data__(d) for d in data["joints"]]
        return link


URDFParser.install_parser(Link, "robot/link")
URDFParser.install_parser(Inertial, "robot/link/inertial")
URDFParser.install_parser(Mass, "robot/link/inertial/mass")
URDFParser.install_parser(Inertia, "robot/link/inertial/inertia")

URDFParser.install_parser(Visual, "robot/link/visual")
URDFParser.install_parser(Collision, "robot/link/collision")

URDFParser.install_parser(
    Frame,
    "robot/link/inertial/origin",
    "robot/link/visual/origin",
    "robot/link/collision/origin",
    proxy_type=FrameProxy,
)
URDFParser.install_parser(LinkGeometry, "robot/link/visual/geometry", "robot/link/collision/geometry")
URDFParser.install_parser(
    MeshDescriptor,
    "robot/link/visual/geometry/mesh",
    "robot/link/collision/geometry/mesh",
)
URDFParser.install_parser(
    Box,
    "robot/link/visual/geometry/box",
    "robot/link/collision/geometry/box",
    proxy_type=BoxProxy,
)
URDFParser.install_parser(
    Cylinder,
    "robot/link/visual/geometry/cylinder",
    "robot/link/collision/geometry/cylinder",
    proxy_type=CylinderProxy,
)
URDFParser.install_parser(
    Sphere,
    "robot/link/visual/geometry/sphere",
    "robot/link/collision/geometry/sphere",
    proxy_type=SphereProxy,
)
URDFParser.install_parser(
    Capsule,
    "robot/link/visual/geometry/capsule",
    "robot/link/collision/geometry/capsule",
    proxy_type=CapsuleProxy,
)

URDFParser.install_parser(Material, "robot/link/visual/material")
URDFParser.install_parser(Color, "robot/link/visual/material/color", proxy_type=ColorProxy)
URDFParser.install_parser(Texture, "robot/link/visual/material/texture")
