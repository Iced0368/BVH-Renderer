#version 330 core

in vec2 TexCoord;
out vec4 FragColor;
uniform sampler2D Texture;
uniform int pixel;

void main()
{
    float Pixels = 512.0;
	float dx = 15.0 * (1.0 / Pixels);
	float dy = 10.0 * (1.0 / Pixels);
	vec2 Coord = vec2(dx * floor(TexCoord.x / dx),
						dy * floor(TexCoord.y / dy));
	FragColor = texture(Texture, Coord);
}