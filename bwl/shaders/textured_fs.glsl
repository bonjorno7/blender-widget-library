out vec4 fragment_color;

uniform vec2 u_position;
uniform vec2 u_size;
uniform vec4 u_color;
uniform vec4 u_border_color;
uniform vec4 u_border_radius;
uniform float u_border_thickness;
uniform sampler2D u_texture;

float rect_sdf(vec2 p, vec2 s, float r)
{
    vec2 d = abs(p) - s + vec2(r);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - r;   
}

void main()
{
    vec2 position = gl_FragCoord.xy - u_position.xy - u_size / 2.0;
    vec2 half_size = u_size / 2.0 + u_border_thickness;

    vec2 uv = (gl_FragCoord.xy - u_position.xy) / u_size;
    vec4 color = u_color * texture(u_texture, uv);

    float border_radius_left = position.y > 0.0 ? u_border_radius.x : u_border_radius.y;
    float border_radius_right = position.y > 0.0 ? u_border_radius.z : u_border_radius.w;
    float border_radius = position.x < 0.0 ? border_radius_left : border_radius_right;

    float dist_outside = rect_sdf(position, half_size, border_radius);
    float outside_mask = smoothstep(-1.0, 1.0, dist_outside * 1.5);

    if (u_border_thickness > 0.0)
    {
        float dist_inside = dist_outside + u_border_thickness;
        float inside_mask = smoothstep(-1.0, 1.0, dist_inside * 1.5);
        fragment_color = mix(color, u_border_color, inside_mask);
    }
    else
    {
        fragment_color = color;
    }

    fragment_color.a = mix(fragment_color.a, 0.0, outside_mask);
    fragment_color = blender_srgb_to_framebuffer_space(fragment_color);
}
