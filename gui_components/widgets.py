from dataclasses import dataclass
from typing import Optional
from PySide6.QtWidgets import QVBoxLayout, QCheckBox, QWidget, QSlider, QLineEdit, QHBoxLayout, QLabel, QFrame, QColorDialog
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor


class FloatSlider(QSlider):
    floatValueChanged = Signal(float)

    def __init__(self, *args, decimals=3, **kargs):
        super(FloatSlider, self).__init__(*args, **kargs)
        self._multi = 10.0 ** decimals
        self.setTickInterval(10*self._multi)
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

    def setTickInterval(self, ti):
        super().setTickInterval(ti*self._multi)


class FloatLineEdit(QLineEdit):
    floatValueChanged = Signal(float)
    def __init__(self, *args, decimals=2, default=0, **kargs):
        super(FloatLineEdit, self).__init__(*args, **kargs)
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


class InterlockedSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, *args, label_layout=QHBoxLayout, **kargs):
        super().__init__(*args)
        layout = None

        decimals = kargs.get('decimals')
        name = kargs.get('name')
        _layout = kargs.get('layout')

        if _layout is None:
            layout = QVBoxLayout(self)
        else:
            layout = _layout(self)

        if name is not None:
            self.label = QLabel(f"{name}:")
        else:
            self.label = QLabel()

        if decimals is not None:
            self.slider = FloatSlider(Qt.Horizontal, decimals=decimals)
        else:
            self.slider = FloatSlider(Qt.Horizontal)

        self.float_edit = FloatLineEdit()
        self.float_edit.setValue(0)

        self.slider.floatValueChanged.connect(self.updateLineEdit)
        self.float_edit.editingFinished.connect(self.updateSlider)

        self.slider.setTickPosition(QSlider.TicksBelow) 
        self.float_edit.setAlignment(Qt.AlignRight)

        hbox = label_layout()
        hbox.addWidget(self.label)
        hbox.addWidget(self.float_edit)

        layout.addLayout(hbox)
        layout.addWidget(self.slider)

    def value(self):
        return self.slider.value()
    
    def setValue(self, value):
        self.float_edit.setValue(value)
        self.slider.setValue(value)
        
    def updateLineEdit(self, value):
        self.float_edit.setValue(value)
        self.valueChanged.emit(value)

    def updateSlider(self):
        value = self.slider.value()
        value = self.float_edit.value()
        self.slider.setValue(value)
        self.valueChanged.emit(value)


class CheckboxLabel(QWidget):
    def __init__(self, parent=None, label_text=''):
        super().__init__(parent)

        self.checkbox = QCheckBox()
        self.checkbox.setCheckState(Qt.CheckState.Checked)
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)

        layout.addStretch(1)

        self.setLayout(layout)

class ColorBox(QFrame):
    colorChanged = Signal(QColor)
    def __init__(self, *args, color=QColor(255, 0, 0), **kargs):
        super().__init__()
        self.setFixedSize(25, 25)
        self.setStyleSheet(f"border: 1px solid gray; background-color: {color.name()}; margin:4px;")
        self.mousePressEvent = self.changeColor

    def changeColor(self, event):
        color_dialog = QColorDialog()
        color = color_dialog.getColor()
        if color.isValid():
            self.color = color
            self.setStyleSheet(f"border: 1px solid gray; background-color: {color.name()}; margin:4px;")
            self.colorChanged.emit(color)