import sys
import PySide6.QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt

from components.objects import *
from components.sample_object import *
from components.grid import Grid
from components.obj_loader import *
from components.bvh_loader import *

from manager import RenderManager as RM

g_time = 0
g_scaler = glm.mat4()

g_vertex_shader_src = '''
#version 330 core

layout (location = 0) in vec3 vin_pos; 
layout (location = 1) in vec3 vin_color; 
layout (location = 2) in vec3 vin_normal; 

out vec4 vout_color;

out vec3 vout_surface_pos;
out vec3 vout_normal;

uniform mat4 MVP;
uniform mat4 M;
uniform mat4 Scaler;

void main()
{
    // 3D points in homogeneous coordinates
    vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);

    gl_Position = Scaler * MVP * p3D_in_hcoord;

    vout_color = vec4(vin_color, 1.);
    vout_surface_pos = vec3(M * vec4(vin_pos, 1));
    vout_normal = normalize( mat3(transpose(inverse(M))) * vin_normal);
}
'''

g_fragment_shader_src = '''
#version 330 core

in vec4 vout_color;
in vec3 vout_surface_pos;
in vec3 vout_normal;

out vec4 FragColor;

uniform vec3 view_pos;
uniform vec3 light_coeff;

uniform vec3 light_pos[10];
uniform vec3 light_color[10];
uniform int light_cnt;

uniform int ignore_light;

void main()
{
    // light and material properties
    vec3 material_color = vout_color.xyz;
    float material_shininess = 32.0;

    vec3 color = vec3(0, 0, 0);
    if(ignore_light > 0)
        color = material_color;
    else
        for(int i = 0; i < light_cnt; i++)
        {
            // light components
            vec3 light_ambient = light_color[i];
            vec3 light_diffuse = light_color[i];
            vec3 light_specular = light_color[i];

            // material components
            vec3 material_ambient = material_color;
            vec3 material_diffuse = material_color;
            vec3 material_specular = light_color[i];  // for non-metal material

            // ambient
            vec3 ambient = light_ambient * material_ambient;

            // for diffiuse and specular
            vec3 normal = normalize(vout_normal);
            vec3 surface_pos = vout_surface_pos;
            vec3 light_dir = normalize(light_pos[i] - surface_pos);

            // diffuse
            float diff = max(dot(normal, light_dir), 0);
            vec3 diffuse = diff * light_diffuse * material_diffuse;

            // specular
            vec3 view_dir = normalize(view_pos - surface_pos);
            vec3 reflect_dir = reflect(-light_dir, normal);
            float spec = pow( max(dot(view_dir, reflect_dir), 0.0), material_shininess);
            vec3 specular = spec * light_specular * material_specular;

            color += light_coeff.x * ambient + light_coeff.y * diffuse + light_coeff.z * specular;
        }
    FragColor = vec4(color, 1.);
}
'''

