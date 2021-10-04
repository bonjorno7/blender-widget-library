from __future__ import annotations

from typing import TYPE_CHECKING

from .style import Align, Direction, Display, Justify, Size

if TYPE_CHECKING:
    from .widget import Widget


class Area:
    '''Area defined by position and size.'''

    def __init__(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, x: float, y: float) -> bool:
        '''Check whether this area contains the given coordinates.'''
        return (self.x < x < self.x + self.width) and (self.y < y < self.y + self.height)


class Layout:
    '''Position and size of a widget.'''

    def __init__(self) -> None:
        self.content = Area()
        self.inside = Area()
        self.padding = Area()
        self.border = Area()
        self.margin = Area()


def compute_layout(widget: Widget):
    '''Compute layout for the given widget and its children.'''
    # Calculate size first because it affects position.
    compute_width(widget)
    compute_height(widget)
    compute_x(widget)
    compute_y(widget)


def compute_width(widget: Widget, width: float = None) -> float:
    '''Compute the content width of this widget and its children, take width taken in parent, return width taken in parent.'''
    # Get relevant groups of child widgets.
    children = [child for child in widget.children if child.style.display != Display.NONE]
    flex_children = [child for child in children if child.style.width == Size.FLEX]
    fixed_children = [child for child in children if child.style.width != Size.FLEX]

    # Use the width given to us by our parent.
    if widget.style.width == Size.FLEX:
        if width is None:
            raise Exception('Flex widgets must get size from parent')

        widget.layout.margin.width = width
        widget.layout.border.width = widget.layout.margin.width - widget.style.margin.width
        widget.layout.padding.width = widget.layout.border.width - (widget.style.border_thickness * 2)
        widget.layout.inside.width = widget.layout.padding.width - widget.style.padding.width

    # Use the width defined in our own style.
    elif widget.style.width != Size.AUTO:
        widget.layout.padding.width = widget.style.width
        widget.layout.inside.width = widget.layout.padding.width - widget.style.padding.width
        widget.layout.border.width = widget.layout.padding.width + (widget.style.border_thickness * 2)
        widget.layout.margin.width = widget.layout.border.width + widget.style.margin.width

    # Calculate width per stretching child.
    if widget.style.direction == Direction.HORIZONTAL:
        widget.layout.content.width = sum(compute_width(child) for child in fixed_children)
        flexible_width = widget.layout.inside.width - widget.layout.content.width
        child_width = (flexible_width / len(flex_children)) if flex_children else 0

    # Stretch children to fit our width.
    elif widget.style.direction == Direction.VERTICAL:
        widget.layout.content.width = max((compute_width(child) for child in fixed_children), default=0)
        child_width = widget.layout.inside.width

    # Stretch children to fit the stretchable width.
    for child in flex_children:
        compute_width(child, child_width)

    # Fit our width to our children.
    if widget.style.width == Size.AUTO:
        widget.layout.inside.width = widget.layout.content.width
        widget.layout.padding.width = widget.layout.inside.width + widget.style.padding.width
        widget.layout.border.width = widget.layout.padding.width + (widget.style.border_thickness * 2)
        widget.layout.margin.width = widget.layout.border.width + widget.style.margin.width

    # Return our width, so our parent can use it to calculate its content width.
    return widget.layout.margin.width


def compute_height(widget: Widget, height: float = None) -> float:
    '''Compute the content height of this widget and its children, take height taken in parent, return height taken in parent.'''
    # Get relevant groups of child widgets.
    children = [child for child in widget.children if child.style.display != Display.NONE]
    flex_children = [child for child in children if child.style.height == Size.FLEX]
    fixed_children = [child for child in children if child.style.height != Size.FLEX]

    # Use the height given to us by our parent.
    if widget.style.height == Size.FLEX:
        if height is None:
            raise Exception('Flex widgets must get size from parent')

        widget.layout.margin.height = height
        widget.layout.border.height = widget.layout.margin.height - widget.style.margin.height
        widget.layout.padding.height = widget.layout.border.height - (widget.style.border_thickness * 2)
        widget.layout.inside.height = widget.layout.padding.height - widget.style.padding.height

    # Use the height defined in our own style.
    elif widget.style.height != Size.AUTO:
        widget.layout.padding.height = widget.style.height
        widget.layout.inside.height = widget.layout.padding.height - widget.style.padding.height
        widget.layout.border.height = widget.layout.padding.height + (widget.style.border_thickness * 2)
        widget.layout.margin.height = widget.layout.border.height + widget.style.margin.height

    # Calculate height per stretching child.
    if widget.style.direction == Direction.VERTICAL:
        widget.layout.content.height = sum(compute_height(child) for child in fixed_children)
        flexible_height = widget.layout.inside.height - widget.layout.content.height
        child_height = (flexible_height / len(flex_children)) if flex_children else 0

    # Stretch children to fit our height.
    elif widget.style.direction == Direction.HORIZONTAL:
        widget.layout.content.height = max((compute_height(child) for child in fixed_children), default=0)
        child_height = widget.layout.inside.height

    # Fit our height to our children.
    if widget.style.height == Size.AUTO:
        widget.layout.inside.height = widget.layout.content.height
        widget.layout.padding.height = widget.layout.inside.height + widget.style.padding.height
        widget.layout.border.height = widget.layout.padding.height + (widget.style.border_thickness * 2)
        widget.layout.margin.height = widget.layout.border.height + widget.style.margin.height

    # Stretch children to fit the stretchable height.
    for child in flex_children:
        compute_height(child, child_height)

    # Return our height, so our parent can use it to calculate its content height.
    return widget.layout.margin.height


