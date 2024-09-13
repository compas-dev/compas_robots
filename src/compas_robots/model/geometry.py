from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas
import compas.geometry
from compas.colors import Color
from compas.data import Data
from compas.datastructures import Mesh
from compas.geometry import Frame

from compas_robots.files import URDFElement
from compas_robots.model.base import ColorProxy

from .base import ProxyObject
from .base import _attr_from_data
from .base import _attr_to_data
from .base import _parse_floats


class BoxProxy(ProxyObject):
    """Proxy class that adds URDF functionality to an instance of :class:`~compas.geometry.Box`.

    This class is internal and not intended to be referenced externally.
    """

    def get_urdf_element(self):
        attributes = {"size": "{} {} {}".format(*self.size)}
        return URDFElement("box", attributes)

    @classmethod
    def from_urdf(cls, attributes, elements=None, text=None):
        xsize, ysize, zsize = _parse_floats(attributes["size"])
        return cls(compas.geometry.Box(xsize, ysize, zsize, Frame.worldXY()))

    @property
    def meshes(self):
        return [Mesh.from_shape(self)]

    @property
    def size(self):
        return [self.xsize, self.ysize, self.zsize]


class CylinderProxy(ProxyObject):
    """Proxy class that adds URDF functionality to an instance of :class:`~compas.geometry.Cylinder`.

    This class is internal and not intended to be referenced externally.
    """

    def get_urdf_element(self):
        attributes = {"radius": self.radius, "length": self.length}
        return URDFElement("cylinder", attributes)

    @classmethod
    def from_urdf(cls, attributes, elements=None, text=None):
        radius = float(attributes["radius"])
        length = float(attributes["length"])
        frame = compas.geometry.Frame.worldXY()
        return cls(compas.geometry.Cylinder(radius=radius, height=length, frame=frame))

    @property
    def meshes(self):
        return [Mesh.from_shape(self)]

    @property
    def length(self):
        return self.height


class SphereProxy(ProxyObject):
    """Proxy class that adds URDF functionality to an instance of :class:`~compas.geometry.Sphere`.

    This class is internal and not intended to be referenced externally.
    """

    def get_urdf_element(self):
        attributes = {"radius": self.radius}
        return URDFElement("sphere", attributes)

    @classmethod
    def from_urdf(cls, attributes, elements=None, text=None):
        radius = float(attributes["radius"])
        return cls(compas.geometry.Sphere(radius, frame=compas.geometry.Frame.worldXY()))

    @property
    def meshes(self):
        return [Mesh.from_shape(self)]


class CapsuleProxy(ProxyObject):
    """Proxy class that adds URDF functionality to an instance of :class:`~compas.geometry.Capsule`.

    This class is internal and not intended to be referenced externally.
    """

    def get_urdf_element(self):
        attributes = {"radius": self.radius, "length": self.length}
        return URDFElement("capsule", attributes)

    @classmethod
    def from_urdf(cls, attributes, elements=None, text=None):
        radius = float(attributes["radius"])
        length = float(attributes["length"])
        frame = compas.geometry.Frame.worldXY()
        return cls(compas.geometry.Capsule(radius=radius, height=length, frame=frame))

    @property
    def meshes(self):
        return [Mesh.from_shape(self)]


class MeshDescriptor(Data):
    """Description of a mesh.

    Parameters
    ----------
    filename : str
        The mesh' filename.
    scale : str, optional
        The scale factors of the mesh in the x-, y-, and z-direction.
    **kwargs : dict[str, Any], optional
        The keyword arguments (kwargs) collected in a dict.
        These allow using non-standard attributes absent in the URDF specification.

    Attributes
    ----------
    filename : str
        The mesh' filename.
    scale : [float, float, float]
        The scale factors of the mesh in the x-, y-, and z-direction.
    meshes : list[:class:`~compas.datastructures.Mesh`]
        List of COMPAS geometric meshes.

    Examples
    --------
    >>> m = MeshDescriptor('link.stl')

    """

    def __init__(self, filename, scale="1.0 1.0 1.0", **kwargs):
        super(MeshDescriptor, self).__init__()
        self.filename = filename
        self.scale = _parse_floats(scale)
        self.meshes = []
        self.attr = kwargs or {}

    def get_urdf_element(self):
        attributes = {"filename": self.filename}
        # There is no need to record default values.  Usually these
        # coincide with some form of 0 and are filtered out with
        # `attributes = dict(filter(lambda x: x[1], attributes.items()))`,
        # but here we must be explicit.
        if self.scale != [1.0, 1.0, 1.0]:
            attributes["scale"] = "{} {} {}".format(*self.scale)
        attributes.update(self.attr)
        return URDFElement("mesh", attributes)

    @property
    def __data__(self):
        return {
            "filename": self.filename,
            "scale": self.scale,
            "attr": _attr_to_data(self.attr),
            "meshes": self.meshes,
        }

    @classmethod
    def __from_data__(cls, data):
        attr = _attr_from_data(data.get("attr", {}))
        md = cls(
            data["filename"],
            scale="{} {} {}".format(
                data["scale"][0],
                data["scale"][1],
                data["scale"][2],
            ),
            **attr
        )
        md.meshes = data["meshes"]
        return md


