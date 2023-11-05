import os
from .objects import *

default_vertex = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
default_normal = [0.0, 0.0, 0.0]
default_texture = [0.0, 0.0]

def fit_to_default(info, default):
    if len(info) < len(default):
        return info + default[len(info):]
    else:
        return info
    
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
                #trans_index(int(indices[1]), t_length) if len(indices) > 1 and len(indices[1]) > 0 else 0,
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


def import_obj(path, log=False, color=[1.0, 1.0, 1.0]):
    with open(path, "r") as file:
        if log:
            print("Obj file name:", os.path.split(path)[-1])
        obj = file.read()

    global default_vertex
    default_vertex = [0, 0, 0] + color

    vertices = [default_vertex]
    textures = [default_texture]
    normals = [default_normal]
    faces, lines, frame = [], [], []

    face_cnt = 0
    face_3v_cnt = 0
    face_4v_cnt = 0
    face_gt4v_cnt = 0

    for line in obj.split('\n'):
        if len(line.strip()) == 0:
            continue
        prefix, args = (line+' ').split(' ', maxsplit=1)
        args = args.strip().split(' ')
        
        if prefix == 'v':
            vertices.append(fit_to_default(list(map(float, args)), default_vertex))

        elif prefix == 'vn':
            normals.append(list(map(float, args)))
        
        elif prefix == 'vt':
            textures.append(list(map(float, args)))

        elif prefix == 'f':
            face_cnt += 1
            if len(args) == 3:
                face_3v_cnt += 1
            elif len(args) == 4:
                face_4v_cnt += 1
            else:
                face_gt4v_cnt += 1

            face_vertices, face_frame = decode_f(args, len(vertices), len(textures), len(normals))
            faces.extend(face_vertices)
            frame.extend(face_frame)

        elif prefix == 'l':
            lines.extend(decode_l(args, len(vertices)))

    if log:
        print("Total number of faces:", face_cnt)

    return GLObject(
        mesh = GLMesh(
            vertices = glm.array(glm.float32, *np.array(vertices).flatten()),
            normals = glm.array(glm.float32, *np.array(normals).flatten()),
            faces = glm.array(glm.uint32, *np.array(faces).flatten()),
            lines = glm.array(glm.uint32, *lines),
            frame = glm.array(glm.uint32, *frame) # For wireframe mode
        )
    )

    