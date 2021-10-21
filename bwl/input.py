from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Context, Event, Operator

from .layout import Area

if TYPE_CHECKING:
    from .widgets import Widget


class ModalState:
    '''Current operator state.'''

    def __init__(self, operator: Operator, context: Context, event: Event):
        self.operator = operator
        self.context = context
        self.event = event

        self.area = Area(0, 0, context.area.width, context.area.height)
        self.mouse_x = event.mouse_region_x
        self.mouse_y = context.area.height - event.mouse_region_y


def under_mouse(widget: Widget, state: ModalState) -> bool:
    '''Check whether the cursor is inside the border of the given widget.'''
    if widget._layout.scissor is not None:
        if not widget._layout.scissor.contains(state.mouse_x, state.mouse_y):
            return False

    if not widget._layout.border.contains(state.mouse_x, state.mouse_y):
        return False

    return True


SCROLL = {
    'WHEELUPMOUSE',
    'WHEELDOWNMOUSE',
}

MOUSE_BUTTONS = {
    'LEFTMOUSE',
    'RIGHTMOUSE',
    'MIDDLEMOUSE',
    'BUTTON4MOUSE',
    'BUTTON5MOUSE',
    'BUTTON6MOUSE',
    'BUTTON7MOUSE',
}

# TODO: Add all the keys.
KEYS = {
    'A',
    'B',
    'C',
    'ESC',
}
