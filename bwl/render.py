from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import bgl
from bpy.types import Context
from gpu.types import GPUBatch, GPUShader
from gpu_extras.batch import batch_for_shader

if TYPE_CHECKING:
    from .widgets.base import Widget


class Shaders:
    '''Stored shaders.'''
    standard: GPUShader = None
    image: GPUShader = None


def compile_shaders(recompile: bool = False) -> None:
    '''Compile the UI shader.'''
    folder = Path(__file__).parent.joinpath('shaders')

    if recompile or Shaders.standard is None:
        vertex_source = folder.joinpath('standard_vs.glsl').read_text()
        fragment_source = folder.joinpath('standard_fs.glsl').read_text()
        Shaders.standard = GPUShader(vertex_source, fragment_source)

    if recompile or Shaders.image is None:
        vertex_source = folder.joinpath('image_vs.glsl').read_text()
        fragment_source = folder.joinpath('image_fs.glsl').read_text()
        Shaders.image = GPUShader(vertex_source, fragment_source)


def render_widget(context: Context, widget: Widget) -> None:
    '''Render a widget on the screen.'''
    x = widget.layout.padding.x
    y = widget.layout.padding.y
    width = widget.layout.padding.width
    height = widget.layout.padding.height

    # Offset Y to work with OpenGL.
    y = context.area.height - y - height

    color = widget.style.color
    border_color = widget.style.border_color
    border_radius = widget.style.border_radius
    border_thickness = widget.style.border_thickness

    # Clamp border radius to border area.
    border_width = widget.layout.border.width
    border_height = widget.layout.border.height
    if border_radius * 2 > min(border_width, border_height):
        border_radius = min(border_width, border_height) / 2

    vertices = (
        (x - border_thickness - 2, y - border_thickness - 2),
        (x + width + border_thickness + 2, y - border_thickness - 2),
        (x + width + border_thickness + 2, y + height + border_thickness + 2),
        (x - border_thickness - 2, y + height + border_thickness + 2),
    )

    indices = (
        (0, 1, 2),
        (2, 3, 0),
    )

    if widget.style.image is None:
        if Shaders.standard is None:
            raise Exception('Shader must be compiled first')

        Shaders.standard.bind()
        Shaders.standard.uniform_float('u_position', [x, y])
        Shaders.standard.uniform_float('u_size', [width, height])
        Shaders.standard.uniform_float('u_color', color)
        Shaders.standard.uniform_float('u_border_color', border_color)
        Shaders.standard.uniform_float('u_border_radius', border_radius)
        Shaders.standard.uniform_float('u_border_thickness', border_thickness)

        bgl.glEnable(bgl.GL_BLEND)
        batch: GPUBatch = batch_for_shader(Shaders.standard, 'TRIS', {'position': vertices}, indices=indices)
        batch.draw(Shaders.standard)
        bgl.glDisable(bgl.GL_BLEND)

    else:
        # TODO: Adjust UVs according to border thickness + 2.
        uvs = (
            (0, 0),
            (1, 0),
            (1, 1),
            (0, 1),
        )

        if Shaders.image is None:
            raise Exception('Shader must be compiled first')

        Shaders.image.bind()
        Shaders.image.uniform_float('u_position', [x, y])
        Shaders.image.uniform_float('u_size', [width, height])
        Shaders.image.uniform_float('u_color', color)
        Shaders.image.uniform_int('u_image', 0)
        Shaders.image.uniform_float('u_border_color', border_color)
        Shaders.image.uniform_float('u_border_radius', border_radius)
        Shaders.image.uniform_float('u_border_thickness', border_thickness)

        image = widget.style.image
        if image.gl_load():
            raise Exception('Failed to load image')

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)

        batch: GPUBatch = batch_for_shader(Shaders.image, 'TRIS', {'position': vertices, 'uv': uvs}, indices=indices)
        batch.draw(Shaders.image)

        bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
        bgl.glDisable(bgl.GL_BLEND)

        image.gl_free()
