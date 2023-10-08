import sys
from PySide6.QtWidgets import QApplication

from manager import RenderManager
from controller import Controller
from renderer import Renderer

def main():
    renderer = Renderer()
    renderer.init()

    app = QApplication(sys.argv)
    window_qt = Controller()
    window_qt.show()
    RenderManager.Camera.controller = window_qt.factorController
    RenderManager.MeshController = window_qt.meshController

    # loop until the user closes the window
    while not renderer.closed():
        renderer.render()

    # terminate glfw
    renderer.terminate()
    window_qt.close()
    sys.exit()

if __name__ == "__main__":
    main()
