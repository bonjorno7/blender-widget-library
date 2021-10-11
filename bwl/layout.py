from __future__ import annotations

from typing import TYPE_CHECKING, Union, overload

import blf

from .style import Align, Direction, Display, Size

if TYPE_CHECKING:
    from .input import ModalState
    from .widgets import Widget


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


def compute_layout(widget: Widget, state: ModalState):
    '''Compute layout for the given widget and its children.'''
    # Don't bother calculating layout for widgets with display none.
    if widget.style.display == Display.NONE:
        return

    # Calculate size first because it affects position.
    compute_width(widget, state)
    compute_height(widget, state)
    compute_x(widget, state)
    compute_y(widget, state)

    compute_scissor(widget, state)

    compute_text_size(widget, state)
    compute_text_x(widget, state)
    compute_text_y(widget, state)


def compute_width(widget: Widget, state: ModalState, width: float = None) -> float:
    '''Compute the content width of this widget and its children, take width taken in parent, return width taken in parent.'''
    # Get relevant groups of child widgets.
    children = [child for child in widget.children if child.style.display not in (Display.NONE, Display.FLOAT)]
    flex_children = [child for child in children if child.style.width == Size.FLEX]
    fixed_children = [child for child in children if child.style.width != Size.FLEX]
    float_children = [child for child in widget.children if child.style.display == Display.FLOAT]

    # Use the width given to us by our parent.
    if widget.style.width == Size.FLEX:
        if width is None:
            width = state.area.width

        widget.layout.margin.width = width
        widget.layout.border.width = widget.layout.margin.width - widget.style.margin.width
        widget.layout.padding.width = widget.layout.border.width - (widget.style.border_thickness * 2)
        widget.layout.inside.width = widget.layout.padding.width - widget.style.padding.width

    # Use the width of our image.
    elif widget.style.width == Size.IMAGE:
        if widget.image is None:
            raise Exception('Widgets that get size from image must have an image')

        widget.layout.padding.width = widget.image.width
        widget.layout.inside.width = widget.layout.padding.width - widget.style.padding.width
        widget.layout.border.width = widget.layout.padding.width + (widget.style.border_thickness * 2)
        widget.layout.margin.width = widget.layout.border.width + widget.style.margin.width

    # Use the width defined in our own style.
    elif widget.style.width != Size.AUTO:
        widget.layout.padding.width = widget.style.width
        widget.layout.inside.width = widget.layout.padding.width - widget.style.padding.width
        widget.layout.border.width = widget.layout.padding.width + (widget.style.border_thickness * 2)
        widget.layout.margin.width = widget.layout.border.width + widget.style.margin.width

    # Calculate width per stretching child.
    if widget.style.direction == Direction.HORIZONTAL:
        widget.layout.content.width = sum(compute_width(child, state) for child in fixed_children)
        flexible_width = widget.layout.inside.width - widget.layout.content.width
        child_width = (flexible_width / len(flex_children)) if flex_children else 0

    # Stretch children to fit our width.
    elif widget.style.direction == Direction.VERTICAL:
        widget.layout.content.width = max((compute_width(child, state) for child in fixed_children), default=0)
        child_width = widget.layout.inside.width

    # Stretch children to fit the stretchable width.
    for child in flex_children:
        compute_width(child, state, child_width)

    # Fit our width to our children.
    if widget.style.width == Size.AUTO:
        widget.layout.inside.width = widget.layout.content.width
        widget.layout.padding.width = widget.layout.inside.width + widget.style.padding.width
        widget.layout.border.width = widget.layout.padding.width + (widget.style.border_thickness * 2)
        widget.layout.margin.width = widget.layout.border.width + widget.style.margin.width

    # Floating children can take the full width.
    for child in float_children:
        compute_width(child, state, widget.layout.inside.width)

    # Return our width, so our parent can use it to calculate its content width.
    return widget.layout.margin.width


