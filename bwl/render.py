from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import bgl
import blf
from gpu.types import GPUBatch, GPUShader
from gpu_extras.batch import batch_for_shader

from .content import Texture
from .input import ModalState
from .layout import Area
from .style import Color, Display, Visibility

if TYPE_CHECKING:
    from .widgets import Widget


class _Shaders:
    '''Stored shaders.'''
    standard: GPUShader = None
    textured: GPUShader = None


def compile_shaders(recompile: bool = False):
    '''Compile the UI shader.'''
    folder = Path(__file__).parent.joinpath('shaders')

    if recompile or _Shaders.standard is None:
        vertex_source = folder.joinpath('standard_vs.glsl').read_text()
        fragment_source = folder.joinpath('standard_fs.glsl').read_text()
        _Shaders.standard = GPUShader(vertex_source, fragment_source)

    if recompile or _Shaders.textured is None:
        vertex_source = folder.joinpath('textured_vs.glsl').read_text()
        fragment_source = folder.joinpath('textured_fs.glsl').read_text()
        _Shaders.textured = GPUShader(vertex_source, fragment_source)


def render_widget(widget: Widget, state: ModalState):
    '''Render a widget on the screen.'''
    # If display is none, don't render this widget or its children.
    if widget._style.display == Display.NONE:
        return

    # Only render this widget if it's set to visible.
    if widget._style.visibility != Visibility.HIDDEN:
        x = widget._layout.padding.x
        y = widget._layout.padding.y
        width = widget._layout.padding.width
        height = widget._layout.padding.height

        # Offset Y to work with OpenGL.
        y = state.area.height - y - height

        color = widget._style.background_color
        border_color = widget._style.border_color
        border_radius = widget._style.border_radius
        border_thickness = widget._style.border_thickness

        # Clamp border radius to border area.
        border_width = widget._layout.border.width
        border_height = widget._layout.border.height
        border_radius = border_radius.clamped(min(border_width, border_height))

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

        if (widget._style.display != Display.SCROLL) and (widget._layout.scissor != None):
            scissor: Area = round(widget._layout.scissor)

            bgl.glScissor(scissor.x, state.area.height - scissor.y - scissor.height, scissor.width, scissor.height)
            bgl.glEnable(bgl.GL_SCISSOR_TEST)

        bgl.glEnable(bgl.GL_BLEND)

        if widget.texture is None:
            _render_standard(
                x=x,
                y=y,
                width=width,
                height=height,
                color=color,
                border_color=border_color,
                border_radius=border_radius,
                border_thickness=border_thickness,
                vertices=vertices,
                indices=indices,
            )

        else:
            _render_texture(
                texture=widget.texture,
                x=x,
                y=y,
                width=width,
                height=height,
                color=color,
                border_color=border_color,
                border_radius=border_radius,
                border_thickness=border_thickness,
                vertices=vertices,
                indices=indices,
            )

        if widget.text is not None:
            _render_text(widget, state)

        bgl.glDisable(bgl.GL_BLEND)

        if (widget._style.display != Display.SCROLL) and (widget._layout.scissor != None):
            bgl.glDisable(bgl.GL_SCISSOR_TEST)

    # Render child widgets.
    if widget._style.display == Display.SCROLL:
        for child in widget._children:
            if child._layout.scissor.contains(child._layout.border, True):
                render_widget(child, state)
    else:
        for child in widget._children:
            render_widget(child, state)


def _render_standard(
    x: float,
    y: float,
    width: float,
    height: float,
    color: Color,
    border_color: Color,
    border_radius: float,
    border_thickness: float,
    vertices: tuple,
    indices: tuple,
):
    if _Shaders.standard is None:
        raise Exception('Shader must be compiled first.')

    _Shaders.standard.bind()
    _Shaders.standard.uniform_float('u_position', [x, y])
    _Shaders.standard.uniform_float('u_size', [width, height])
    _Shaders.standard.uniform_float('u_color', color)
    _Shaders.standard.uniform_float('u_border_color', border_color)
    _Shaders.standard.uniform_float('u_border_radius', border_radius)
    _Shaders.standard.uniform_float('u_border_thickness', border_thickness)

    batch: GPUBatch = batch_for_shader(_Shaders.standard, 'TRIS', {'position': vertices}, indices=indices)
    batch.draw(_Shaders.standard)


def _render_texture(
    texture: Texture,
    x: float,
    y: float,
    width: float,
    height: float,
    color: Color,
    border_color: Color,
    border_radius: float,
    border_thickness: float,
    vertices: tuple,
    indices: tuple,
):
    if _Shaders.textured is None:
        raise Exception('Shader must be compiled first.')

    if texture.gl_load():
        raise Exception('Failed to load texture.')

    _Shaders.textured.bind()
    _Shaders.textured.uniform_float('u_position', [x, y])
    _Shaders.textured.uniform_float('u_size', [width, height])
    _Shaders.textured.uniform_float('u_color', color)
    _Shaders.textured.uniform_float('u_border_color', border_color)
    _Shaders.textured.uniform_float('u_border_radius', border_radius)
    _Shaders.textured.uniform_float('u_border_thickness', border_thickness)
    _Shaders.textured.uniform_int('u_texture', 0)

    bgl.glActiveTexture(bgl.GL_TEXTURE0)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture.bindcode)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)

    batch: GPUBatch = batch_for_shader(_Shaders.textured, 'TRIS', {'position': vertices}, indices=indices)
    batch.draw(_Shaders.textured)

    bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)

    texture.gl_free()


def _render_text(widget: Widget, state: ModalState):
    x = widget._layout.text.x
    y = widget._layout.text.y
    height = widget._layout.text.height

    # Offset Y to work with OpenGL.
    y = state.area.height - y - height

    # Get the font ID once because it's a getter.
    id = widget._style.font.id

    blf.color(id, *widget._style.foreground_color)
    blf.size(id, widget._style.font_size, 72)
    blf.position(id, x, y, 0)
    blf.draw(id, widget.text)
