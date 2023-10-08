from dataclasses import dataclass
from PySide6.QtWidgets import QCheckBox, QWidget, QSlider, QLineEdit, QHBoxLayout, QLabel, QFrame, QColorDialog
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

@dataclass
class Factor:
    name: str
    minimum: float
    maximum: float


class FloatSlider(QSlider):
    floatValueChanged = Signal(float)

    def __init__(self, *args, decimals=3, **kargs):
        super(FloatSlider, self).__init__( *args, **kargs)
        self._multi = 10.0 ** decimals
        self.valueChanged.connect(self.emitFloatValueChanged)

    def emitFloatValueChanged(self):
        value = float(super(FloatSlider, self).value())/self._multi
        self.floatValueChanged.emit(value)

    def value(self):
        return float(super(FloatSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(FloatSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(FloatSlider, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super(FloatSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(FloatSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(FloatSlider, self).setValue(int(value * self._multi))


class FloatLineEdit(QLineEdit):
    floatValueChanged = Signal(float)
    def __init__(self, *args, decimals=2, default=0, **kargs):
        super(FloatLineEdit, self).__init__( *args, **kargs)
        self.decimals = decimals
        self.textChanged.connect(self.emitFloatValueChanged)
        self.setValue(default)

    def emitFloatValueChanged(self):
        value = round(float(super(FloatLineEdit, self).text()), self.decimals)
        self.floatValueChanged.emit(value)

    def value(self):
        return round(float(super(FloatLineEdit, self).text()), self.decimals)
    
    def setValue(self, value):
        super(FloatLineEdit, self).setText(str(round(value, self.decimals)))



class ColorLabel(QWidget):
    colorChanged = Signal(QColor)

    def __init__(self, label_text, color=QColor(1, 0, 0)):
        super().__init__()
        self.color = color

        self.checkbox = QCheckBox()
        self.checkbox.setCheckState(Qt.CheckState.Checked)

        self.label = QLabel(label_text)
        #self.label.setStyleSheet('background-color: #DDDDDD; border: 2px solid transparent; padding: 2px;')

        self.color_frame = QFrame()
        self.color_frame.setFixedSize(20, 20)
        self.color_frame.setStyleSheet(f"background-color: {color.name()};")

        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)

        layout.addStretch(1)
        layout.addWidget(self.color_frame)

        self.setLayout(layout)

        self.color_frame.mousePressEvent = self.changeColor

    def changeColor(self, event):
        color_dialog = QColorDialog()
        color = color_dialog.getColor()
        if color.isValid():
            self.color = color
            self.color_frame.setStyleSheet(f"background-color: {color.name()};")
            self.colorChanged.emit(color)