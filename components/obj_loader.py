import os
from PIL import Image
from .objects import *


default_vertex = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
default_normal = [0.0, 0.0, 0.0]
default_texture = [0.0, 0.0]



def get_absolute_path(cur_dir, rel_dir):
    absolute_path = os.path.abspath(os.path.join(cur_dir, rel_dir))
    return absolute_path

    
def trans_index(index, length):
    return index if index > 0 else length+index


def decode_f(args, pc_length, t_length, n_length):
    mesh_res = []
    frame_res = []
    faces =[]
    for arg in args:
        indices = arg.split('/')
        faces.append(
            [
                trans_index(int(indices[0]), pc_length) if len(indices) > 0 and len(indices[0]) > 0 else 0,
                trans_index(int(indices[1]), t_length) if len(indices) > 1 and len(indices[1]) > 0 else 0,
                trans_index(int(indices[2]), n_length) if len(indices) > 2 and len(indices[2]) > 0 else 0
            ]
        )

    for i in range(1, len(args)-1):
        mesh_res.append(faces[0])
        mesh_res.append(faces[i])
        mesh_res.append(faces[i+1])
    
    for i in range(0, len(args)):
        frame_res.append(faces[i][0])
        frame_res.append(faces[(i+1) % len(args)][0])

    return mesh_res, frame_res


def decode_l(args, pc_length):
    vs = list(map(lambda v: trans_index(int(v), pc_length), args))
    res = []
    for i in range(len(args)-1):
        res.append(vs[i])
        res.append(vs[i+1])
    return res


def import_mtl(mtl_file_path):
    materials = {}
    current_material = None

    with open(mtl_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if not parts:
                continue

            if parts[0] == 'newmtl':
                if current_material is not None:
                    materials[current_material.name] = current_material
                current_material = GLMaterial(name=parts[1])
            elif current_material:
                if parts[0] == 'Ka':
                    current_material.ambient = tuple(map(float, parts[1:]))
                elif parts[0] == 'Kd':
                    current_material.diffuse = tuple(map(float, parts[1:]))
                elif parts[0] == 'Ks':
                    current_material.specular = tuple(map(float, parts[1:]))
                elif parts[0] == 'Ns':
                    current_material.shininess = float(parts[1])
                elif parts[0] == 'map_Kd':
                    # create texture
                    texture1 = glGenTextures(1)             # create texture object
                    glBindTexture(GL_TEXTURE_2D, texture1)  # activate texture1 as GL_TEXTURE_2D

                    # set texture filtering parameters - skip at this moment
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
                    try:
                        img_math = get_absolute_path(os.path.dirname(mtl_file_path), parts[1])
                        extension = parts[1].split('.')[-1]
                        img = Image.open(img_math)
                        img = img.transpose(Image.FLIP_TOP_BOTTOM)

                        if extension == 'jpg':
                            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img.tobytes())
                        elif extension == 'png':
                            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())
                        current_material.texture = texture1
                        print("Loaded", parts[1])
                    except:
                        print("Failed to load texture:", img_math)

        if current_material is not None:
            materials[current_material.name] = current_material

    return materials


def import_obj(path, log=False, color=[1.0, 1.0, 1.0]):
    with open(path, "r") as file:
        if log:
            print("Obj file name:", os.path.split(path)[-1])
        obj = file.read()


    global default_vertex
    default_vertex = [0, 0, 0]

    vertices = [default_vertex]
    textures = [default_texture]
    normals = [default_normal]
    faces, lines, frame = [], [], []

    materials = {}
    usemtl = []

    face_cnt = 0
    tri_cnt = 0

    for line in obj.split('\n'):
        if len(line.strip()) == 0:
            continue
        prefix, args = (line+' ').split(' ', maxsplit=1)
        args = args.strip().split(' ')
        
        if prefix == 'mtllib':
            mtpath = get_absolute_path(os.path.dirname(path), ' '.join(args))
            try:
                materials = import_mtl(mtpath)
            except:
                print('Failed to load:', mtpath)

        if prefix == 'usemtl':
            usemtl.append((len(faces), materials.get(args[0])))
        
        elif prefix == 'v':
            vertices.append(list(map(float, args)))

        elif prefix == 'vn':
            normals.append(list(map(float, args)))
        
        elif prefix == 'vt':
            textures.append(list(map(float, args[:2])))

        elif prefix == 'f':
            face_cnt += 1
            tri_cnt += len(args)-2
            face_vertices, face_frame = decode_f(args, len(vertices), len(textures), len(normals))
            faces.extend(face_vertices)
            frame.extend(face_frame)

        elif prefix == 'l':
            lines.extend(decode_l(args, len(vertices)))

    if log:
        print("Number of faces:", face_cnt)
        print("Number of triangles:", tri_cnt)

    return GLObject(
        mesh = GLMesh(
            vertices = glm.array(glm.float32, *np.array(vertices).flatten()),
            normals = glm.array(glm.float32, *np.array(normals).flatten()),
            textures = glm.array(glm.float32, *np.array(textures).flatten()),
            
            faces = glm.array(glm.uint32, *np.array(faces).flatten()),
            lines = glm.array(glm.uint32, *lines),
            frame = glm.array(glm.uint32, *frame),
            usemtl = usemtl,
        )
    )

    