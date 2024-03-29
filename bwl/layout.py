from __future__ import annotations

from typing import TYPE_CHECKING, Union, overload

import blf
from bpy.types import Context, Event

from .style import Align, Direction, Display, Size

if TYPE_CHECKING:
    from .widget import Widget


class Area:
    '''Area defined by position and size.'''

    def __init__(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __round__(self) -> Area:
        return Area(round(self.x), round(self.y), round(self.width), round(self.height))

    @overload
    def contains(self, x: float, y: float) -> bool:
        '''Check whether this area contains the given coordinates.'''
        ...

    @overload
    def contains(self, other: Area, partial: bool) -> bool:
        '''Check whether this area contains the given area fully or partially.'''
        ...

    def contains(self, x: Union[float, Area], y: Union[float, bool]) -> bool:
        if isinstance(x, Area):
            other: Area = x
            partial: bool = y

            if partial:
                if (self.x <= other.x + other.width) and (self.x + self.width >= other.x):
                    return (self.y <= other.y + other.height) and (self.y + self.height >= other.y)
            else:
                if (self.x <= other.x) and (self.x + self.width >= other.x + other.width):
                    return (self.y <= other.y) and (self.y + self.height >= other.y + other.height)

            return False
        else:
            return (self.x < x < self.x + self.width) and (self.y < y < self.y + self.height)


class Layout:
    '''Position and size of a widget.'''

    def __init__(self) -> None:
        self.text = Area()
        self.content = Area()
        self.inside = Area()
        self.padding = Area()
        self.border = Area()
        self.margin = Area()

        # None means don't use scissor.
        self.scissor: Union[Area, None] = None

    def under_mouse(self, context: Context, event: Event) -> bool:
        '''Check whether the cursor is inside this layout.'''
        mouse_x = event.mouse_region_x
        mouse_y = context.area.height - event.mouse_region_y

        if self.scissor is not None:
            if not self.scissor.contains(mouse_x, mouse_y):
                return False

        if not self.border.contains(mouse_x, mouse_y):
            return False

        return True


def compute_layout(widget: Widget, context: Context):
    '''Compute layout for the given widget and its children.'''
    # Don't bother calculating layout for widgets with display none.
    if widget._style.display is Display.NONE:
        return

    # Calculate size first because it affects position.
    compute_width(widget, context)
    compute_height(widget, context)
    compute_x(widget, context)
    compute_y(widget, context)

    compute_scissor(widget, context)

    compute_text_size(widget, context)
    compute_text_x(widget, context)
    compute_text_y(widget, context)


def compute_width(widget: Widget, context: Context, width: float = None) -> float:
    '''Compute the content width of this widget and its children, take width taken in parent, return width taken in parent.'''
    # Get relevant groups of child widgets.
    children = [child for child in widget._children if child._style.display not in (Display.NONE, Display.FLOAT)]
    flex_children = [child for child in children if child._style.width.type is Size.Type.FLEXIBLE]
    fixed_children = [child for child in children if child._style.width.type is not Size.Type.FLEXIBLE]
    float_children = [child for child in widget._children if child._style.display is Display.FLOAT]

    # Use the width defined in our own style.
    if widget._style.width.type is Size.Type.ABSOLUTE:
        widget._layout.padding.width = widget._style.width.value
        widget._layout.inside.width = widget._layout.padding.width - widget._style.padding.width
        widget._layout.border.width = widget._layout.padding.width + (widget._style.border_thickness * 2)
        widget._layout.margin.width = widget._layout.border.width + widget._style.margin.width

    # Use a factor of our parent width.
    elif widget._style.width.type is Size.Type.RELATIVE:
        if width is None:
            width = context.area.width

        widget._layout.margin.width = widget._style.width.value * width
        widget._layout.border.width = widget._layout.margin.width - widget._style.margin.width
        widget._layout.padding.width = widget._layout.border.width - (widget._style.border_thickness * 2)
        widget._layout.inside.width = widget._layout.padding.width - widget._style.padding.width

    # Use the width given to us by our parent.
    elif widget._style.width.type is Size.Type.FLEXIBLE:
        if width is None:
            width = context.area.width

        widget._layout.margin.width = width
        widget._layout.border.width = widget._layout.margin.width - widget._style.margin.width
        widget._layout.padding.width = widget._layout.border.width - (widget._style.border_thickness * 2)
        widget._layout.inside.width = widget._layout.padding.width - widget._style.padding.width

    # Use the width of our texture.
    elif widget._style.width.type is Size.Type.TEXTURE:
        if widget.texture is None:
            raise Exception('Widgets that get size from texture must have a texture')

        widget._layout.padding.width = widget.texture.width
        widget._layout.inside.width = widget._layout.padding.width - widget._style.padding.width
        widget._layout.border.width = widget._layout.padding.width + (widget._style.border_thickness * 2)
        widget._layout.margin.width = widget._layout.border.width + widget._style.margin.width

    # Calculate width per stretching child.
    if widget._style.direction is Direction.HORIZONTAL:
        inside_width = widget._layout.inside.width
        content_width = sum(compute_width(child, context, inside_width) for child in fixed_children)
        widget._layout.content.width = content_width

        if flex_children:
            flexible_width = inside_width - content_width
            width_per_weight = flexible_width / sum(child._style.width.value for child in flex_children)

    # Stretch children to fit our width.
    elif widget._style.direction is Direction.VERTICAL:
        inside_width = widget._layout.inside.width
        content_width = max((compute_width(child, context, inside_width) for child in fixed_children), default=0)
        widget._layout.content.width = content_width

        if flex_children:
            width_per_weight = widget._layout.inside.width

    # Stretch children to fit the stretchable width.
    for child in flex_children:
        compute_width(child, context, child._style.width.value * width_per_weight)

    # Fit our width to our children.
    if widget._style.width.type is Size.Type.CHILDREN:
        widget._layout.inside.width = widget._layout.content.width
        widget._layout.padding.width = widget._layout.inside.width + widget._style.padding.width
        widget._layout.border.width = widget._layout.padding.width + (widget._style.border_thickness * 2)
        widget._layout.margin.width = widget._layout.border.width + widget._style.margin.width

    # Floating children can take the full width.
    for child in float_children:
        compute_width(child, context, widget._layout.inside.width)

    # Return our width, so our parent can use it to calculate its content width.
    return widget._layout.margin.width


def compute_height(widget: Widget, context: Context, height: float = None) -> float:
    '''Compute the content height of this widget and its children, take height taken in parent, return height taken in parent.'''
    # Get relevant groups of child widgets.
    children = [child for child in widget._children if child._style.display not in (Display.NONE, Display.FLOAT)]
    flex_children = [child for child in children if child._style.height.type is Size.Type.FLEXIBLE]
    fixed_children = [child for child in children if child._style.height.type is not Size.Type.FLEXIBLE]
    float_children = [child for child in widget._children if child._style.display is Display.FLOAT]

    # Use the height defined in our own style.
    if widget._style.height.type is Size.Type.ABSOLUTE:
        widget._layout.padding.height = widget._style.height.value
        widget._layout.inside.height = widget._layout.padding.height - widget._style.padding.height
        widget._layout.border.height = widget._layout.padding.height + (widget._style.border_thickness * 2)
        widget._layout.margin.height = widget._layout.border.height + widget._style.margin.height

    # Use a factor of our parent height.
    elif widget._style.height.type is Size.Type.RELATIVE:
        if height is None:
            height = context.area.height

        widget._layout.margin.height = widget._style.height.value * height
        widget._layout.border.height = widget._layout.margin.height - widget._style.margin.height
        widget._layout.padding.height = widget._layout.border.height - (widget._style.border_thickness * 2)
        widget._layout.inside.height = widget._layout.padding.height - widget._style.padding.height

    # Use the height given to us by our parent.
    elif widget._style.height.type is Size.Type.FLEXIBLE:
        if height is None:
            height = context.area.height

        widget._layout.margin.height = height
        widget._layout.border.height = widget._layout.margin.height - widget._style.margin.height
        widget._layout.padding.height = widget._layout.border.height - (widget._style.border_thickness * 2)
        widget._layout.inside.height = widget._layout.padding.height - widget._style.padding.height

    # Use the height of our texture.
    elif widget._style.height.type is Size.Type.TEXTURE:
        if widget.texture is None:
            raise Exception('Widgets that get size from texture must have a texture')

        widget._layout.padding.height = widget.texture.height
        widget._layout.inside.height = widget._layout.padding.height - widget._style.padding.height
        widget._layout.border.height = widget._layout.padding.height + (widget._style.border_thickness * 2)
        widget._layout.margin.height = widget._layout.border.height + widget._style.margin.height

    # Calculate height per stretching child.
    if widget._style.direction is Direction.VERTICAL:
        inside_height = widget._layout.inside.height
        content_height = sum(compute_height(child, context, inside_height) for child in fixed_children)
        widget._layout.content.height = content_height

        if flex_children:
            flexible_height = inside_height - content_height
            height_per_weight = flexible_height / sum(child._style.height.value for child in flex_children)

    # Stretch children to fit our height.
    elif widget._style.direction is Direction.HORIZONTAL:
        inside_height = widget._layout.inside.height
        content_height = max((compute_height(child, context, inside_height) for child in fixed_children), default=0)
        widget._layout.content.height = content_height

        if flex_children:
            height_per_weight = inside_height

    # Fit our height to our children.
    if widget._style.height.type is Size.Type.CHILDREN:
        widget._layout.inside.height = widget._layout.content.height
        widget._layout.padding.height = widget._layout.inside.height + widget._style.padding.height
        widget._layout.border.height = widget._layout.padding.height + (widget._style.border_thickness * 2)
        widget._layout.margin.height = widget._layout.border.height + widget._style.margin.height

    # Stretch children to fit the stretchable height.
    for child in flex_children:
        compute_height(child, context, child._style.height.value * height_per_weight)

    # Floating children can take the full height.
    for child in float_children:
        compute_height(child, context, widget._layout.inside.height)

    # Return our height, so our parent can use it to calculate its content height.
    return widget._layout.margin.height


def compute_x(widget: Widget, context: Context, x: float = None):
    # Get relevant groups of child widgets.
    children = [child for child in widget._children if child._style.display not in (Display.NONE, Display.FLOAT)]
    flex_children = [child for child in children if child._style.width.type is Size.Type.FLEXIBLE]
    float_children = [child for child in widget._children if child._style.display is Display.FLOAT]

    # Start at the position defined in style.
    widget._layout.margin.x = widget._style.offset_x

    # Add the position given by our parent.
    if x is not None:
        widget._layout.margin.x += x

    # Calculate positions for other bounding boxes.
    widget._layout.border.x = widget._layout.margin.x + widget._style.margin.left
    widget._layout.padding.x = widget._layout.border.x + widget._style.border_thickness
    widget._layout.inside.x = widget._layout.padding.x + widget._style.padding.left

    # Calculate content position for horizontal layout.
    if widget._style.direction is Direction.HORIZONTAL:
        if flex_children or widget._style.align_x is Align.START:
            widget._layout.content.x = widget._layout.inside.x
        else:
            offset = widget._layout.inside.width - widget._layout.content.width
            if widget._style.align_x is Align.CENTER:
                widget._layout.content.x = widget._layout.inside.x + offset / 2
            elif widget._style.align_x is Align.END:
                widget._layout.content.x = widget._layout.inside.x + offset

        # Calculate position for children.
        child_x = widget._layout.content.x - widget._style.scroll
        for child in children:
            compute_x(child, context, child_x)
            child_x += child._layout.margin.width

    # Calculate content position for vertical layout.
    elif widget._style.direction is Direction.VERTICAL:
        for child in children:
            if widget._style.align_x is Align.START:
                compute_x(child, context, widget._layout.inside.x)
            else:
                offset = widget._layout.inside.width - child._layout.margin.width
                if widget._style.align_x is Align.CENTER:
                    compute_x(child, context, widget._layout.inside.x + offset / 2)
                elif widget._style.align_x is Align.END:
                    compute_x(child, context, widget._layout.inside.x + offset)

    # Floating children are placed relative to our inside position.
    for child in float_children:
        compute_x(child, context, widget._layout.inside.x)


def compute_y(widget: Widget, context: Context, y: float = None):
    # Get relevant groups of child widgets.
    children = [child for child in widget._children if child._style.display not in (Display.NONE, Display.FLOAT)]
    flex_children = [child for child in children if child._style.height.type is Size.Type.FLEXIBLE]
    float_children = [child for child in widget._children if child._style.display is Display.FLOAT]

    # Start at the position defined in style.
    widget._layout.margin.y = widget._style.offset_y

    # Add the position given by our parent.
    if y is not None:
        widget._layout.margin.y += y

    # Calculate positions for other bounding boxes.
    widget._layout.border.y = widget._layout.margin.y + widget._style.margin.top
    widget._layout.padding.y = widget._layout.border.y + widget._style.border_thickness
    widget._layout.inside.y = widget._layout.padding.y + widget._style.padding.top

    # Calculate content position for vertical layout.
    if widget._style.direction is Direction.VERTICAL:
        if flex_children or widget._style.align_y is Align.START:
            widget._layout.content.y = widget._layout.inside.y
        else:
            offset = widget._layout.inside.height - widget._layout.content.height
            if widget._style.align_y is Align.CENTER:
                widget._layout.content.y = widget._layout.inside.y + offset / 2
            elif widget._style.align_y is Align.END:
                widget._layout.content.y = widget._layout.inside.y + offset

        # Calculate position for children.
        child_y = widget._layout.content.y - widget._style.scroll
        for child in children:
            compute_y(child, context, child_y)
            child_y += child._layout.margin.height

    # Calculate content position for horizontal layout.
    elif widget._style.direction is Direction.HORIZONTAL:
        for child in children:
            if widget._style.align_y is Align.START:
                compute_y(child, context, widget._layout.inside.y)
            else:
                offset = widget._layout.inside.height - child._layout.margin.height
                if widget._style.align_y is Align.CENTER:
                    compute_y(child, context, widget._layout.inside.y + offset / 2)
                elif widget._style.align_y is Align.END:
                    compute_y(child, context, widget._layout.inside.y + offset)

    # Floating children are placed relative to our inside position.
    for child in float_children:
        compute_x(child, context, widget._layout.inside.y)


def compute_scissor(widget: Widget, context: Context, area: Area = None):
    if area is not None:
        widget._layout.scissor = area
    elif widget._style.display is Display.SCROLL:
        widget._layout.scissor = widget._layout.padding
    else:
        widget._layout.scissor = None

    for child in widget._children:
        if child._style.display is not Display.NONE:
            compute_scissor(child, context, widget._layout.scissor)


def compute_text_size(widget: Widget, context: Context):
    if widget.text is not None:
        font_id = widget._style.font.id
        font_size = widget._style.font_size
        blf.size(font_id, font_size, 72)

        # Get height from capital A because it looks better.
        width = blf.dimensions(font_id, widget.text)[0]
        height = blf.dimensions(font_id, 'A')[1]

        widget._layout.text.width = width
        widget._layout.text.height = height

    for child in widget._children:
        if child._style.display is not Display.NONE:
            compute_text_size(child, context)


def compute_text_x(widget: Widget, context: Context):
    if widget.text is not None:
        if widget._style.align_x is Align.START:
            widget._layout.text.x = widget._layout.inside.x
        else:
            offset = widget._layout.inside.width - widget._layout.text.width
            if widget._style.align_x is Align.CENTER:
                widget._layout.text.x = widget._layout.inside.x + offset / 2
            elif widget._style.align_x is Align.END:
                widget._layout.text.x = widget._layout.inside.x + offset

    for child in widget._children:
        if child._style.display is not Display.NONE:
            compute_text_x(child, context)


def compute_text_y(widget: Widget, context: Context):
    if widget.text is not None:
        if widget._style.align_y is Align.START:
            widget._layout.text.y = widget._layout.inside.y
        else:
            offset = widget._layout.inside.height - widget._layout.text.height
            if widget._style.align_y is Align.CENTER:
                widget._layout.text.y = widget._layout.inside.y + offset / 2
            elif widget._style.align_y is Align.END:
                widget._layout.text.y = widget._layout.inside.y + offset

    for child in widget._children:
        if child._style.display is not Display.NONE:
            compute_text_y(child, context)
