#version 330 core

in vec2 TexCoord;
out vec4 FragColor;
uniform sampler2D Texture;
uniform float blur_radius;

void main()
{
    vec4 color = vec4(0.0);
    float total = 0.0;
    for(float x = -blur_radius; x <= blur_radius; x += 1.0) {
        for(float y = -blur_radius; y <= blur_radius; y += 1.0) {
            float weight = 1.0 / (blur_radius * blur_radius);
            color += texture(Texture, TexCoord + vec2(x, y) / 800.0) * weight;
            total += weight;
        }
    }
    FragColor = color / total;
}