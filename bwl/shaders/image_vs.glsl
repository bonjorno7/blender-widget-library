uniform mat4 ModelViewProjectionMatrix;

in vec2 position;
in vec2 uv;

out vec2 uv_interp;

void main()
{
    uv_interp = uv;

    gl_Position = ModelViewProjectionMatrix * vec4(position.xy, 0.0, 1.0);
}
