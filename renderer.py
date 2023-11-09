import sys
import PySide6.QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt

from components.objects import *
from components.grid import Grid, Axis
from components.obj_loader import *
from components.bvh_loader import *

from manager import RenderManager as RM

from shader.shader_loader import *
from shader.filter import *

g_vscaler = glm.mat4()

g_vertex_shader_src = load_shader_code('./shader/vertex_shader.glsl')
g_fragment_shader_src = load_shader_code('./shader/fragment_shader.glsl')

scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100


class MM: # Mouse Manager
    # Mouse Callback
    xpos, ypos = 0, 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class OpenGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAcceptDrops(True)
        self.dropFile = None
        self.g_time = 0
        self.FBO = None
        self.texture = None

    def initializeGL(self):
        # initialize glfw
        if not glfwInit():
            return

        FBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, FBO)

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, int(scaleFactor*self.width()), int(scaleFactor*self.height()), 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

        RBO = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, RBO)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, int(scaleFactor*self.width()), int(scaleFactor*self.height()))
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, RBO)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer is not complete!")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        self.FBO = FBO
        self.texture = texture
        
        GLFilter.init()
        RM.Filter = PixelateFilter()
        RM.FilterController.initUI()
        

        # load shaders
        self.shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)

        # get uniform locations
        self.uniform_names = [
            'MVP', 'M', 'view_pos', 'Scaler', 'ViewPortScaler', 
            'diffuseMap', 'normalMap',
            'useDiffuseMap', 'useNormalMap',
            'Ka', 'Kd', 'Ks', 'Ns', 
            'mesh_color', 
            'light_pos', 'light_color', 'light_enabled', 'ignore_light'
        ]
        self.uniform_locs = {}
        for name in self.uniform_names:
            self.uniform_locs[name] = glGetUniformLocation(self.shader_program, name)

        self.grid = Grid(scale=100)
        self.axis = Axis(scale=100)
        self.grid.prepare()
        self.axis.prepare()

        glUseProgram(self.shader_program)
        glUniform1i(self.uniform_locs['diffuseMap'], 0)
        glUniform1i(self.uniform_locs['normalMap'], 1)


    def resizeGL(self, w, h):
        global g_vscaler
        if h == 0:
            return
        g_vscaler = glm.scale(glm.vec3(1, w/h, 1))
    
    def beforePaintGL(self):
        while not RM.execQueue.empty():
            RM.execQueue.get()()

    def paintGL(self):
        self.beforePaintGL()

        MainCamera = RM.Camera
        Animation = RM.Animation
        Objects = RM.Objects
        ENABLE_GRID = RM.ENABLE_GRID
        ENABLE_INTERPOLATION = RM.ENABLE_INTERPOLATION
        PAUSED = RM.PAUSED
        DRAW_MODE = RM.DRAW_MODE

        defaultFBO = glGetIntegerv(GL_FRAMEBUFFER_BINDING)

        glUseProgram(self.shader_program)
        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO if RM.ENABLE_FILTER else defaultFBO)

        glClearColor(*RM.BackgroundColor, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glUniformMatrix4fv(self.uniform_locs['ViewPortScaler'], 1, GL_FALSE, glm.value_ptr(g_vscaler))
        glUniform3f(self.uniform_locs['view_pos'], MainCamera.eye.x, MainCamera.eye.y, MainCamera.eye.z)

        # projection matrix
        P = MainCamera.projectionMatrix()
        # view matrix
        V = glm.lookAt(MainCamera.eye, MainCamera.target, MainCamera.up)

        VP = P*V * glm.scale(RM.Scaler*glm.vec3(1, 1, 1))

        def Draw(object, ignore_light=False):
            object.Draw(VP, self.uniform_locs, ignore_light, DRAW_MODE)

        if not PAUSED:
            self.g_time = glfwGetTime()
        

        glUniform3fv(self.uniform_locs['light_pos'], RM.MAXLIGHTS, RM.light_positions)
        glUniform3fv(self.uniform_locs['light_color'], RM.MAXLIGHTS, RM.light_colors)
        glUniform1iv(self.uniform_locs['light_enabled'], RM.MAXLIGHTS, RM.light_enabled)

        if Objects is not None:
            for Object in Objects:
                Draw(Object, not RM.ENABLE_SHADE)

        if Animation is not None and Animation.frame >= 0:
            if self.g_time > Animation.framerate:
                glfwSetTime(0)
                Animation.set_frame(
                    Animation.frame+1, 
                    fix_origin= RM.FIX_ORIGIN
                )
            elif ENABLE_INTERPOLATION:
                Animation.set_frame(
                    Animation.frame, 
                    factor= self.g_time / Animation.framerate, 
                    fix_origin= RM.FIX_ORIGIN
                )

        if Animation is not None:
            Draw(Animation, not RM.ENABLE_SHADE)

        if RM.ENABLE_FILTER:
            RM.Filter.apply(self.texture, defaultFBO)

        glUseProgram(self.shader_program)
        VP = P*V
        
        if ENABLE_GRID:
            self.axis.Draw(VP, self.uniform_locs, True, DRAW_WIREFRAME)
            self.grid.Draw(VP, self.uniform_locs, True, DRAW_WIREFRAME)

        #glfwPollEvents()
        self.update()


    def keyPressEvent(self, event):
        key = event.key()

        def _func(key=key):
            if key==Qt.Key_V:
                RM.Camera.isPerspective = not RM.Camera.isPerspective
            if key==Qt.Key_S:
                RM.ENABLE_SHADE = not RM.ENABLE_SHADE
            elif key==Qt.Key_G:
                RM.ENABLE_GRID = not RM.ENABLE_GRID
            elif key==Qt.Key_Space:
                if RM.PAUSED:
                    glfwSetTime(self.g_time)
                RM.PAUSED = not RM.PAUSED
                if RM.Animation is not None and RM.Animation.frame == -1:
                    RM.Animation.frame = 0
            elif key==Qt.Key_F:
                RM.ENABLE_FILTER = not RM.ENABLE_FILTER
            elif key==Qt.Key_O:
                RM.FIX_ORIGIN = not RM.FIX_ORIGIN

            elif key==Qt.Key_Space:
                if RM.Animation is not None and RM.Animation.frame == -1:
                    RM.Animation.frame = 0
            elif key==Qt.Key_I:
                RM.ENABLE_INTERPOLATION = not RM.ENABLE_INTERPOLATION
            elif key==Qt.Key_1:
                RM.DRAW_MODE = DRAW_WIREFRAME
            elif key==Qt.Key_2:
                RM.DRAW_MODE = DRAW_MESH
        
        RM.execQueue.put(_func)

    def mouseReleaseEvent(self, event):
        MM.xpos, MM.ypos = None, None

    def mouseMoveEvent(self, event):
        buttons = event.buttons()
        x, y = event.position().x(), event.position().y()

        if MM.xpos is not None:
            dxpos, dypos = x-MM.xpos, y-MM.ypos
            if buttons & Qt.MouseButton.LeftButton:
                RM.Camera.orbit(0.6*dxpos, 0.6*dypos)
            elif buttons & Qt.MouseButton.RightButton:
                RM.Camera.pan(-0.005*dxpos, 0.005*dypos)

        MM.xpos, MM.ypos = x, y

    def wheelEvent(self, event):
        angle = event.angleDelta().y() / 120
        RM.Camera.zoom(angle)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
 
    def dropEvent(self, event):
        self.dropFile = [u.toLocalFile() for u in event.mimeData().urls()]
        def _func(self=self):
            if self.dropFile is not None:
                for path in self.dropFile:
                    filename = os.path.split(path)[-1]
                    extension = filename.split('.')[-1]
                    if extension == 'bvh':
                        RM.Objects = None
                        RM.Animation = import_bvh(path, log=True)
                        RM.Animation.prepare()
                        RM.PAUSED = True
                        RM.MeshController.loadAnimation()
                        self.g_time = 0
                        glfwSetTime(0)

                    if extension == 'obj':
                        RM.Animation = None
                        Object = import_obj(path, log=True)
                        if RM.Objects is None:
                            RM.Objects = set()
                        RM.Objects.add(Object)
                        RM.MeshController.addObject(Object, filename)
                        Object.prepare()

                self.dropFile = None

        RM.execQueue.put(_func)