#version 330 core

in vec2 TexCoord;
out vec4 FragColor;
uniform sampler2D Texture;
uniform int pixel;

void main()
{
    vec2 p = TexCoord.xy;
	
	p.x = round(p.x * pixel) / pixel;
	p.y = round(p.y * pixel) / pixel;

	//p.x -= mod(p.x, 1.0 / pixel);
	//p.y -= mod(p.y, 1.0 / pixel);
    
	vec3 col = texture(Texture, p).rgb;
	FragColor = vec4(col, 1.0);
}