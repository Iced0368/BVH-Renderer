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
    Scaler = 1.0
    Filter = None

    SingleMeshObject = GLObject()
    Animation = None

    MeshController = None
    FilterController = None
    LightController = None

    MAXLIGHTS = 5

    light_positions = [0, 0, 0]
    light_colors = [1, 1, 1]
    light_enabled = [True]

    while len(light_positions) < 3*MAXLIGHTS:
        light_positions.append(0)

    while len(light_colors) < 3*MAXLIGHTS:
        light_colors.append(1)

    while len(light_enabled) < MAXLIGHTS:
        light_enabled.append(False)
    

    DRAW_MODE = DRAW_MESH
    PAUSED = False

    ENABLE_GRID = True
    ENABLE_INTERPOLATION = False
    ENABLE_SHADE = True
    ENABLE_FILTER = False

    FIX_ORIGIN = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    