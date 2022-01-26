from __future__ import annotations

from bpy.types import Event


def is_move(event: Event) -> bool:
    return event.type in _EventTypes.move


def is_mouse(event: Event) -> bool:
    return event.type in _EventTypes.mouse


def is_scroll(event: Event) -> bool:
    return event.type in _EventTypes.scroll


def is_keyboard(event: Event) -> bool:
    return event.type in _EventTypes.keyboard


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
