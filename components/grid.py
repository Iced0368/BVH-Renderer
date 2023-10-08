from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np

from .objects import GLMesh

class Grid(GLMesh):
    def __init__(self, dg=1, scale=10):
        vertices = glm.array(glm.float32, 
            #poisiton          #color         
             scale, 0.0, 0.0,  1.0, 0.0, 0.0, # x axis start
            -scale, 0.0, 0.0,  1.0, 0.0, 0.0, # x axis end
            0.0, 0.0,  scale,  0.0, 1.0, 0.0, # z axis start
            0.0, 0.0, -scale,  0.0, 1.0, 0.0, # z axis end
            0.0,    0.0, 0.0,  0.0, 0.0, 1.0, # y axis start
            0.0,  scale, 0.0,  0.0, 0.0, 1.0, # y axis end

            # xz-plane grid  
            *(np.array([   
                [   #poisiton              #color        
                        scale, 0.0,   dg*g,   1.0, 1.0, 1.0,    # horizontal grid start
                    -scale, 0.0,   dg*g,   1.0, 1.0, 1.0,   # horizontal grid end
                        dg*g,  0.0,  scale,   1.0, 1.0, 1.0,    # vertical grid start
                        dg*g,  0.0, -scale,   1.0, 1.0, 1.0,    # vertical grid end
                ] for g in range(-scale//dg+1, scale//dg)
            ]
        ).reshape(-1)))
        
        super().__init__(
            vertices= vertices,
            frame = glm.array(glm.uint32, *[i for i in range(len(vertices))])
        )