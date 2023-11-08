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
        
        filter_layouts = RM.Filter.controllerLayouts()

        if filter_layouts is not None:
            for filter_layout in [filter_layouts]:
                layout.addLayout(filter_layout)

        layout.setContentsMargins(10, 20, 10, 10)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def parmeterChanged(self, key, value):
        RM.Filter.parameters[key] = value