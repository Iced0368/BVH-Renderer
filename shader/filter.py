from OpenGL.GL import *
from glfw.GLFW import *
import ctypes
import numpy as np

from .shader_loader import *

from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from gui_components.widgets import ColorBox

from manager import RenderManager as RM


class LabeledInput(QHBoxLayout):
    def __init__(self, name, filter):
        super().__init__()

        label = QLabel(f"{name}: ")
        input_field = QLineEdit()
        input_field.setText(str(filter.parameters[name]))

        input_field.editingFinished.connect(lambda : filter.parmeterChanged(name, input_field.text()))

        self.addWidget(label)
        self.addWidget(input_field)
        self.setContentsMargins(0, 0, 0, 10)

class LabeledColorbox(QHBoxLayout):
    def __init__(self, name, filter, color):
        super().__init__()
        self.setAlignment(Qt.AlignLeft)

        label = QLabel(f"{name}: ")
        colorbox = ColorBox(color=color)

        colorbox.colorChanged.connect(lambda color: filter.parmeterChanged(name, (color.red()/255, color.green()/255, color.blue()/255)))

        self.addWidget(label)
        self.addWidget(colorbox)
        self.setContentsMargins(0, 0, 0, 10)


def _returnFullScreenVAO():
    fullscreen = np.array([
        1,  1, 0,
        1, -1, 0,
        -1, -1, 0,
        1,  1, 0,
        -1,  1, 0,
        -1, -1, 0,
    ], dtype=np.float32)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    # 버퍼 생성 및 데이터 전송
    fullscreen_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, fullscreen_buffer)
    glBufferData(GL_ARRAY_BUFFER, fullscreen.nbytes, fullscreen, GL_STATIC_DRAW)

    # 정점 데이터 구조 설정
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)    
    return VAO


class GLFilter:
    def init():
        GLFilter._fullScreenVAO = _returnFullScreenVAO()

    def __init__(self, vertex_shader_src, fragment_shader_src, parameters={}):
        self.shader_program = load_shaders(vertex_shader_src, fragment_shader_src)
        self.parameters = parameters
        self.locs = {}
        for param in parameters:
            self.locs[param] = glGetUniformLocation(self.shader_program, param)

    def setParameter(self, name, value):
        if name in self.parameters:
            self.parameters[name] = value

    def applyParameter(self): # For Child class
        pass

    def apply(self, texture, fbo):
        glUseProgram(self.shader_program)
        self.applyParameter()

        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader_program)
        glBindVertexArray(self._fullScreenVAO)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
        glDrawArrays(GL_TRIANGLES, 0, 6)

    def parmeterChanged(self, key, value):
        RM.Filter.parameters[key] = value

    def controllerLayouts(self):
        return None


class BlurFilter(GLFilter):
    def __init__(self):
        super().__init__(
            vertex_shader_src = load_shader_code('./shader/blur/vertex_shader.glsl'),
            fragment_shader_src = load_shader_code('./shader/blur/fragment_shader.glsl'),
            parameters= {'blur_radius': 10.0}
        )
    
    def applyParameter(self):
        glUniform1f(self.locs['blur_radius'], float(self.parameters['blur_radius']))
            
    def controllerLayouts(self):
        return LabeledInput(name='blur_radius', filter=self)


class PixelateFilter(GLFilter):
    def __init__(self):
        super().__init__(
            vertex_shader_src = load_shader_code('./shader/pixelate/vertex_shader.glsl'),
            fragment_shader_src = load_shader_code('./shader/pixelate/fragment_shader.glsl'),
            parameters= {'pixel': 64}
        )

    def applyParameter(self):
        glUniform1i(self.locs['pixel'], int(self.parameters['pixel']))

    def controllerLayouts(self):
        return LabeledInput(name='pixel', filter=self)