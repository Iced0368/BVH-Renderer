import glm
import numpy as np
from components.objects import *


class Cube(GLMesh):
    def __init__(self):
        super().__init__(
            vertices = glm.array(glm.float32,
                -1,  1, -1,   0, 0, 0,
                -1,  1,  1,   1, 0, 0,
                 1,  1,  1,   0, 1, 0,
                 1,  1, -1,   1, 1, 0,
                -1, -1, -1,   0, 0, 1,
                -1, -1,  1,   1, 0, 1,
                 1, -1,  1,   0, 1, 1,
                 1, -1, -1,   1, 1, 1,
            ),
            normals = glm.array(glm.float32,
                -0.577 ,  0.577,  0.577, # v0
                 0.816 ,  0.408,  0.408, # v1
                 0.408 , -0.408,  0.816, # v2
                -0.408 , -0.816,  0.408, # v3
                -0.408 ,  0.408, -0.816, # v4
                 0.408 ,  0.816, -0.408, # v5
                 0.577 , -0.577, -0.577, # v6
                -0.816 , -0.408, -0.408, # v7
            ),
            faces = glm.array(glm.uint32,
                0,0, 1,1, 2,2,
                0,0, 2,2, 3,3,

                0,0, 4,4, 1,1,
                1,1, 4,4, 5,5,

                0,0, 3,3, 7,7,
                0,0, 7,7, 4,4,

                1,1, 5,5, 6,6,
                1,1, 6,6, 2,2,

                2,2, 6,6, 7,7,
                2,2, 7,7, 3,3,
                
                4,4, 7,7, 6,6,
                4,4, 6,6, 5,5
            ),
        )

class Tetra(GLMesh):
    def __init__(self):
        super().__init__(
            vertices = glm.array(glm.float32,
                # position               # color      
                 0.0,    1.0,    0.0,    1.0, 0.0, 0.0,
                 0.942, -0.333,  0.0,    0.0, 1.0, 0.0,
                -0.471, -0.333,  0.942,  0.0, 0.0, 1.0,
                -0.471, -0.333, -0.942,  0.5, 0.5, 0.5,
                # for edges
                 0.0,    1.0,    0.0,    1.0, 1.0, 1.0,
                 0.942, -0.333,  0.0,    1.0, 1.0, 1.0,
                -0.471, -0.333,  0.942,  1.0, 1.0, 1.0,
                -0.471, -0.333, -0.942,  1.0, 1.0, 1.0,
            ),
            normals = glm.array(glm.float32,
                 0.0,    1.0,    0.0,
                 0.942, -0.333,  0.0,
                -0.471, -0.333,  0.942
                -0.471, -0.333, -0.942,
                # for edges
                 0.0,    1.0,    0.0,
                 0.942, -0.333,  0.0,
                -0.471, -0.333,  0.942,
                -0.471, -0.333, -0.942,
            ),
            faces = glm.array(glm.uint32,
                0,0, 1,1, 2,2,
                0,0, 1,1, 3,3,
                0,0, 2,2, 3,3,
                1,1, 2,2, 3,3,
            ),
            frame = glm.array(glm.uint32,
                4, 5,
                4, 6,
                4, 7,
                5, 6,
                5, 7,
                6, 7
            ),
        )


def getRGBfromIndex(i, j, n):
    return 1-j/n, (1+np.sin(np.pi/n*i))/3, j/n


def getSphereCord(azimuth, elevation):
    return (
        np.sin(elevation)*np.cos(azimuth),
        np.cos(elevation),
        np.sin(elevation)*np.sin(azimuth)
    )

class Sphere(GLMesh):
    def __init__(self, n=15):
        s_points = []
        
        for i in range(0, n):
            for j in range(0, n):
                azimuth, elevation = 2*np.pi/(n-1) * i, np.pi/(n-1) * j
                s_points.append([
                    *getSphereCord(azimuth, elevation),        # position
                    *getRGBfromIndex(i, j, n),                 # color
                ])
        # for edges
        for i in range(0, n):
            for j in range(0, n):
                azimuth, elevation = 2*np.pi/(n-1) * i, np.pi/(n-1) * j
                s_points.append([
                    *getSphereCord(azimuth, elevation),        # position
                    *(1.0, 1.0, 1.0),                          # color
                ])

        super().__init__(
            vertices = glm.array(glm.float32, *list(np.array(s_points).reshape(-1))),
            normals = glm.array(glm.float32, *list(np.array(s_points).reshape(-1))),
            faces=glm.array(glm.uint32,
                *(np.array([
                    [
                        n*i + j, n*i + j, 
                        n*i + (j+1), n*i + (j+1), 
                        n*(i+1) + j+1, n*(i+1) + j+1,
                        
                        n*i + j, n*i + j, 
                        n*(i+1) + j, n*(i+1) + j, 
                        n*(i+1) + j+1, n*(i+1) + j+1,
                    ] for i in range(0, n) for j in range(0, n)]
                ).reshape(-1))
            ),
            frame=glm.array(glm.uint32,
                *(np.array([
                    [
                        n*i + j, n*(i+1) + j,
                        n*i + j, n*i + (j+1),
                    ] for i in range(0, n) for j in range(0, n)]
                ).reshape(-1) + n*n)
            )
        )