from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np

from .objects import GLMesh, GLObject

class Grid(GLObject):
    def __init__(self, dg=1, scale=10):
        vertices = glm.array(glm.float32, 
            # xz-plane grid  
            *(np.array([   
                [   #poisiton            
                     scale, 0.0,   dg*g,  
                    -scale, 0.0,   dg*g,
                     dg*g,  0.0,  scale,
                     dg*g,  0.0, -scale,
                ] for g in range(-scale//dg+1, scale//dg)
            ]
        ).reshape(-1)))
        
        super().__init__(
            mesh=GLMesh(
                vertices= vertices,
                frame = glm.array(glm.uint32, *[i for i in range(len(vertices))])
            )
        )


class Axis:
    def __init__(self, scale=10):
        self.x = GLObject(mesh=GLMesh(
            vertices = glm.array(glm.float32,    
                 scale, 0.0, 0.0,
                -scale, 0.0, 0.0,
            ),
            frame = glm.array(glm.uint32, 0, 1)
        ))
        self.y = GLObject(mesh=GLMesh(
            vertices = glm.array(glm.float32,    
                0.0, 0.0,  scale,
                0.0, 0.0, -scale,
            ),
            frame = glm.array(glm.uint32, 0, 1)
        ))
        self.z = GLObject(mesh=GLMesh(
            vertices = glm.array(glm.float32,    
                0.0,    0.0, 0.0,
                0.0,  scale, 0.0,
            ),
            frame = glm.array(glm.uint32, 0, 1)
        ))

    def prepare(self):
        self.x.prepare()
        self.y.prepare()
        self.z.prepare()
    
    def Draw(self, VP, uniform_locs, ignore_light, mode):
        glUniform1i(uniform_locs['ignore_light'], 1)
        glUniform1i(uniform_locs['useDiffuseMap'], 0)
        glUniform1i(uniform_locs['useNormalMap'], 0)

        axises = [self.x, self.y, self.z]
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]

        for i in range(3):
            axis = axises[i]
            axis.Draw(VP, uniform_locs, ignore_light, mode, color=colors[i])