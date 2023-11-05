from PySide6.QtWidgets import QTabWidget, QWidget

from gui_components.widgets import *
from controller_tabs.camera_control import CameraController
from controller_tabs.filter_control import FilterController
from controller_tabs.light_control import LightController
from controller_tabs.mesh_control import MeshController

from manager import RenderManager as RM


class Controller(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 탭 위젯 생성
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setGeometry(0, 0, self.width(), self.height())

        self.cameraController = CameraController()
        self.meshController = MeshController()
        self.filterController = FilterController()
        self.lightController = LightController()
        
        self.tab_widget.addTab(self.cameraController, "Camera")
        self.tab_widget.addTab(self.lightController, "Light")
        self.tab_widget.addTab(self.meshController, "Meshes")
        self.tab_widget.addTab(self.filterController, "Filter")

    def resizeEvent(self, event):
        self.tab_widget.setGeometry(0, 0, self.width(), self.height())
        event.accept()

