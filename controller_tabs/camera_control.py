from PySide6.QtWidgets import QVBoxLayout, QWidget, QDoubleSpinBox, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

from gui_components.widgets import *

from manager import RenderManager as RM

class CameraController(QWidget):
    def __init__(self, *args, **kargs):
        super(CameraController, self).__init__( *args, **kargs)
        self.initUI()

    def initUI(self):
        self.slider_factors = {
            'azimuth': (-180, 180),
            'elevation': (-180, 180),
            'distance': (0, 100)
        }
        self.float_factors = ['target_x', 'target_y', 'target_z',]

        self.factors = {}

        layout = QVBoxLayout(self)

        scaler = InterlockedSlider(name='Scale', decimals=2)
        scaler.slider.setMinimum(0.01)
        scaler.slider.setMaximum(100)
        scaler.setValue(1)
        scaler.slider.setTickInterval(10)

        scaler.valueChanged.connect(lambda value: self.updateScale(value))
        scaler.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(scaler)

        target_layout = QHBoxLayout()
        layout.addLayout(target_layout)
        target_layout.setContentsMargins(0, 10, 0, 15)

        for name in self.float_factors:
            input_row_layout = QVBoxLayout()

            label = QLabel(f"{name}:")
            float_edit = QDoubleSpinBox()
            float_edit.setRange(-100.0, 100.0)
            float_edit.setAlignment(Qt.AlignRight)

            input_row_layout.addWidget(label)
            input_row_layout.addWidget(float_edit)
            target_layout.addLayout(input_row_layout)

            self.factors[name] = float_edit

            float_edit.valueChanged.connect(lambda value, name=name: self.updateCameraValue(name, value))

        for name, limit in self.slider_factors.items():
            factor = InterlockedSlider(name=name, decimals=2)
            slider, float_edit = factor.slider, factor.float_edit

            slider.setMinimum(limit[0])
            slider.setMaximum(limit[1])
            slider.setTickInterval((limit[1]-limit[0])/40)
            float_edit.setValue(0)

            layout.addWidget(factor)

            self.factors[name] = factor

            factor.valueChanged.connect(lambda value, name=name: self.updateCameraValue(name, value))
            
        layout.addStretch(1)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)

        label = QLabel(f"background: ")
        colorbox = ColorBox(color=QColor(0, 0, 0))

        colorbox.colorChanged.connect(lambda color: self.updateBackgroundColor(color))

        hbox.addWidget(label)
        hbox.addWidget(colorbox)

        layout.addLayout(hbox)

        layout.setAlignment(Qt.AlignTop)

    def updateScale(self, value):
        RM.Scaler = value

    def updateCameraValue(self, name, value):
        if name in self.factors:
            setattr(RM.Camera, name, value)

    def updateBackgroundColor(self, color):
        RM.BackgroundColor = (color.red()/255, color.green()/255, color.blue()/255)