from camera import Camera
from components.objects import *

AHModelRendering = 0
SingleMeshRendering = 1
AnimationRendering = 2

class RenderManager:
    Camera = Camera()

    RenderingMode = AnimationRendering
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

    