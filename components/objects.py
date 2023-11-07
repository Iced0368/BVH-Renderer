from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

from dataclasses import dataclass

DRAW_MESH = 1 << 0
DRAW_WIREFRAME = 1 << 1
DRAW_SHADELESS = 1 << 2



def prepare_vao_face(vertices, normals, textures, faces, materials):
    if vertices is None:
        return None
    
    vertex_dict = {}
    vertices_combined = []
    faces_combined = []

    for i in range(0, len(faces), 3):
        face = [faces[i], faces[i+1], faces[i+2]] #vertex, texture, normal

        index_hash = ','.join(list(map(str, face)))

        face_index = vertex_dict.get(index_hash)
        
        if face_index is None:
            vertex_dict[index_hash] = len(vertices_combined)
            faces_combined.append(len(vertices_combined))

            if textures is not None:
                vertices_combined.append([
                    *vertices[3*face[0] : 3*(face[0]+1)], 
                    *textures[2*face[1] : 2*(face[1]+1)],
                    *normals[3*face[2] : 3*(face[2]+1)],
                ])
            else:
                vertices_combined.append([
                    *vertices[3*face[0] : 3*(face[0]+1)], 
                    0, 0,
                    *normals[3*face[2] : 3*(face[2]+1)],
                ])
        else:
            faces_combined.append(face_index)

    vertices_combined = glm.array(glm.float32, *np.array(vertices_combined).flatten())

    # create and activate VBO (vertex buffer object)
    VBO_vertex = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO_vertex)  # activate VBO as a vertex buffer object
    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices_combined.nbytes, vertices_combined.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer


    VAOs = []
    face_lengths = []
    
    for material in materials:
        s, e = material[1]
        if s == e:
            continue

        _faces_combined = glm.array(glm.uint32, *faces_combined[s:e])
        
        # create and activate VAO (vertex array object)
        VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
        glBindVertexArray(VAO)      # activate VAO

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8*glm.sizeof(glm.float32), None)
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8*glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(1)

        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8*glm.sizeof(glm.float32), ctypes.c_void_p(5*glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(2)
    
        # indexing
        EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, _faces_combined.nbytes, _faces_combined.ptr, GL_STATIC_DRAW)

        glBindVertexArray(0)

        VAOs.append(VAO)
        face_lengths.append(e-s)
    
    return VAOs, face_lengths


def prepare_vao_line(vertices, lines):
    if vertices is None:
        return None

    # create and activate VAO (vertex array object)
    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)      # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO_vertex = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO_vertex)  # activate VBO as a vertex buffer object
    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3*glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # indexing
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, lines.nbytes, lines.ptr, GL_STATIC_DRAW)

    glBindVertexArray(0)
    
    return VAO


@dataclass
class GLMaterial:
    name: str = ''
    ambient: tuple = (1.0, 1.0, 1.0)
    diffuse: tuple = (1.0, 1.0, 1.0)
    specular: tuple = (1.0, 1.0, 1.0)
    shininess: float = 16.0
    disffuse_map: int = None
    normal_map: int = None

    def apply(self, uniform_locs, ignore_light):
        if self.disffuse_map is not None:
            glActiveTexture(GL_TEXTURE0)
            glUniform1i(uniform_locs['useDiffuseMap'], 1)
            glBindTexture(GL_TEXTURE_2D, self.disffuse_map)
        else:
            glUniform1i(uniform_locs['useDiffuseMap'], 0)

        if self.normal_map is not None:
            glActiveTexture(GL_TEXTURE1)
            glUniform1i(uniform_locs['useNormalMap'], 1)
            glBindTexture(GL_TEXTURE_2D, self.normal_map)
        else:
            glUniform1i(uniform_locs['useNormalMap'], 0)

        if ignore_light:
            return

        glUniform3f(uniform_locs['Ka'], *self.ambient)
        glUniform3f(uniform_locs['Kd'], *self.diffuse)
        glUniform3f(uniform_locs['Ks'], *self.specular)
        glUniform1f(uniform_locs['Ns'], self.shininess)




