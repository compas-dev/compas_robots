import logging
from collections import OrderedDict

from compas.datastructures import Mesh
from compas.files import XML
from compas.geometry import Transformation
from compas.tolerance import TOL

LOGGER = logging.getLogger(__file__)

SUPPORTED_FORMATS = ("obj", "stl", "ply", "dae")


def _xml_namespace(tag):
    if tag.startswith("{"):
        return tag[1:].split("}", 1)[0]
    return None


def _xml_tag(name, namespace=None):
    if namespace:
        return "{{{}}}{}".format(namespace, name)
    return name


def _xml_local_name(tag):
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[1]
    return tag


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
    elif file_extension == "dae":
        return _meshes_from_collada(file, precision)

    raise Exception


def _meshes_from_collada(filename, precision):
    """This is a very simple implementation of a DAE/Collada parser.

    Collada specification: https://www.khronos.org/files/collada_spec_1_5.pdf
    """
    dae = XML.from_file(filename)
    meshes = []
    namespace = _xml_namespace(dae.root.tag)

    def tag(name):
        return _xml_tag(name, namespace)

    visual_scenes = dae.root.find(tag("library_visual_scenes"))
    materials = dae.root.find(tag("library_materials"))
    effects = dae.root.find(tag("library_effects"))

    for geometry in dae.root.findall("{}/{}".format(tag("library_geometries"), tag("geometry"))):
        mesh_xml = geometry.find(tag("mesh"))
        mesh_id = geometry.attrib["id"]
        matrix_node = None
        transform = None

        if visual_scenes is not None:
            for node in visual_scenes.findall(".//{}".format(tag("node"))):
                instance_geometry = node.find('{}[@url="#{}"]'.format(tag("instance_geometry"), mesh_id))
                if instance_geometry is not None:
                    matrix_node = node.find(tag("matrix"))
                    break

        if matrix_node is not None:
            M = [float(i) for i in matrix_node.text.split()]

            # If it's the identity matrix, then ignore, we don't need to transform it
            if M != [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]:
                M = M[0:4], M[4:8], M[8:12], M[12:16]
                transform = Transformation.from_matrix(M)

        # primitive elements can be any combination of:
        # lines, linestrips, polygons, polylist, triangles, trifans, tristrips
        # The current implementation only supports triangles and polylist of triangular meshes
        primitive_element_sets = []
        primitive_element_sets.extend(mesh_xml.findall(tag("triangles")))
        primitive_element_sets.extend(mesh_xml.findall(tag("polylist")))

        if len(primitive_element_sets) == 0:
            raise Exception("No primitive elements found (currently only triangles and polylist are supported)")

        for primitive_element_set in primitive_element_sets:
            primitive_tag = _xml_local_name(primitive_element_set.tag)
            primitive_set_data = primitive_element_set.find(tag("p")).text.split()
            primitive_count = int(primitive_element_set.attrib["count"])

            # Try to retrieve mesh colors
            mesh_colors = {}

            if materials is not None and effects is not None:
                try:
                    instance_effect = None
                    material_id = primitive_element_set.attrib.get("material")

                    if material_id is not None:
                        instance_effect = materials.find('{}[@id="{}"]/{}'.format(tag("material"), material_id, tag("instance_effect")))

                    if instance_effect is not None:
                        instance_effect_id = instance_effect.attrib["url"][1:]
                        effect = effects.find('{}[@id="{}"]'.format(tag("effect"), instance_effect_id))
                        phong = effect.find("{}/{}/{}".format(tag("profile_COMMON"), tag("technique"), tag("phong")))
                        colors = phong.findall(".//{}".format(tag("color")))
                        for color_node in colors:
                            rgba = [float(i) for i in color_node.text.split()]
                            if "sid" in color_node.attrib:
                                mesh_colors["mesh_color.{}".format(color_node.attrib["sid"])] = rgba
                except Exception:
                    LOGGER.exception("Exception while loading materials, all materials of mesh file %s will be ignored ", filename)

            # Parse vertices
            all_offsets = sorted([int(i.attrib["offset"]) for i in primitive_element_set.findall("{}[@offset]".format(tag("input")))])
            if not all_offsets:
                raise Exception("Primitive element node does not contain offset information! Primitive tag={}".format(primitive_tag))

            vertices_input = primitive_element_set.find('{}[@semantic="VERTEX"]'.format(tag("input")))
            vertices_id = vertices_input.attrib["source"][1:]
            vertices_link = mesh_xml.find('{}[@id="{}"]/{}'.format(tag("vertices"), vertices_id, tag("input")))
            positions = mesh_xml.find('{}[@id="{}"]/{}'.format(tag("source"), vertices_link.attrib["source"][1:], tag("float_array")))
            positions = positions.text.split()

            vertices = [[float(p) for p in positions[i : i + 3]] for i in range(0, len(positions), 3)]

            # Parse faces
            # Every nth element is a vertex key, we ignore the rest based on the offsets defined
            # Usually, every second item is the normal, but there can be other items offset in there (vertex tangents, etc)
            skip_step = 1 + all_offsets[-1]

            if primitive_tag == "triangles":
                vcount = [3] * primitive_count
            elif primitive_tag == "polylist":
                vcount = [int(v) for v in primitive_element_set.find(tag("vcount")).text.split()]

            if len(vcount) != primitive_count:
                raise Exception("Primitive count does not match vertex per face count, vertex input id={}".format(vertices_id))

            fkeys = [int(f) for f in primitive_set_data[::skip_step]]
            faces = []
            for i in range(primitive_count):
                a = i * vcount[i]
                b = a + vcount[i]
                faces.append(fkeys[a:b])

            # Rebuild vertices and faces using the same logic that other importers
            # use remapping everything based on a selected precision
            index_key = OrderedDict()
            vertex = OrderedDict()

            for i, xyz in enumerate(vertices):
                key = TOL.geometric_key(xyz, precision)
                index_key[i] = key
                vertex[key] = xyz

            key_index = {key: index for index, key in enumerate(vertex)}
            index_index = {index: key_index[key] for index, key in iter(index_key.items())}
            vertices = [xyz for xyz in iter(vertex.values())]
            faces = [[index_index[index] for index in face] for face in faces]

            mesh = Mesh.from_vertices_and_faces(vertices, faces)

            if mesh_colors:
                mesh.attributes.update(mesh_colors)

            if transform:
                mesh.transform(transform)

            meshes.append(mesh)

    return meshes
