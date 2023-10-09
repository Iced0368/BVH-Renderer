from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

DRAW_MESH = 1 << 0
DRAW_WIREFRAME = 1 << 1
DRAW_SHADELESS = 1 << 2


def prepare_vao_face(vertices, normals, faces):
    if vertices is None:
        return None
    
    vertex_dict = {}
    vertices_combined = []
    faces_combined = []
    for i in range(0, len(faces), 2):
        face = [faces[i], faces[i+1]]
        index_hash = face[0] * (len(normals) // 3) + face[1]
        face_index = vertex_dict.get(index_hash)
        if face_index is None:
            vertex_dict[index_hash] = len(vertices_combined)
            faces_combined.append(len(vertices_combined))
            vertices_combined.append([
                *vertices[6*face[0] : 6*(face[0]+1)], 
                *normals[3*face[1] : 3*(face[1]+1)]
            ])
        else:
            faces_combined.append(face_index)

    vertices_combined = glm.array(glm.float32, *np.array(vertices_combined).flatten())
    faces_combined = glm.array(glm.uint32, *faces_combined)


    # create and activate VAO (vertex array object)
    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)      # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO_vertex = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO_vertex)  # activate VBO as a vertex buffer object
    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices_combined.nbytes, vertices_combined.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9*glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9*glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9*glm.sizeof(glm.float32), ctypes.c_void_p(6*glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(2)

    # indexing
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, faces_combined.nbytes, faces_combined.ptr, GL_STATIC_DRAW)

    glBindVertexArray(0)
    
    return VAO


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
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6*glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6*glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    # indexing
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, lines.nbytes, lines.ptr, GL_STATIC_DRAW)

    glBindVertexArray(0)
    
    return VAO


class GLMesh:
    def __init__(self, vertices=None, normals=None, faces=None, lines=None, frame=None):
        self.vertices = vertices
        self.normals = normals
        self.faces = faces
        self.lines = lines
        self.frame = frame

        self.vao_faces = None
        self.vao_lines = None
        self.vao_frame = None
                
    def prepare(self):
        if self.faces is not None:
            self.vao_faces = prepare_vao_face(self.vertices, self.normals, self.faces)
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

    def Draw(self, VP, uniform_locs, ambient, diffuse, specular, ignore_light, mode):
        if self.mesh is None:
            return
        mesh = self.get_mesh()
        M = self.get_global_transform() * self.get_shape_transform()
        MVP = VP * M

        glUniformMatrix4fv(uniform_locs['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
        glUniformMatrix4fv(uniform_locs['M'], 1, GL_FALSE, glm.value_ptr(M))

        if mesh.vao_faces is not None and mode & DRAW_MESH:
            glUniform3f(uniform_locs['light_coeff'], ambient, diffuse, specular)
            glUniform1i(uniform_locs['ignore_light'], ignore_light)
            glBindVertexArray(mesh.vao_faces)
            glDrawElements(GL_TRIANGLES, len(mesh.faces), GL_UNSIGNED_INT, None)

        if mesh.vao_lines is not None and mode & DRAW_MESH:
            glUniform1i(uniform_locs['ignore_light'], 1)
            glBindVertexArray(mesh.vao_lines)
            glDrawElements(GL_LINES, len(mesh.lines), GL_UNSIGNED_INT, None)

        if mesh.vao_frame is not None and mode & DRAW_WIREFRAME:
            glUniform1i(uniform_locs['ignore_light'], 1)
            glBindVertexArray(mesh.vao_frame)
            glDrawElements(GL_LINES, len(mesh.frame), GL_UNSIGNED_INT, None)
        