def load_shaders(vertex_shader_source, fragment_shader_source):
    # build and compile our shader program
    # ------------------------------------
    
    # vertex shader 
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)    # create an empty shader object
    glShaderSource(vertex_shader, vertex_shader_source) # provide shader source code
    glCompileShader(vertex_shader)                      # compile the shader object
    
    # check for shader compile errors
    success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if (not success):
        infoLog = glGetShaderInfoLog(vertex_shader)
        print("ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" + infoLog.decode())
        
    # fragment shader
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)    # create an empty shader object
    glShaderSource(fragment_shader, fragment_shader_source) # provide shader source code
    glCompileShader(fragment_shader)                        # compile the shader object
    
    # check for shader compile errors
    success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if (not success):
        infoLog = glGetShaderInfoLog(fragment_shader)
        print("ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" + infoLog.decode())

    # link shaders
    shader_program = glCreateProgram()               # create an empty program object
    glAttachShader(shader_program, vertex_shader)    # attach the shader objects to the program object
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)                    # link the program object

    # check for linking errors
    success = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if (not success):
        infoLog = glGetProgramInfoLog(shader_program)
        print("ERROR::SHADER::PROGRAM::LINKING_FAILED\n" + infoLog.decode())
        
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program    # return the shader program


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

    def initializeGL(self):
        # initialize glfw
        if not glfwInit():
            return

        # load shaders
        self.shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)

        # get uniform locations
        self.uniform_names = ['MVP', 'M', 'view_pos', 'Scaler', 'light_coeff', 'light_pos', 'light_color', 'light_cnt', 'ignore_light']
        self.uniform_locs = {}
        for name in self.uniform_names:
            self.uniform_locs[name] = glGetUniformLocation(self.shader_program, name)

        self.grid = GLObject(mesh=Grid(scale=100))
        self.grid.prepare()


    def resizeGL(self, w, h):
        global g_scaler
        if h == 0:
            return

        #glViewport(0, 0, w, h)
        g_scaler = glm.scale(glm.vec3(1, w/h, 1))

    def paintGL(self):
        global g_time

        if self.dropFile is not None:
            for path in self.dropFile:
                if os.path.split(path)[-1].split('.')[-1] == 'bvh':
                    RM.Animation = import_bvh(path, log=True)
                    RM.Animation.prepare()
                    RM.PAUSED = True
                    RM.MeshController.loadMesh()
                    g_time = 0
                    glfwSetTime(0)
            self.dropFile = None

        MainCamera = RM.Camera
        Animation = RM.Animation
        ENABLE_GRID = RM.ENABLE_GRID
        ENABLE_INTERPOLATION = RM.ENABLE_INTERPOLATION
        PAUSED = RM.PAUSED
        DRAW_MODE = RM.DRAW_MODE

        # enable depth test (we'll see details later)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        glUseProgram(self.shader_program)

        glUniformMatrix4fv(self.uniform_locs['Scaler'], 1, GL_FALSE, glm.value_ptr(g_scaler))
        glUniform3f(self.uniform_locs['view_pos'], MainCamera.eye.x, MainCamera.eye.y, MainCamera.eye.z)

        # projection matrix
        P = MainCamera.projectionMatrix()
        # view matrix
        V = glm.lookAt(MainCamera.eye, MainCamera.target, MainCamera.up)

        VP = P*V

        def Draw(object, ambient, diffuse, specular, ignore_light=False):
            object.Draw(VP, self.uniform_locs, ambient, diffuse, specular, ignore_light, DRAW_MODE)
        
        if ENABLE_GRID:
            self.grid.Draw(VP, self.uniform_locs, 1, 0, 0, True, DRAW_WIREFRAME)

        if not PAUSED:
            g_time = glfwGetTime()
        
        
        light_positions = [6.0, 4.0, 8]
        light_colors = [1, 1, 1]
        light_cnt = len(light_positions) // 3

        glUniform3fv(self.uniform_locs['light_pos'], light_cnt, light_positions)
        glUniform3fv(self.uniform_locs['light_color'], light_cnt, light_colors)
        glUniform1i(self.uniform_locs['light_cnt'], light_cnt)

        if Animation is not None and Animation.frame >= 0:
            if g_time > Animation.framerate:
                glfwSetTime(0)
                Animation.set_frame(Animation.frame+1)
            elif ENABLE_INTERPOLATION:
                Animation.set_frame(Animation.frame, g_time / Animation.framerate)

        if Animation is not None:
            Draw(Animation, 0.3, 1, 1, RM.ENABLE_SHADE)

        #glfwPollEvents()
        self.update()


    def keyPressEvent(self, event):
        key = event.key()

        if key==Qt.Key_V:
            RM.Camera.isPerspective = not RM.Camera.isPerspective
        if key==Qt.Key_S:
            RM.ENABLE_SHADE = not RM.ENABLE_SHADE
        elif key==Qt.Key_G:
            RM.ENABLE_GRID = not RM.ENABLE_GRID
        elif key==Qt.Key_Space:
            if RM.PAUSED:
                glfwSetTime(g_time)
            RM.PAUSED = not RM.PAUSED
            if RM.Animation is not None and RM.Animation.frame == -1:
                RM.Animation.frame = 0

        elif key==Qt.Key_Space:
            if RM.Animation is not None and RM.Animation.frame == -1:
                RM.Animation.frame = 0
        elif key==Qt.Key_I:
            RM.ENABLE_INTERPOLATION = not RM.ENABLE_INTERPOLATION
        elif key==Qt.Key_1:
            RM.DRAW_MODE = DRAW_WIREFRAME
        if key==Qt.Key_2:
            RM.DRAW_MODE = DRAW_MESH

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