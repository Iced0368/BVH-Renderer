import glfw
from OpenGL.GL import *
import numpy as np
import math
import glm
from PIL import Image

def load_texture(file_path):
    img = Image.open(file_path)
    img_data = np.array(list(img.getdata()), np.uint8)
    width, height = img.size
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)
    return texture

def returnFullScreenVAO():
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

def main():
    # GLFW 초기화
    if not glfw.init():
        return

    # 윈도우 생성
    window = glfw.create_window(800, 600, "회전하는 삼각형", None, None)
    if not window:
        glfw.terminate()
        return

    # OpenGL 컨텍스트를 현재 윈도우로 설정
    glfw.make_context_current(window)

    # 삼각형의 정점 좌표
    vertices = np.array([
        -0.5, -0.5, 0.0,
         0.5, -0.5, 0.0,
         0.0,  0.5, 0.0
    ], dtype=np.float32)


    # 정점 배열 생성
    vertex_array = glGenVertexArrays(1)
    glBindVertexArray(vertex_array)

    # 버퍼 생성 및 데이터 전송
    vertex_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # 셰이더 프로그램 작성
    vertex_shader = """
    #version 330 core
    layout (location = 0) in vec3 aPos;
    uniform mat4 model;
    out vec2 vout_uv;

    void main()
    {
        gl_Position = model * vec4(aPos, 1.0);
        vout_uv = gl_Position.xy;
    }
    """

    fragment_shader = """
    #version 330 core
    out vec4 FragColor;
    in vec2 vout_uv;
    uniform sampler2D Texture;
    void main()
    {
        FragColor = vec4(1.0, 0.5, 0.2, 1.0);
        FragColor = texture(Texture, vout_uv);
    }
    """

    shader_program = glCreateProgram()
    vertex_shader_obj = glCreateShader(GL_VERTEX_SHADER)
    fragment_shader_obj = glCreateShader(GL_FRAGMENT_SHADER)

    glShaderSource(vertex_shader_obj, vertex_shader)
    glShaderSource(fragment_shader_obj, fragment_shader)

    glCompileShader(vertex_shader_obj)
    glCompileShader(fragment_shader_obj)

    glAttachShader(shader_program, vertex_shader_obj)
    glAttachShader(shader_program, fragment_shader_obj)

    glLinkProgram(shader_program)
    glUseProgram(shader_program)

    # 정점 데이터 구조 설정
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # 프레임 버퍼 설정
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    # 프레임 버퍼 텍스처 생성 및 연결
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 800, 600, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

    # 렌더버퍼 설정
    rbo = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rbo)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 800, 600)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo)

    # 프레임 버퍼 체크
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        print("프레임 버퍼가 완전하지 않습니다!")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # Blur 셰이더 프로그램 작성
    blur_vertex_shader = """
    #version 330 core
    layout (location = 0) in vec3 aPos;
    out vec2 TexCoord;
    void main()
    {
        gl_Position = vec4(aPos, 1.0);
        TexCoord = (aPos.xy + 1.0) / 2.0;
    }
    """

    blur_fragment_shader = """
    #version 330 core
    in vec2 TexCoord;
    out vec4 FragColor;
    uniform sampler2D screenTexture;
    uniform float blur_radius;
    void main()
    {
        vec4 color = vec4(0.0);
        float total = 0.0;
        for(float x = -blur_radius; x <= blur_radius; x += 1.0) {
            for(float y = -blur_radius; y <= blur_radius; y += 1.0) {
                float weight = 1.0 / (blur_radius * blur_radius);
                color += texture(screenTexture, TexCoord + vec2(x, y) / 800.0) * weight;
                total += weight;
            }
        }
        FragColor = color / total;
    }
    """

    blur_shader_program = glCreateProgram()
    blur_vertex_shader_obj = glCreateShader(GL_VERTEX_SHADER)
    blur_fragment_shader_obj = glCreateShader(GL_FRAGMENT_SHADER)

    glShaderSource(blur_vertex_shader_obj, blur_vertex_shader)
    glShaderSource(blur_fragment_shader_obj, blur_fragment_shader)

    glCompileShader(blur_vertex_shader_obj)
    glCompileShader(blur_fragment_shader_obj)

    glAttachShader(blur_shader_program, blur_vertex_shader_obj)
    glAttachShader(blur_shader_program, blur_fragment_shader_obj)

    glLinkProgram(blur_shader_program)

    fullVAO = returnFullScreenVAO()
    model_location = glGetUniformLocation(shader_program, "model")

    texture1 = load_texture("320px-Solarsystemscope_texture_8k_earth_daymap.jpg")


    # 렌더링 루프
    while not glfw.window_should_close(window):
        glfw.poll_events()


        # 프레임 버퍼에 렌더링
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(shader_program)

        # 회전 행렬 생성
        rotation_angle = glfw.get_time()
        rotation_matrix = glm.rotate(rotation_angle, glm.vec3(0, 0, 1))
        
        # 모델 행렬을 셰이더로 전달
        glUniformMatrix4fv(model_location, 1, GL_FALSE, glm.value_ptr(rotation_matrix))

        glBindVertexArray(vertex_array)
        glBindTexture(GL_TEXTURE_2D, texture1)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        # Blur 셰이더를 활성화
        glUseProgram(blur_shader_program)
        glUniform1f(glGetUniformLocation(blur_shader_program, "blur_radius"), 5.0)  # 블러 반경 설정


        # 텍스처를 화면에 렌더링
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(blur_shader_program)

        glBindVertexArray(fullVAO)
        glBindTexture(GL_TEXTURE_2D, texture)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        # 프론트 버퍼와 백 버퍼 교체
        glfw.swap_buffers(window)

    # GLFW 종료
    glfw.terminate()

if __name__ == "__main__":
    main()