class Texture(Data):
    """Texture description.

    Parameters
    ----------
    filename : str
        The filename of the texture.

    Attributes
    ----------
    filename : str
        The filename of the texture.

    Examples
    --------
    >>> t = Texture('wood.jpg')

    """

    def __init__(self, filename):
        super(Texture, self).__init__()
        self.filename = filename

    def get_urdf_element(self):
        attributes = {"filename": self.filename}
        return URDFElement("texture", attributes)

    @property
    def __data__(self):
        return {
            "filename": self.filename,
        }


class Material(Data):
    """Material description.

    Parameters
    ----------
    name : str
        The name of the material.
    color : :class:`~compas.colors.Color`, optional
        The color of the material.
    texture : :class:`~compas_robots.model.Texture`, optional
        The filename of the texture.

    Examples
    --------
    >>> c = Color(1, 0, 0)
    >>> material = Material('wood', c)

    >>> material = Material('aqua')
    >>> material.get_color()
    Color(0.0, 1.0, 1.0, alpha=1.0)

    """

    def __init__(self, name=None, color=None, texture=None):
        super(Material, self).__init__()
        self.name = name
        self.color = color
        self.texture = texture

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value is None:
            self._color = None
            return

        if isinstance(value, compas.colors.Color):
            self._color = ColorProxy.create_proxy(value)
        else:
            self._color = value

    def get_urdf_element(self):
        attributes = {"name": self.name}
        elements = [self.color, self.texture]
        return URDFElement("material", attributes, elements)

    @property
    def __data__(self):
        return {
            "name": self.name,
            "color": self.color.__data__ if self.color else None,
            "texture": self.texture.__data__ if self.texture else None,
        }

    @classmethod
    def __from_data__(cls, data):
        return cls(
            name=data["name"],
            color=Color.__from_data__(data["color"]) if data["color"] else None,
            texture=Texture.__from_data__(data["texture"]) if data["texture"] else None,
        )

    def get_color(self):
        """Get the RGBA color array of the material.

        Returns
        -------
        :class:`~compas.colors.Color`
            Color of the material.

        Examples
        --------
        >>> material = Material('aqua')
        >>> material.get_color()
        Color(0.0, 1.0, 1.0, alpha=1.0)

        """
        if self.name:
            try:
                return Color.from_name(self.name)
            except ValueError:
                pass

        if self.color:
            return Color(*self.color.rgba)

        return None


class LinkGeometry(Data):
    """Geometrical description of the shape of a link.

    Parameters
    ----------
    box : :class:`~compas.geometry.Box`, optional
        A box shape primitive.
    cylinder : :class:`~compas.geometry.Cylinder`, optional
        A cylinder shape primitive.
    sphere : :class:`~compas.geometry.Sphere`, optional
        A sphere shape primitive.
    capsule : :class:`~compas.geometry.Capsule`, optional
        A capsule shape primitive.
    mesh : :class:`~compas_robots.model.MeshDescriptor`, optional
        A descriptor of a mesh.
    **kwargs : dict[str, Any], optional
        The keyword arguments (kwargs) collected in a dict.
        These allow using non-standard attributes absent in the URDF specification.

    Attributes
    ----------
    shape : object
        The shape of the geometry
    attr : keyword arguments
        Additional attributes

    Examples
    --------
    >>> box = compas.geometry.Box(1)
    >>> geo = LinkGeometry(box=box)

    """

    def __init__(self, box=None, cylinder=None, sphere=None, capsule=None, mesh=None, **kwargs):
        super(LinkGeometry, self).__init__()
        self.shape = box or cylinder or sphere or capsule or mesh
        self.attr = kwargs

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        if value is None:
            self._shape = None
            return

        if isinstance(value, compas.geometry.Box):
            self._shape = BoxProxy.create_proxy(value)
        elif isinstance(value, compas.geometry.Cylinder):
            self._shape = CylinderProxy.create_proxy(value)
        elif isinstance(value, compas.geometry.Sphere):
            self._shape = SphereProxy.create_proxy(value)
        elif isinstance(value, compas.geometry.Capsule):
            self._shape = CapsuleProxy.create_proxy(value)
        else:
            self._shape = value

        if "meshes" not in dir(self._shape):
            raise TypeError("Shape implementation does not define a meshes accessor: {}".format(type(self._shape)))

    def get_urdf_element(self):
        attributes = self.attr.copy()
        elements = [self.shape]
        return URDFElement("geometry", attributes, elements)

    @property
    def __data__(self):
        return {
            "shape": self.shape,  # type: ignore
            "attr": _attr_to_data(self.attr),
        }

    @classmethod
    def __from_data__(cls, data):
        geo = cls(box=compas.geometry.Box(1))
        geo.shape = data["shape"]
        geo.attr = _attr_from_data(data["attr"])
        return geo

    @staticmethod
    def _get_item_meshes(item):
        meshes = item.geometry.shape.meshes

        if meshes:
            # Coerce meshes into an iterable (a tuple if not natively iterable)
            if not hasattr(meshes, "__iter__"):
                meshes = (meshes,)

        return meshes
