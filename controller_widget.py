import sys
from dataclasses import dataclass
from PySide6.QtWidgets import QScrollArea, QApplication, QMainWindow, QTabWidget, QSlider, QVBoxLayout, QWidget, QLabel, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt

from gui_components.widgets import *

from manager import RenderManager

@dataclass
class Factor:
    name: str
    minimum: float
    maximum: float


class FactorController(QWidget):
    def __init__(self, *args, **kargs):
        super(FactorController, self).__init__( *args, **kargs)
        self.initUI()

    def initUI(self):
        self.slider_factors = {
            'azimuth': (-180, 180),
            'elevation': (-180, 180),
            'distance': (0, 100)
        }
        self.value_factors = ['target_x', 'target_y', 'target_z',]

        self.sliders = {}
        self.value_inputs = {}

        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        layout.addLayout(top_layout)
        top_layout.setContentsMargins(0, 10, 0, 15)

        for name in self.value_factors:
            input_row_layout = QVBoxLayout()

            label = QLabel(f"{name}:")
            value_input = FloatLineEdit()

            input_row_layout.addWidget(label)
            input_row_layout.addWidget(value_input)
            top_layout.addLayout(input_row_layout)

            self.value_inputs[name] = value_input

            value_input.floatValueChanged.connect(lambda value, name=name: self.inputChangedNotFocused(value, name))
            value_input.returnPressed.connect(lambda name=name: self.value_inputs[name].clearFocus())
            value_input.focusOutEvent = lambda event, name=name: self.inputChanged(self.value_inputs[name].value(), name)


        for name, limit in self.slider_factors.items():
            slider = FloatSlider(Qt.Horizontal, decimals= 2)
            slider.setMinimum(limit[0])
            slider.setMaximum(limit[1])
            slider.setTickInterval(10*slider._multi)
            slider.setTickPosition(QSlider.TicksBelow)

            value_input = FloatLineEdit()
            value_input.setAlignment(Qt.AlignRight)
            value_input.setValue(0)

            label = QLabel(f"{name}:")

            # 레이블과 수치 표시 칸을 수평 레이아웃에 배치
            hbox = QHBoxLayout()
            hbox.addWidget(label)
            hbox.addWidget(value_input)

            layout.addLayout(hbox)
            layout.addWidget(slider)

            self.sliders[name] = slider
            self.value_inputs[name] = value_input

            slider.floatValueChanged.connect(lambda value, name=name: self.sliderChanged(value, name))
            
            value_input.floatValueChanged.connect(lambda value, name=name: self.inputChangedNotFocused(value, name))
            value_input.returnPressed.connect(lambda name=name: self.value_inputs[name].clearFocus())
            value_input.focusOutEvent = lambda event, name=name: self.inputChanged(self.value_inputs[name].value(), name)

        layout.setAlignment(Qt.AlignTop)

    def sliderChanged(self, value, name, decimals=2):
        value = round(value, decimals)
        if name in self.value_inputs:
            self.value_inputs[name].setValue(value)
            setattr(RenderManager.Camera, name, self.sliders[name].value())

    def inputChanged(self, value, name, decimals=2):
        value = round(value, decimals)
        if name in self.slider_factors:
            if self.sliders[name].value() != value and self.slider_factors[name][0] <= value and value <= self.slider_factors[name][1]:
                self.sliders[name].setValue(value)
                setattr(RenderManager.Camera, name, value)
        elif name in self.value_factors:
            setattr(RenderManager.Camera, name, value)

    def inputChangedNotFocused(self, value, name,decimals=2):
        if not self.value_inputs[name].hasFocus():
            self.inputChanged(value, name, decimals)


class MeshController(QWidget):
    def __init__(self, *args, **kargs):
        super(MeshController, self).__init__( *args, **kargs)
        self.initUI()

    def initUI(self):
        # 스크롤 영역 생성
        self.scroll_area = QScrollArea(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.scroll_area)

        # 스크롤 영역에 배치될 위젯 생성
        self.scroll_widget = QWidget()
        self.scroll_widget_layout = QVBoxLayout(self.scroll_widget)

        # 스크롤 영역 설정
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: none; }")


    def loadMesh(self):
        while self.scroll_widget_layout.count() > 0:
            item = self.scroll_widget_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        Animation = RenderManager.Animation
        if Animation is not None:
            for skeleton in Animation.skeletons:
                if not skeleton.enable_mesh:
                    continue
                label = ColorLabel(f"{skeleton.name}:", QColor(255*skeleton.color[0], 255*skeleton.color[1], 255*skeleton.color[2]))
                
                label.colorChanged.connect(lambda color, name=skeleton.name: self.onColorChanged(color, name))
                label.checkbox.stateChanged.connect(lambda state, name=skeleton.name: self.onCheckboxStateChanged(state, name))

                label.layout().setContentsMargins(0, 0, 0, 2)
                self.scroll_widget_layout.addWidget(label)


    def onColorChanged(self, color, name):
        Animation = RenderManager.Animation
        for skeleton in Animation.skeletons:
            if name == skeleton.name:
                skeleton.setColor([color.red() / 255, color.green() / 255, color.blue() / 255])

    def onCheckboxStateChanged(self, state, name):
        Animation = RenderManager.Animation
        for skeleton in Animation.skeletons:
            if name == skeleton.name:
                skeleton.enable_mesh = not skeleton.enable_mesh


class Controller(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 탭 위젯 생성
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setGeometry(0, 0, self.width(), self.height())


        self.factorController = FactorController()
        self.meshController = MeshController()
        
        self.tab_widget.addTab(self.factorController, "Factors")
        self.tab_widget.addTab(self.meshController, "Meshes")

    def resizeEvent(self, event):
        self.tab_widget.setGeometry(0, 0, self.width(), self.height())
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = Controller()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
