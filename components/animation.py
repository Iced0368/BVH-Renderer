import numpy as np
from .objects import *

default_color = [0.7, 0.7, 1]

def calculate_rotation_matrix(p):
    if p == glm.vec3(0, 0, 0):
        return glm.mat4()
    
    eps = 1e-6
    up_vector = glm.vec3(0, 1, 0)
    p = glm.normalize(p)

    axis = glm.cross(up_vector, p)
    dot_product = glm.dot(up_vector, p)
    
    if abs(dot_product-1) < eps:
        return glm.mat4()
    if abs(dot_product+1) < eps:
        return glm.mat4(
            1, 0, 0, 0,
            0, -1, 0, 0,
            0, 0, -1, 0,
            0, 0, 0, 1
        )

    angle = glm.acos(dot_product)

    return glm.rotate(angle, axis)


joint_transform = {
    'XPOSITION': lambda x : glm.translate((x, 0, 0)),
    'YPOSITION': lambda y : glm.translate((0, y, 0)),
    'ZPOSITION': lambda z : glm.translate((0, 0, z)),
    'XROTATION': lambda t : glm.rotate(glm.radians(t), (1, 0, 0)),
    'YROTATION': lambda t : glm.rotate(glm.radians(t), (0, 1, 0)),
    'ZROTATION': lambda t : glm.rotate(glm.radians(t), (0, 0, 1)),
}


class SkeletonMesh(GLMesh):
    def __init__(self, enable_box=True):
        super().__init__(
            vertices = glm.array(glm.float32,
                -0.5,  0.9, -0.5,
                -0.5,  0.9,  0.5,
                 0.5,  0.9,  0.5,
                 0.5,  0.9, -0.5,
                -0.5,  0, -0.5,
                -0.5,  0,  0.5,
                 0.5,  0,  0.5,
                 0.5,  0, -0.5,

                 0, 0, 0,
                 0, 1, 0,
            ),
            normals = glm.array(glm.float32,
                0,  1, 0,
                0,  -1,  0,
                1, 0, 0,
                -1, 0,  0,
                0,  0,  1,
                0,  0, -1,
            ),
            faces = glm.array(glm.uint32,
                0,0,0, 1,0,0, 2,0,0,
                0,0,0, 2,0,0, 3,0,0,

                0,0,3, 4,0,3, 1,0,3,
                1,0,3, 4,0,3, 5,0,3,

                0,0,5, 3,0,5, 7,0,5,
                0,0,5, 7,0,5, 4,0,5,

                1,0,4, 5,0,4, 6,0,4,
                1,0,4, 6,0,4, 2,0,4,

                2,0,2, 6,0,2, 7,0,2,
                2,0,2, 7,0,2, 3,0,2,
                
                4,0,1, 7,0,1, 6,0,1,
                4,0,1, 6,0,1, 5,0,1
            ) if enable_box else None,

            #frame= glm.array(glm.uint32,
            #    0,1, 1,2, 2,3, 3,0,
            #    0,4, 1,5, 2,6, 3,7,
            #    4,5, 5,6, 6,7, 7,4,
            #)
            frame = glm.array(glm.uint32, 8, 9)
        )

def normalize_angle(theta):
    while theta < -180 or theta >= 180:
        if theta < -180:
            theta += 360
        elif theta >= 180:
            theta -= 360
    return theta

def slerp(channels, a, b, t):
    diff = b - a
    for i in range(len(channels)):
        if channels[i][1:] == 'ROTATION':
            diff[i] = normalize_angle(diff[i])
    return a + t * diff


class GLSkeleton(GLObject):
    def __init__(self, name, parent, offset, channels, thickness, color=default_color, enable_mesh=True):
        self.offset = offset
        self.name = name
        self.channels = channels
        self.joint = glm.mat4()
        self.color = color
        self.enable_mesh = enable_mesh

        super().__init__(
            parent= parent, 
            link_transform= glm.translate(parent.offset) if parent is not None else None, 
            shape_transform= calculate_rotation_matrix(offset) * glm.scale(glm.vec3(thickness, glm.l2Norm(offset), thickness)), 
            mesh = SkeletonMesh() if enable_mesh and glm.l2Norm(offset) > 0 else None
        )

    def set_joint(self, channel_values, fix_origin=False):
        self.joint = glm.mat4()
        for i in range(len(self.channels)):
            if not fix_origin or self.channels[i] not in ['XPOSITION', 'YPOSITION', 'ZPOSITION']:
                self.joint *= joint_transform[self.channels[i]](channel_values[i])

class GLAnimation:
    def __init__(self, skeletons, roots, motion, frames, framerate):
        self.skeletons= skeletons
        self.roots= roots
        self.motion= motion
        self.framerate= framerate
        self.frames= frames
        self.frame= -1

    def prepare(self):
        for skeleton in self.skeletons:
            skeleton.prepare()
        for root in self.roots:
            self.skeletons[root].update_tree_global_transform()
    
    def set_frame(self, frame, fix_origin=False):
        self.frame = frame % self.frames
        index = 0
        for skeleton in self.skeletons:
            if skeleton.channels is None:
                continue
            skeleton.set_joint(
                self.motion[self.frame][index : index+len(skeleton.channels)], 
                fix_origin
            )
            index += len(skeleton.channels)

        for skeleton in self.skeletons:
            if skeleton.parent is not None:
                skeleton.joint_transform = skeleton.parent.joint

        for root in self.roots:
            self.skeletons[root].update_tree_global_transform()

    def Draw(self, VP, uniform_locs, ignore_light, mode):
        for skeleton in self.skeletons:
            if skeleton.enable_mesh:
                skeleton.Draw(VP, uniform_locs, ignore_light, mode, color=skeleton.color)
    

class GLAnimationInterpolated(GLAnimation):
    def __init__(self, skeletons, roots, motion, frames, framerate):
        super().__init__(skeletons, roots, motion, frames, framerate)
    
    def set_frame(self, frame, factor= 0, fix_origin=False):
        self.frame = frame % self.frames
        index = 0
        for skeleton in self.skeletons:
            if skeleton.channels is None:
                continue
            skeleton.set_joint(slerp(
                skeleton.channels,
                self.motion[self.frame][index : index+len(skeleton.channels)],
                self.motion[(self.frame+1) % self.frames][index : index+len(skeleton.channels)],
                factor
            ), fix_origin)
            index += len(skeleton.channels)

        for skeleton in self.skeletons:
            if skeleton.parent is not None:
                skeleton.joint_transform = skeleton.parent.joint

        for root in self.roots:
            self.skeletons[root].update_tree_global_transform()

    