from OpenGL.GL import *
from glfw.GLFW import *
import ctypes
import numpy as np

from .loader import *

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
        glBindTexture(GL_TEXTURE_2D, texture)
        glDrawArrays(GL_TRIANGLES, 0, 6)


class BlurFilter(GLFilter):
    def __init__(self):
        super().__init__(
            vertex_shader_src = load_shader_code('./shader/blur/vertex_shader.glsl'),
            fragment_shader_src = load_shader_code('./shader/blur/fragment_shader.glsl'),
            parameters= {'blur_radius': 10.0}
        )
    
    def applyParameter(self):
        glUniform1f(self.locs['blur_radius'], self.parameters['blur_radius'])


class PixelateFilter(GLFilter):
    def __init__(self):
        super().__init__(
            vertex_shader_src = load_shader_code('./shader/pixelate/vertex_shader.glsl'),
            fragment_shader_src = load_shader_code('./shader/pixelate/fragment_shader.glsl'),
            parameters= {'pixel': 10}
        )
    
    def applyParameter(self):
        glUniform1i(self.locs['pixel'], self.parameters['pixel'])
