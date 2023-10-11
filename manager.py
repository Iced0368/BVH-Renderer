from camera import Camera
from components.objects import *
from queue import Queue
from threading import Lock

class LockedQueue(Queue):
    def __init__(self, maxsize: int = 0):
        super().__init__(maxsize)
        self.lock = Lock()

    def put(self, item):
        with self.lock:
            super().put(item)

    def get(self):
        with self.lock:
            return super().get()


class RenderManager:
    execQueue = LockedQueue()

    Camera = Camera()

    SingleMeshObject = GLObject()
    Animation = None
    MeshController = None

    DRAW_MODE = DRAW_MESH
    PAUSED = False

    ENABLE_GRID = True
    ENABLE_INTERPOLATION = False
    ENABLE_SHADE = True
    ENABLE_FILTER = False

    FIX_ORIGIN = False

    def setRenderer(self, renderer):
        self.renderer = renderer

    def setController(self, controller):
        self.renderer = controller

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    