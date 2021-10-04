uniform mat4 ModelViewProjectionMatrix;

in vec2 position;

void main()
{
    gl_Position = ModelViewProjectionMatrix * vec4(position, 0.0, 1.0);
}
