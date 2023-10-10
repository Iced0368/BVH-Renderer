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