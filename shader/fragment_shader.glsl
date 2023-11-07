#version 330 core

in vec3 vout_surface_pos;
in vec2 vout_uv;
in vec3 vout_normal;

out vec4 FragColor;

uniform sampler2D diffuseMap;
uniform sampler2D normalMap;

uniform bool useDiffuseMap;
uniform bool useNormalMap;

uniform vec3 view_pos;

uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Ns;

uniform vec3 mesh_color;

uniform vec3 light_pos[10];
uniform vec3 light_color[10];
uniform bool light_enabled[10];

uniform bool ignore_light;

void main()
{
    // light and material properties
    vec3 material_color;

    vec3 color = vec3(0, 0, 0);
    float alpha = 1.0;

    if(useDiffuseMap) {
        vec4 texColor = texture(diffuseMap, vout_uv);
        material_color = texColor.rgb;
        alpha = texColor.a;
    }
    else
        material_color = mesh_color;

    if(alpha < 0.5)
        discard;

    vec3 normalFromMap = texture(normalMap, vout_uv).xyz * 2.0 - 1.0;

    if(ignore_light)
        color = material_color * Ka * Kd;
    else
        for(int i = 0; i < 10; i++)
        {
            if(!light_enabled[i]) continue;
            
            // light components
            vec3 light_ambient = light_color[i];
            vec3 light_diffuse = light_color[i];
            vec3 light_specular = light_color[i];

            // material components
            vec3 material_ambient = material_color;
            vec3 material_diffuse = material_color;
            vec3 material_specular = light_color[i];  // for non-metal material

            // ambient
            vec3 ambient = 0.3 * light_ambient * material_ambient * Ka;

            // for diffiuse and specular
            vec3 normal;
            if(useNormalMap) normal = normalize(vout_normal + normalFromMap);
            else normal = normalize(vout_normal);

            vec3 surface_pos = vout_surface_pos;
            vec3 light_dir = normalize(light_pos[i] - surface_pos);

            // diffuse
            float diff = max(dot(normal, light_dir), 0);
            vec3 diffuse = diff * light_diffuse * material_diffuse * Kd;

            // specular
            vec3 view_dir = normalize(view_pos - surface_pos);
            vec3 reflect_dir = reflect(-light_dir, normal);
            float spec = pow( max(dot(view_dir, reflect_dir), 0.0), Ns);
            vec3 specular = spec * light_specular * material_specular * Ks;

            color += ambient + diffuse + specular;
        }
        
    FragColor = vec4(color, alpha);
}