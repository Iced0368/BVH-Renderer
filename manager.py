from camera import Camera
from components.objects import *

class RenderManager:
    Camera = Camera()

    SingleMeshObject = GLObject()
    Animation = None
    MeshController = None

    DRAW_MODE = DRAW_MESH
    ENABLE_GRID = True
    PAUSED = False
    ENABLE_INTERPOLATION = False
    ENABLE_SHADE = True

    def setRenderer(self, renderer):
        self.renderer = renderer

    def setController(self, controller):
        self.renderer = controller

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    