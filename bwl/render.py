from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import bgl
import blf
from gpu.types import GPUBatch, GPUShader
from gpu_extras.batch import batch_for_shader

from .content import Image
from .input import ModalState
from .layout import Area
from .style import Color, Display, Visibility

if TYPE_CHECKING:
    from .widgets import Widget


class Shaders:
    '''Stored shaders.'''
    standard: GPUShader = None
    image: GPUShader = None


def compile_shaders(recompile: bool = False):
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


def render(widget: Widget, state: ModalState):
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

        if widget.image is None:
            render_standard(
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
            render_image(
                image=widget.image,
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
            render_text(widget, state)

        bgl.glDisable(bgl.GL_BLEND)

        if (widget._style.display != Display.SCROLL) and (widget._layout.scissor != None):
            bgl.glDisable(bgl.GL_SCISSOR_TEST)

    # Render child widgets.
    if widget._style.display == Display.SCROLL:
        for child in widget._children:
            if child._layout.scissor.contains(child._layout.border, True):
                render(child, state)
    else:
        for child in widget._children:
            render(child, state)


def render_standard(
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
    if Shaders.standard is None:
        raise Exception('Shader must be compiled first.')

    Shaders.standard.bind()
    Shaders.standard.uniform_float('u_position', [x, y])
    Shaders.standard.uniform_float('u_size', [width, height])
    Shaders.standard.uniform_float('u_color', color)
    Shaders.standard.uniform_float('u_border_color', border_color)
    Shaders.standard.uniform_float('u_border_radius', border_radius)
    Shaders.standard.uniform_float('u_border_thickness', border_thickness)

    batch: GPUBatch = batch_for_shader(Shaders.standard, 'TRIS', {'position': vertices}, indices=indices)
    batch.draw(Shaders.standard)


def render_image(
    image: Image,
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
    if Shaders.image is None:
        raise Exception('Shader must be compiled first.')

    if image.gl_load():
        raise Exception('Failed to load image.')

    Shaders.image.bind()
    Shaders.image.uniform_float('u_position', [x, y])
    Shaders.image.uniform_float('u_size', [width, height])
    Shaders.image.uniform_float('u_color', color)
    Shaders.image.uniform_float('u_border_color', border_color)
    Shaders.image.uniform_float('u_border_radius', border_radius)
    Shaders.image.uniform_float('u_border_thickness', border_thickness)
    Shaders.image.uniform_int('u_image', 0)

    bgl.glActiveTexture(bgl.GL_TEXTURE0)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)

    batch: GPUBatch = batch_for_shader(Shaders.image, 'TRIS', {'position': vertices}, indices=indices)
    batch.draw(Shaders.image)

    bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)

    image.gl_free()


def render_text(widget: Widget, state: ModalState):
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
