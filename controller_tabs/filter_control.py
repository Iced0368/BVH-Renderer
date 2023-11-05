from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt

from gui_components.widgets import *

from manager import RenderManager as RM


class FilterController(QWidget):
    def __init__(self, *args, **kargs):
        super(FilterController, self).__init__( *args, **kargs)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        if RM.Filter is None:
            return
        for key, value in RM.Filter.parameters.items():
            hbox = QHBoxLayout()
            
            label = QLabel(f"{key}: ")
            input_field = QLineEdit()
            input_field.setText(str(value))

            input_field.editingFinished.connect(lambda key=key: self.parmeterChanged(key, input_field.text()))

            hbox.addWidget(label)
            hbox.addWidget(input_field)
            hbox.setContentsMargins(0, 0, 0, 10)

            layout.addLayout(hbox)

        layout.setContentsMargins(10, 20, 10, 10)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def parmeterChanged(self, key, value):
        RM.Filter.parameters[key] = value