from OpenGL.GL import *
from glfw.GLFW import *
import glm
import os

from components.objects import *
from components.sample_object import *
from components.grid import Grid
from components.obj_loader import *
from components.bvh_loader import *


from manager import *

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


def framebuffer_size_callback(window, width, height):
    global g_scaler
    if height == 0:
        return

    glViewport(0, 0, width, height)
    g_scaler = glm.scale(glm.vec3(1, width/height, 1))


# Key Callback
def key_callback(window, key, scancode, action, mods):
    if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    else:
        if action==GLFW_PRESS or action==GLFW_REPEAT:
            # share
            if key==GLFW_KEY_V:
                RenderManager.Camera.isPerspective = not RenderManager.Camera.isPerspective
            if key==GLFW_KEY_S:
                RenderManager.ENABLE_SHADE = not RenderManager.ENABLE_SHADE
            elif key==GLFW_KEY_G:
                RenderManager.ENABLE_GRID = not RenderManager.ENABLE_GRID
            elif key==GLFW_KEY_SPACE:
                if RenderManager.PAUSED:
                    glfwSetTime(g_time)
                RenderManager.PAUSED = not RenderManager.PAUSED

            if RenderManager.RenderingMode in [AnimationRendering]:
                if key==GLFW_KEY_SPACE:
                    if RenderManager.Animation is not None and RenderManager.Animation.frame == -1:
                        RenderManager.Animation.frame = 0
                elif key==GLFW_KEY_I:
                    RenderManager.ENABLE_INTERPOLATION = not RenderManager.ENABLE_INTERPOLATION
                if key==GLFW_KEY_1:
                    RenderManager.DRAW_MODE = DRAW_WIREFRAME
                if key==GLFW_KEY_2:
                    RenderManager.DRAW_MODE = DRAW_MESH
            

# Mouse Callback
LEFT, RIGHT = 0, 1
pressed = [False, False] # Left, Right
xpos = 0
ypos = 0
dxpos = 0
dypos = 0

def mouseclick_callback(window, button, action, mods):
    global pressed
    if button in [0, 1]:
        pressed[button] = action

def mousemove_callback(window, x, y):
    global xpos, ypos, dxpos, dypos
    dxpos, dypos = x-xpos, y-ypos
    xpos, ypos = x, y
    if pressed[LEFT]:
        RenderManager.Camera.orbit(0.6*dxpos, 0.6*dypos)
    elif pressed[RIGHT]:
        RenderManager.Camera.pan(-0.005*dxpos, 0.005*dypos)

def mousescroll_callback(window, xoffset, yoffset):
    RenderManager.Camera.zoom(yoffset)


def drop_callback(window, paths):
    global g_time
    for path in paths:
        if os.path.split(path)[-1].split('.')[-1] == 'bvh':
            RenderManager.Animation = import_bvh(path, log=True)
            RenderManager.Animation.prepare()
            RenderManager.RenderingMode = AnimationRendering
            RenderManager.PAUSED = True
            g_time = 0
            glfwSetTime(0)

            RenderManager.MeshController.loadMesh()



class Renderer:
    def init(self):
        # initialize glfw
        if not glfwInit():
            return

        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)   # OpenGL 3.3
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE) # for macOS

        # create a window and OpenGL context
        self.window = glfwCreateWindow(1200, 800, 'Renderer', None, None)
        if not self.window:
            glfwTerminate()
            return
        glfwMakeContextCurrent(self.window)

        # register event callbacks
        glfwSetKeyCallback(self.window, key_callback)
        glfwSetMouseButtonCallback(self.window, mouseclick_callback)
        glfwSetCursorPosCallback(self.window, mousemove_callback)
        glfwSetScrollCallback(self.window, mousescroll_callback)
        glfwSetFramebufferSizeCallback(self.window, framebuffer_size_callback)
        glfwSetDropCallback(self.window, drop_callback)

        # load shaders
        self.shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)

        # get uniform locations
        self.uniform_names = ['MVP', 'M', 'view_pos', 'Scaler', 'light_coeff', 'light_pos', 'light_color', 'light_cnt', 'ignore_light']
        self.uniform_locs = {}
        for name in self.uniform_names:
            self.uniform_locs[name] = glGetUniformLocation(self.shader_program, name)

        self.grid = GLObject(mesh=Grid(scale=100))
        self.grid.prepare()


    def closed(self):
        return glfwWindowShouldClose(self.window)
    
    def terminate(self):
        glfwTerminate()
    
    def render(self):
        global g_time
        MainCamera = RenderManager.Camera
        RenderingMode = RenderManager.RenderingMode
        Animation = RenderManager.Animation
        ENABLE_GRID = RenderManager.ENABLE_GRID
        ENABLE_INTERPOLATION = RenderManager.ENABLE_INTERPOLATION
        PAUSED = RenderManager.PAUSED
        DRAW_MODE = RenderManager.DRAW_MODE

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
        
        
        if RenderingMode == AnimationRendering:
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
                Draw(Animation, 0.3, 1, 1, RenderManager.ENABLE_SHADE)

        glfwSwapBuffers(self.window)
        glfwPollEvents()