def compute_height(widget: Widget, state: ModalState, height: float = None) -> float:
    '''Compute the content height of this widget and its children, take height taken in parent, return height taken in parent.'''
    # Get relevant groups of child widgets.
    children = [child for child in widget.children if child.style.display not in (Display.NONE, Display.FLOAT)]
    flex_children = [child for child in children if child.style.height == Size.FLEX]
    fixed_children = [child for child in children if child.style.height != Size.FLEX]
    float_children = [child for child in widget.children if child.style.display == Display.FLOAT]

    # Use the height given to us by our parent.
    if widget.style.height == Size.FLEX:
        if height is None:
            height = state.area.height

        widget.layout.margin.height = height
        widget.layout.border.height = widget.layout.margin.height - widget.style.margin.height
        widget.layout.padding.height = widget.layout.border.height - (widget.style.border_thickness * 2)
        widget.layout.inside.height = widget.layout.padding.height - widget.style.padding.height

    # Use the height of our image.
    elif widget.style.height == Size.IMAGE:
        if widget.image is None:
            raise Exception('Widgets that get size from image must have an image')

        widget.layout.padding.height = widget.image.height
        widget.layout.inside.height = widget.layout.padding.height - widget.style.padding.height
        widget.layout.border.height = widget.layout.padding.height + (widget.style.border_thickness * 2)
        widget.layout.margin.height = widget.layout.border.height + widget.style.margin.height

    # Use the height defined in our own style.
    elif widget.style.height != Size.AUTO:
        widget.layout.padding.height = widget.style.height
        widget.layout.inside.height = widget.layout.padding.height - widget.style.padding.height
        widget.layout.border.height = widget.layout.padding.height + (widget.style.border_thickness * 2)
        widget.layout.margin.height = widget.layout.border.height + widget.style.margin.height

    # Calculate height per stretching child.
    if widget.style.direction == Direction.VERTICAL:
        widget.layout.content.height = sum(compute_height(child, state) for child in fixed_children)
        flexible_height = widget.layout.inside.height - widget.layout.content.height
        child_height = (flexible_height / len(flex_children)) if flex_children else 0

    # Stretch children to fit our height.
    elif widget.style.direction == Direction.HORIZONTAL:
        widget.layout.content.height = max((compute_height(child, state) for child in fixed_children), default=0)
        child_height = widget.layout.inside.height

    # Fit our height to our children.
    if widget.style.height == Size.AUTO:
        widget.layout.inside.height = widget.layout.content.height
        widget.layout.padding.height = widget.layout.inside.height + widget.style.padding.height
        widget.layout.border.height = widget.layout.padding.height + (widget.style.border_thickness * 2)
        widget.layout.margin.height = widget.layout.border.height + widget.style.margin.height

    # Stretch children to fit the stretchable height.
    for child in flex_children:
        compute_height(child, state, child_height)

    # Floating children can take the full height.
    for child in float_children:
        compute_height(child, state, widget.layout.inside.height)

    # Return our height, so our parent can use it to calculate its content height.
    return widget.layout.margin.height


def compute_x(widget: Widget, state: ModalState, x: float = None):
    # Get relevant groups of child widgets.
    children = [child for child in widget.children if child.style.display not in (Display.NONE, Display.FLOAT)]
    flex_children = [child for child in children if child.style.width == Size.FLEX]
    float_children = [child for child in widget.children if child.style.display == Display.FLOAT]

    # Keep floating widgets that have no parent inside the 3D view.
    if (widget.style.display == Display.FLOAT) and (x is None):
        widget.style.x = max(0, min(widget.style.x, state.area.width - widget.layout.margin.width))

    # Start at the position defined in style.
    widget.layout.margin.x = widget.style.x

    # Add the position given by our parent.
    if x is not None:
        widget.layout.margin.x += x

    # Calculate positions for other bounding boxes.
    widget.layout.border.x = widget.layout.margin.x + widget.style.margin.left
    widget.layout.padding.x = widget.layout.border.x + widget.style.border_thickness
    widget.layout.inside.x = widget.layout.padding.x + widget.style.padding.left

    # Calculate content position for horizontal layout.
    if widget.style.direction == Direction.HORIZONTAL:
        if flex_children or widget.style.align_x == Align.START:
            widget.layout.content.x = widget.layout.inside.x
        else:
            offset = widget.layout.inside.width - widget.layout.content.width
            if widget.style.align_x == Align.CENTER:
                widget.layout.content.x = widget.layout.inside.x + offset / 2
            elif widget.style.align_x == Align.END:
                widget.layout.content.x = widget.layout.inside.x + offset

        # Calculate position for children.
        child_x = widget.layout.content.x - widget.style.scroll
        for child in children:
            compute_x(child, state, child_x)
            child_x += child.layout.margin.width

    # Calculate content position for vertical layout.
    elif widget.style.direction == Direction.VERTICAL:
        for child in children:
            if widget.style.align_x == Align.START:
                compute_x(child, state, widget.layout.inside.x)
            else:
                offset = widget.layout.inside.width - child.layout.margin.width
                if widget.style.align_x == Align.CENTER:
                    compute_x(child, state, widget.layout.inside.x + offset / 2)
                elif widget.style.align_x == Align.END:
                    compute_x(child, state, widget.layout.inside.x + offset)

    # Floating children are constrained to our inside bounds.
    for child in float_children:
        child.style.x = max(0, min(child.style.x, widget.layout.inside.width - child.layout.margin.width))
        compute_x(child, state, widget.layout.inside.x)


