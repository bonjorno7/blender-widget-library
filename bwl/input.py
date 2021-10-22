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

        self.is_move = self.event.type in _EventTypes.move
        self.is_mouse = self.event.type in _EventTypes.mouse
        self.is_scroll = self.event.type in _EventTypes.scroll
        self.is_keyboard = self.event.type in _EventTypes.keyboard


def under_mouse(widget: Widget, state: ModalState) -> bool:
    '''Check whether the cursor is inside the border of the given widget.'''
    if widget._layout.scissor is not None:
        if not widget._layout.scissor.contains(state.mouse_x, state.mouse_y):
            return False

    if not widget._layout.border.contains(state.mouse_x, state.mouse_y):
        return False

    return True


class _EventTypes:
    move = {
        'MOUSEMOVE',
    }

    mouse = {
        'LEFTMOUSE',
        'RIGHTMOUSE',
        'MIDDLEMOUSE',
        'BUTTON4MOUSE',
        'BUTTON5MOUSE',
        'BUTTON6MOUSE',
        'BUTTON7MOUSE',
    }

    scroll = {
        'WHEELUPMOUSE',
        'WHEELDOWNMOUSE',
        'WHEELINMOUSE',
        'WHEELOUTMOUSE',
    }

    keyboard = {
        'A',
        'B',
        'C',
        'D',
        'E',
        'F',
        'G',
        'H',
        'I',
        'J',
        'K',
        'L',
        'M',
        'N',
        'O',
        'P',
        'Q',
        'R',
        'S',
        'T',
        'U',
        'V',
        'W',
        'X',
        'Y',
        'Z',
        'ZERO',
        'ONE',
        'TWO',
        'THREE',
        'FOUR',
        'FIVE',
        'SIX',
        'SEVEN',
        'EIGHT',
        'NINE',
        'LEFT_CTRL',
        'LEFT_ALT',
        'LEFT_SHIFT',
        'RIGHT_ALT',
        'RIGHT_CTRL',
        'RIGHT_SHIFT',
        'OSKEY',
        'GRLESS',
        'ESC',
        'TAB',
        'RET',
        'SPACE',
        'LINE_FEED',
        'BACK_SPACE',
        'DEL',
        'SEMI_COLON',
        'PERIOD',
        'COMMA',
        'QUOTE',
        'ACCENT_GRAVE',
        'MINUS',
        'PLUS',
        'SLASH',
        'BACK_SLASH',
        'EQUAL',
        'LEFT_BRACKET',
        'RIGHT_BRACKET',
        'LEFT_ARROW',
        'DOWN_ARROW',
        'RIGHT_ARROW',
        'UP_ARROW',
        'NUMPAD_2',
        'NUMPAD_4',
        'NUMPAD_6',
        'NUMPAD_8',
        'NUMPAD_1',
        'NUMPAD_3',
        'NUMPAD_5',
        'NUMPAD_7',
        'NUMPAD_9',
        'NUMPAD_PERIOD',
        'NUMPAD_SLASH',
        'NUMPAD_ASTERIX',
        'NUMPAD_0',
        'NUMPAD_MINUS',
        'NUMPAD_ENTER',
        'NUMPAD_PLUS',
        'F1',
        'F2',
        'F3',
        'F4',
        'F5',
        'F6',
        'F7',
        'F8',
        'F9',
        'F10',
        'F11',
        'F12',
        'F13',
        'F14',
        'F15',
        'F16',
        'F17',
        'F18',
        'F19',
        'F20',
        'F21',
        'F22',
        'F23',
        'F24',
        'PAUSE',
        'INSERT',
        'HOME',
        'PAGE_UP',
        'PAGE_DOWN',
        'END',
    }
