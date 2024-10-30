from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from .mesh_importer import get_file_format
from .mesh_importer import mesh_import


class AbstractMeshLoader(object):
    """Basic contract/interface for all mesh loaders."""

    def can_load_mesh(self, url):
        """Determine whether this loader can load a given Mesh URL.

        Parameters
        ----------
        url : str
            Mesh URL.

        Returns
        -------
        bool
            ``True`` if it can handle it, otherwise ``False``.
        """
        return NotImplementedError

    def load_meshes(self, url, precision=None):
        """Load meshes from the given URL.

        A single mesh file can contain multiple meshes depending on the format.

        Parameters
        ----------
        url : str
            Mesh URL
        precision: int, optional
            The precision for parsing geometric data.

        Returns
        -------
        list[:class:`~compas.datastructures.Mesh`]
            List of meshes.
        """
        return NotImplementedError


class DefaultMeshLoader(AbstractMeshLoader):
    """Handles basic mesh loader tasks, mostly from local files.

    Attributes
    ----------
    kwargs (optional): dict
        Additional keyword arguments.
    """

    def __init__(self, **kwargs):
        super(DefaultMeshLoader, self).__init__()
        self.attr = kwargs or dict()

    def can_load_mesh(self, url):
        """Determine whether this loader can load a given mesh URL.

        Parameters
        ----------
        url : str
            Mesh URL.

        Returns
        -------
        bool
            ``True`` if the URL points to a local and valid file.
            Otherwise ``False``.
        """

        url = self._get_mesh_url(url)
        scheme = urlparse(url).scheme

        # Local files have either:
        #  - no scheme
        #  - a one-letter scheme in Windows
        #  - file scheme
        is_local_file = len(scheme) in (0, 1) or scheme == "file"

        if is_local_file:
            if os.path.isfile(url):
                return True

        # Only OBJ loader supports remote files atm
        is_obj = get_file_format(url) == "obj"
        return scheme in ("http", "https") and is_obj

    def load_meshes(self, url, precision=None):
        """Load meshes from the given URL.

        A single mesh file can contain multiple meshes depending on the format.

        Parameters
        ----------
        url : str
            Mesh URL
        precision: int, optional
            The precision for parsing geometric data.

        Returns
        -------
        list[:class:`~compas.datastructures.Mesh`]
            List of meshes.
        """
        url = self._get_mesh_url(url)
        return mesh_import(url, url, precision)

    def _get_mesh_url(self, url):
        """Concatenates basepath directory to URL only if defined in the keyword arguments.
        It also strips out the scheme 'file:///' from the URL if present.

        Parameters
        ----------
        url : str
            Mesh location.

        Returns
        -------
        url: str
            Extended mesh url location if basepath in kwargs.
            Else, it returns url.
        """
        if url.startswith("file:///"):
            url = url[8:]

        basepath = self.attr.get("basepath")
        if basepath:
            return os.path.join(basepath, url)
        return url


class LocalPackageMeshLoader(AbstractMeshLoader):
    """Loads suport package resources stored locally.

    Attributes
    ----------
    path : str
        Path where the package is stored locally.
    support_package : str, optional
        Name of the support package containing URDF, Meshes
        and additional assets, e.g. 'abb_irb4400_support'.
        Default is None.
    """

    def __init__(self, path, support_package=None):
        super(LocalPackageMeshLoader, self).__init__()
        self.path = path
        self.support_package = support_package
        if not support_package:
            self.schema_prefix = "package://"
        else:
            self.schema_prefix = "package://" + self.support_package + "/"

    def build_path(self, *path_parts):
        """Returns the building path.

        Parameters
        ----------
        *path_parts: str
            The additional foldernames that construct the path.

        Returns
        -------
        str
        """
        if not self.support_package:
            return os.path.join(self.path, *path_parts)
        else:
            return os.path.join(self.path, self.support_package, *path_parts)

    def load_urdf(self, file):
        """Load a URDF file from local storage.

        Parameters
        ----------
        file : str
            File name. Following convention, the file should reside
            inside a ``urdf`` folder.
        """

        path = self.build_path("urdf", file)
        return open(path, "r")

    def can_load_mesh(self, url):
        """Determine whether this loader can load a given mesh URL.

        Parameters
        ----------
        url : str
            Mesh URL.

        Returns
        -------
        bool
            ``True`` if the URL uses the ``package://` scheme and the package name
            matches the specified in the constructor and the file exists locally,
            otherwise ``False``.
        """
        if not url.startswith(self.schema_prefix):
            return False

        local_file = self._get_local_path(url)
        return os.path.isfile(local_file)

    def load_meshes(self, url, precision=None):
        """Load meshes from the given URL.

        A single mesh file can contain multiple meshes depending on the format.

        Parameters
        ----------
        url : str
            Mesh URL
        precision: int, optional
            The precision for parsing geometric data.

        Returns
        -------
        list[:class:`~compas.datastructures.Mesh`]
            List of meshes.
        """
        local_file = self._get_local_path(url)
        return mesh_import(url, local_file, precision)

    def _get_local_path(self, url):
        _prefix, path = url.split(self.schema_prefix)
        return self.build_path(*path.split("/"))
