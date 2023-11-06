import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

from components.objects import *
from components.obj_loader import *
from components.bvh_loader import *

from manager import RenderManager as RM

from controller import Controller
from renderer import OpenGLWidget


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("OpenGL and Widgets")
        self.setGeometry(100, 100, 1340, 800)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # OpenGL 위젯 생성
        self.renderer = OpenGLWidget()
        self.renderer.setFixedWidth(1000)

        self.controller = Controller()

        # 전체 레이아웃 생성
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.renderer)  # 오른쪽에 OpenGL 위젯 배치
        main_layout.addWidget(self.controller)  # 오른쪽에 다른 위젯 배치
    

def main():
    app = QApplication(sys.argv)
    window = MainApp()

    RM.Camera.controller = window.controller.cameraController
    RM.MeshController = window.controller.meshController
    RM.FilterController = window.controller.filterController

    
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
