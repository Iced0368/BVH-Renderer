from typing import Optional
from PySide6.QtWidgets import QScrollArea, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PySide6.QtCore import Qt

from gui_components.widgets import *

from manager import RenderManager as RM
from queue import Queue

class LightWidget(QWidget):
    def __init__(self, index=None):
        super().__init__()
        self.index = index
        if index is not None:
            for offset in range(3):
                RM.light_positions[3*index + offset] = 4
                RM.light_colors[3*index + offset] = 1
            RM.light_enabled[index] = True

        self.axis= []
        layout = QVBoxLayout(self)

        label_layout = QHBoxLayout()
        slider_layout = QHBoxLayout()

        label_layout.addWidget(QLabel("Show/hide"))
        checkbox = QCheckBox()
        checkbox.setCheckState(Qt.CheckState.Checked)
        checkbox.stateChanged.connect(self.updateEnabled)
        label_layout.addWidget(checkbox)

        label_layout.addWidget(QLabel(" Color"))
        colorbox = ColorBox(color=QColor(255,255,255))
        colorbox.colorChanged.connect(lambda color: self.updateColor(color))
        label_layout.addWidget(colorbox)

        label_layout.addWidget(QLabel(" Remove"))
        self.remove_button = QPushButton("X")
        self.remove_button.setFixedWidth(25)
        label_layout.addWidget(self.remove_button)

        label_layout.setAlignment(Qt.AlignCenter)
        label_layout.setContentsMargins(1, 1, 1, 1)
        
        for axis in ['x', 'y', 'z']:
            islider = InterlockedSlider(name=axis, decimals=2)
            islider.layout().setContentsMargins(1, 0, 1, 0)
            islider.slider.setMinimum(-50)
            islider.slider.setMaximum(50)
            islider.slider.setTickInterval(10)
            #islider.float_edit.setStyleSheet('background-color: white;')
            islider.valueChanged.connect(lambda value: self.updatePosition())

            slider_layout.addWidget(islider)
            self.axis.append(islider)

        layout.addLayout(label_layout)
        layout.addLayout(slider_layout)
        #self.setStyleSheet('background-color: #DDDDDD;')
    

    def updatePosition(self):
        for offset in range(3):
            RM.light_positions[3*self.index + offset] = self.axis[offset].value()

    def updateColor(self, color):
        RM.light_colors[3*self.index:3*self.index+3] = [color.red() / 255, color.green() / 255, color.blue() / 255]

    def updateEnabled(self):
        RM.light_enabled[self.index] = not RM.light_enabled[self.index]


class LightController(QWidget):
    def __init__(self, *args, **kargs):
        super(LightController, self).__init__(*args, **kargs)
        self.indexq = Queue()
        [self.indexq.put(i) for i in range(RM.MAXLIGHTS)]
        self.initUI()

    def initUI(self):
        scroll_area = QScrollArea(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)

        content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(content_widget)

        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.addNewWidget)
        self.content_layout.addWidget(self.add_button)
        self.content_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: none; }")

        for i in range(RM.MAXLIGHTS):
            if RM.light_enabled[i]:
                self.addNewWidget()

    def addNewWidget(self):
        new_widget = LightWidget(self.indexq.get())

        new_widget.remove_button.clicked.connect(lambda: self.removeWidget(new_widget))

        self.content_layout.insertWidget(self.content_layout.count()-1, new_widget)

        if self.content_layout.count() > RM.MAXLIGHTS:
            self.add_button.setVisible(False)
        
        return new_widget


    def removeWidget(self, widget):
        RM.light_enabled[widget.index] = False
        self.indexq.put(widget.index)
        widget.deleteLater()

        self.add_button.setVisible(True)