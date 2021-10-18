from __future__ import annotations

from bpy.types import Context, Event, Operator

from .layout import Area


class ModalState:
    '''Current operator state.'''

    def __init__(self, operator: Operator, context: Context, event: Event):
        self.operator = operator
        self.context = context
        self.event = event

        self.area = Area(0, 0, context.area.width, context.area.height)
        self.mouse_x = event.mouse_region_x
        self.mouse_y = context.area.height - event.mouse_region_y


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