def compute_y(widget: Widget, state: ModalState, y: float = None):
    # Get relevant groups of child widgets.
    children = [child for child in widget.children if child.style.display not in (Display.NONE, Display.FLOAT)]
    flex_children = [child for child in children if child.style.height == Size.FLEX]
    float_children = [child for child in widget.children if child.style.display == Display.FLOAT]

    # Keep floating widgets that have no parent inside the 3D view.
    if (widget.style.display == Display.FLOAT) and (y is None):
        widget.style.y = max(0, min(widget.style.y, state.area.height - widget.layout.margin.height))

    # Start at the position defined in style.
    widget.layout.margin.y = widget.style.y

    # Add the position given by our parent.
    if y is not None:
        widget.layout.margin.y += y

    # Calculate positions for other bounding boxes.
    widget.layout.border.y = widget.layout.margin.y + widget.style.margin.top
    widget.layout.padding.y = widget.layout.border.y + widget.style.border_thickness
    widget.layout.inside.y = widget.layout.padding.y + widget.style.padding.top

    # Calculate content position for vertical layout.
    if widget.style.direction == Direction.VERTICAL:
        if flex_children or widget.style.align_y == Align.START:
            widget.layout.content.y = widget.layout.inside.y
        else:
            offset = widget.layout.inside.height - widget.layout.content.height
            if widget.style.align_y == Align.CENTER:
                widget.layout.content.y = widget.layout.inside.y + offset / 2
            elif widget.style.align_y == Align.END:
                widget.layout.content.y = widget.layout.inside.y + offset

        # Calculate position for children.
        child_y = widget.layout.content.y - widget.style.scroll
        for child in children:
            compute_y(child, state, child_y)
            child_y += child.layout.margin.height

    # Calculate content position for horizontal layout.
    elif widget.style.direction == Direction.HORIZONTAL:
        for child in children:
            if widget.style.align_y == Align.START:
                compute_y(child, state, widget.layout.inside.y)
            else:
                offset = widget.layout.inside.height - child.layout.margin.height
                if widget.style.align_y == Align.CENTER:
                    compute_y(child, state, widget.layout.inside.y + offset / 2)
                elif widget.style.align_y == Align.END:
                    compute_y(child, state, widget.layout.inside.y + offset)

    # Floating children are constrained to our inside bounds.
    for child in float_children:
        child.style.y = max(0, min(child.style.y, widget.layout.inside.height - child.layout.margin.height))
        compute_y(child, state, widget.layout.inside.y)


def compute_scissor(widget: Widget, state: ModalState, area: Area = None):
    if area is not None:
        widget.layout.scissor = area
    elif widget.style.display == Display.SCROLL:
        widget.layout.scissor = widget.layout.padding
    else:
        widget.layout.scissor = None

    for child in widget.children:
        if child.style.display != Display.NONE:
            compute_scissor(child, state, widget.layout.scissor)


def compute_text_size(widget: Widget, state: ModalState):
    if widget.text is not None:
        font_id = widget.text.style.font_id
        blf.size(font_id, widget.text.style.font_size, 72)

        # Get height from capital A because it looks better.
        width = blf.dimensions(font_id, widget.text.data)[0]
        height = blf.dimensions(font_id, 'A')[1]

        widget.layout.text.width = width
        widget.layout.text.height = height

    for child in widget.children:
        if child.style.display != Display.NONE:
            compute_text_size(child, state)


def compute_text_x(widget: Widget, state: ModalState):
    if widget.text is not None:
        if widget.style.align_x == Align.START:
            widget.layout.text.x = widget.layout.inside.x
        else:
            offset = widget.layout.inside.width - widget.layout.text.width
            if widget.style.align_x == Align.CENTER:
                widget.layout.text.x = widget.layout.inside.x + offset / 2
            elif widget.style.align_x == Align.END:
                widget.layout.text.x = widget.layout.inside.x + offset

    for child in widget.children:
        if child.style.display != Display.NONE:
            compute_text_x(child, state)


def compute_text_y(widget: Widget, state: ModalState):
    if widget.text is not None:
        if widget.style.align_y == Align.START:
            widget.layout.text.y = widget.layout.inside.y
        else:
            offset = widget.layout.inside.height - widget.layout.text.height
            if widget.style.align_y == Align.CENTER:
                widget.layout.text.y = widget.layout.inside.y + offset / 2
            elif widget.style.align_y == Align.END:
                widget.layout.text.y = widget.layout.inside.y + offset

    for child in widget.children:
        if child.style.display != Display.NONE:
            compute_text_y(child, state)