class GLMesh:
    def __init__(self, vertices=None, normals=None, textures=None, faces=None, lines=None, frame=None, usemtl=[]):
        self.vertices = vertices
        self.normals = normals
        self.textures = textures

        self.faces = faces
        self.lines = lines
        self.frame = frame

        self.materials = None
        if faces is not None:
            materials = [[None, [0, -1]]]
            for mtl in usemtl:
                if materials[-1][1][0] == mtl[0]:
                    materials.pop()
                else:
                    materials[-1][1][1] = mtl[0]
                materials.append([mtl[1], [mtl[0], -1]])
            materials[-1][1][1] = len(faces)
            self.materials = materials

        self.vao_faces_list = None
        self.face_lengths = None
        self.vao_lines = None
        self.vao_frame = None
                
    def prepare(self):
        if self.faces is not None:      
            self.vao_faces_list, self.face_lengths = prepare_vao_face(self.vertices, self.normals, self.textures, self.faces, self.materials)
        
        if self.lines is not None:
            self.vao_lines = prepare_vao_line(self.vertices, self.lines)

        if self.frame is not None:
            self.vao_frame = prepare_vao_line(self.vertices, self.frame)


class GLObject:
    def __init__(self, parent=None, link_transform=None, shape_transform=None, mesh=None):
        self.parent = parent
        self.children = set()
        if parent is not None:
            parent.children.add(self)
        
        self.shape_transform = shape_transform if shape_transform is not None else glm.mat4()
        self.link_transform = link_transform if link_transform is not None else glm.mat4()
        self.joint_transform = glm.mat4()
        self.global_transform = glm.mat4()

        self.mesh = mesh


    def update_tree_global_transform(self):
        if self.parent is not None:
            self.global_transform = self.parent.global_transform * self.link_transform * self.joint_transform
        else:
            self.global_transform = self.link_transform * self.joint_transform

        for child in self.children:
            child.update_tree_global_transform()

    def get_global_transform(self):
        return self.global_transform
    def get_shape_transform(self):
        return self.shape_transform
    def get_mesh(self):
        return self.mesh
    def set_transform(self, shape_transform=None, joint_transform=None, link_transform=None):
        if shape_transform is not None:
            self.shape_transform = shape_transform
        if joint_transform is not None:
            self.joint_transform = joint_transform
        if link_transform is not None:
            self.link_transform = link_transform
    
    def set_parent(self, parent):
        if self.parent is not None:
            self.parent.children.remove(self)
        self.parent = parent
        if parent is not None:
            parent.children.add(self)


    def prepare(self):
        if self.mesh is not None:
            self.mesh.prepare()

    def Draw(self, VP, uniform_locs, ignore_light, mode, color=(1, 1, 1)):
        if self.mesh is None:
            return
        mesh = self.get_mesh()

        M = self.get_global_transform() * self.get_shape_transform()
        MVP = VP * M

        glUniformMatrix4fv(uniform_locs['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
        glUniformMatrix4fv(uniform_locs['M'], 1, GL_FALSE, glm.value_ptr(M))
        glUniform3f(uniform_locs['mesh_color'], *color)
        glUniform3f(uniform_locs['Ka'], 1, 1, 1)
        glUniform3f(uniform_locs['Kd'], 1, 1, 1)

        if mesh.vao_faces_list is not None and mode & DRAW_MESH:
            glUniform1i(uniform_locs['ignore_light'], ignore_light)

            for i in range(len(mesh.vao_faces_list)):
                vao_faces = mesh.vao_faces_list[i]
                face_length = mesh.face_lengths[i]
                glBindVertexArray(vao_faces)

                mtl = mesh.materials[i][0]
                if mtl is not None:
                    mtl.apply(uniform_locs, ignore_light)
                else:
                    GLMaterial().apply(uniform_locs, ignore_light)
            
                glDrawElements(GL_TRIANGLES, face_length, GL_UNSIGNED_INT, None)

        if mesh.vao_lines is not None and mode & DRAW_MESH:
            glBindVertexArray(mesh.vao_lines)
            glDrawElements(GL_LINES, len(mesh.lines), GL_UNSIGNED_INT, None)

        glUniform1i(uniform_locs['ignore_light'], 1)
        glUniform1i(uniform_locs['useDiffuseMap'], 0)
        glUniform1i(uniform_locs['useNormalMap'], 0)

        if mesh.vao_frame is not None and mode & DRAW_WIREFRAME:
            glBindVertexArray(mesh.vao_frame)
            glDrawElements(GL_LINES, len(mesh.frame), GL_UNSIGNED_INT, None)
        