def compute_x(widget: Widget, x: float = None):
    # Get relevant groups of child widgets.
    children = [child for child in widget.children if child.style.display != Display.NONE]
    flex_children = [child for child in children if child.style.width == Size.FLEX]

    # Start at the position defined in style.
    widget.layout.margin.x = widget.style.x

    # Add the position given by our parent.
    if x is not None:
        widget.layout.margin.x += x

    # Calculate positions for other bounding boxes.
    widget.layout.border.x = widget.layout.margin.x + widget.style.margin.left
    widget.layout.padding.x = widget.layout.border.x + widget.style.border_thickness
    widget.layout.inside.x = widget.layout.padding.x + widget.style.padding.left

    # Calculate content position based on justify.
    if widget.style.direction == Direction.HORIZONTAL:
        if flex_children or widget.style.justify in (Justify.START, Justify.SPACE):
            widget.layout.content.x = widget.layout.inside.x
        else:
            offset = widget.layout.inside.width - widget.layout.content.width
            if widget.style.justify == Justify.CENTER:
                widget.layout.content.x = widget.layout.inside.x - round(offset / 2)
            elif widget.style.justify == Justify.END:
                widget.layout.content.x = widget.layout.inside.x - offset

        # Calculate gap for justify space.
        if widget.style.justify == Justify.SPACE and not flex_children and len(children) > 1:
            offset = round((widget.layout.inside.width - widget.layout.content.width) / (len(children) - 1))
        else:
            offset = 0

        # Calculate position for children.
        child_x = widget.layout.content.x
        for child in children:
            compute_x(child, child_x)
            child_x += child.layout.margin.width + offset

    # Calculate content position based on align.
    elif widget.style.direction == Direction.VERTICAL:
        for child in children:
            if widget.style.align == Align.START:
                compute_x(child, widget.layout.inside.x)
            else:
                offset = widget.layout.inside.width - child.layout.margin.width
                if widget.style.align == Align.CENTER:
                    compute_x(child, widget.layout.inside.x + round(offset / 2))
                elif widget.style.align == Align.END:
                    compute_x(child, widget.layout.inside.x + offset)


def compute_y(widget: Widget, y: float = None):
    # Get relevant groups of child widgets.
    children = [child for child in widget.children if child.style.display != Display.NONE]
    flex_children = [child for child in children if child.style.height == Size.FLEX]

    # Start at the position defined in style.
    widget.layout.margin.y = widget.style.y

    # Add the position given by our parent.
    if y is not None:
        widget.layout.margin.y += y

    # Calculate positions for other bounding boxes.
    widget.layout.border.y = widget.layout.margin.y + widget.style.margin.top
    widget.layout.padding.y = widget.layout.border.y + widget.style.border_thickness
    widget.layout.inside.y = widget.layout.padding.y + widget.style.padding.top

    # Calculate content position based on justify.
    if widget.style.direction == Direction.VERTICAL:
        if flex_children or widget.style.justify in (Justify.START, Justify.SPACE):
            widget.layout.content.y = widget.layout.inside.y
        else:
            offset = widget.layout.inside.height - widget.layout.content.height
            if widget.style.justify == Justify.CENTER:
                widget.layout.content.y = widget.layout.inside.y - round(offset / 2)
            elif widget.style.justify == Justify.END:
                widget.layout.content.y = widget.layout.inside.y - offset

        # Calculate gap for justify space.
        if widget.style.justify == Justify.SPACE and not flex_children and len(children) > 1:
            offset = round((widget.layout.inside.height - widget.layout.content.height) / (len(children) - 1))
        else:
            offset = 0

        # Calculate position for children.
        child_y = widget.layout.content.y
        for child in children:
            compute_y(child, child_y)
            child_y += child.layout.margin.height + offset

    # Calculate content position based on align.
    elif widget.style.direction == Direction.HORIZONTAL:
        for child in children:
            if widget.style.align == Align.START:
                compute_y(child, widget.layout.inside.y)
            else:
                offset = widget.layout.inside.height - child.layout.margin.height
                if widget.style.align == Align.CENTER:
                    compute_y(child, widget.layout.inside.y + round(offset / 2))
                elif widget.style.align == Align.END:
                    compute_y(child, widget.layout.inside.y + offset)
