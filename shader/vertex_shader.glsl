#version 330 core

layout (location = 0) in vec3 vin_pos; 
layout (location = 1) in vec2 vin_uv; 
layout (location = 2) in vec3 vin_normal;

out vec3 vout_surface_pos;
out vec3 vout_normal;
out vec2 vout_uv;

uniform mat4 MVP;
uniform mat4 M;
uniform mat4 ViewPortScaler;

void main()
{
    // 3D points in homogeneous coordinates
    vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1);

    gl_Position = ViewPortScaler * MVP * p3D_in_hcoord;

    vout_surface_pos = vec3(M * vec4(vin_pos, 1));
    vout_normal = normalize( mat3(transpose(inverse(M))) * vin_normal);
    vout_uv = vin_uv;
}