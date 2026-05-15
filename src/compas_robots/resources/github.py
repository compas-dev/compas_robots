from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.request import urlopen

from .basic import AbstractMeshLoader
from .mesh_importer import mesh_import

if TYPE_CHECKING:
    from typing import Optional

    from compas.datastructures import Mesh


class GithubPackageMeshLoader(AbstractMeshLoader):
    """Loads resources stored in Github.

    Attributes
    ----------
    repository : str
        Repository name including organization,
        e.g. `ros-industrial/abb`.
    support_package : str
        Name of the support package containing URDF, Meshes
        and additional assets, e.g. `abb_irb4400_support`
    branch : str
        Branch name, defaults to `main`.
    relative_path : str
        Relative path of the support package within the repository.
        If the repository itself is the support package, set
        `relative_path` to `'.'`.  Defaults to `support_package`
    """

    HOST = "https://raw.githubusercontent.com"

    def __init__(self, repository: str, support_package: str, branch: str = "main", relative_path: Optional[str] = None) -> None:
        super(GithubPackageMeshLoader, self).__init__()
        self.repository = repository
        self.support_package = support_package
        self.branch = branch
        self.schema_prefix = "package://" + self.support_package + "/"
        self.relative_path = support_package if relative_path is None else relative_path

    def build_url(self, file: str) -> str:
        """Returns the corresponding url of the file.

        Parameters
        ----------
        file
            File name. Following convention, the file should reside
            inside a `urdf` folder.

        Returns
        -------
        The file's url.
        """
        relative_path_component = None if self.relative_path == "." else self.relative_path
        url_components = [
            GithubPackageMeshLoader.HOST,
            self.repository,
            self.branch,
            relative_path_component,
            file,
        ]
        return "/".join(filter(None, url_components))

    def load_urdf(self, file: str):
        """Load a URDF file from a Github support package repository.

        Parameters
        ----------
        file
            File name. Following convention, the file should reside
            inside a `urdf` folder.
        """
        url = self.build_url("urdf/{}".format(file))
        return urlopen(url)

    def can_load_mesh(self, url: str) -> bool:
        """Determine whether this loader can load a given mesh URL.

        Parameters
        ----------
        url
            Mesh URL.

        Returns
        -------
        bool
            `True` if the URL uses the `package://` scheme and the package name
            matches the specified in the constructor, otherwise `False`.
        """
        return url.startswith(self.schema_prefix)

    def load_meshes(self, url: str, precision: Optional[int] = None) -> list[Mesh]:
        """Load meshes from the given URL.

        A single mesh file can contain multiple meshes depending on the format.

        Parameters
        ----------
        url
            Mesh URL
        precision
            The precision for parsing geometric data.

        Returns
        -------
        List of meshes.
        """
        _prefix, path = url.split(self.schema_prefix)
        url = self.build_url(path)

        return mesh_import(url, url, precision)
