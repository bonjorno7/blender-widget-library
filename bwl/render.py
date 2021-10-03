from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import bgl
from bpy.types import Context
from gpu.types import GPUBatch, GPUShader
from gpu_extras.batch import batch_for_shader

if TYPE_CHECKING:
    from .widgets.base import Widget

_shader: GPUShader = None


def compile_shader(recompile: bool = False):
    '''Compile the UI shader.'''
    global _shader

    if recompile or _shader is None:
        folder = Path(__file__).parent.joinpath('shaders')
        vertex_source = folder.joinpath('vertex.glsl').read_text()
        fragment_source = folder.joinpath('fragment.glsl').read_text()

        _shader = GPUShader(vertex_source, fragment_source)


def render_widget(context: Context, widget: Widget):
    '''Render a widget on the screen.'''
    global _shader

    if _shader is None:
        raise Exception('Shader must be compiled first')

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

    _shader.bind()
    _shader.uniform_float('u_position', [x, y])
    _shader.uniform_float('u_size', [width, height])
    _shader.uniform_float('u_color', color)
    _shader.uniform_float('u_border_color', border_color)
    _shader.uniform_float('u_border_radius', border_radius)
    _shader.uniform_float('u_border_thickness', border_thickness)

    batch: GPUBatch = batch_for_shader(_shader, 'TRIS', {'position': vertices}, indices=indices)
    bgl.glEnable(bgl.GL_BLEND)
    batch.draw(_shader)
    bgl.glDisable(bgl.GL_BLEND)
