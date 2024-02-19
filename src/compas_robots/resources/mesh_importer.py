from compas.datastructures import Mesh

SUPPORTED_FORMATS = ("obj", "stl", "ply")


def get_file_format(url):
    # This could be much more elaborate
    # with an actual header check
    # and/or remote content-type check
    file_extension = url.split(".")[-1].lower()
    return file_extension


def mesh_import(name, file, precision=None):
    """Internal function to load meshes using the correct loader.

    Name and file might be the same but not always, e.g. temp files."""
    file_extension = get_file_format(name)

    if file_extension not in SUPPORTED_FORMATS:
        raise NotImplementedError("Mesh type not supported: {}".format(file_extension))

    if file_extension == "obj":
        return [Mesh.from_obj(file, precision)]
    elif file_extension == "stl":
        return [Mesh.from_stl(file, precision)]
    elif file_extension == "ply":
        return [Mesh.from_ply(file, precision)]

    raise Exception
