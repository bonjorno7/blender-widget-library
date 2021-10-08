from __future__ import annotations

from typing import Set, Union

from bpy.types import Context, Event


class ModalState:
    '''Class to keep track of mouse position and pressed keys.'''

    def __init__(self, context: Context, event: Event):
        self.context = context
        self.event = event

        self.mouse_x = event.mouse_region_x
        self.mouse_y = context.area.height - event.mouse_region_y

        self.mouse_prev_x = self.mouse_x
        self.mouse_prev_y = self.mouse_y

        self.mouse_delta_x = 0
        self.mouse_delta_y = 0

        self.pressed: Set[str] = set()

    def update(self, context: Context, event: Event):
        self.context = context
        self.event = event

        self.mouse_prev_x = self.mouse_x
        self.mouse_prev_y = self.mouse_y

        self.mouse_x = event.mouse_region_x
        self.mouse_y = context.area.height - event.mouse_region_y

        self.mouse_delta_x = self.mouse_x - self.mouse_prev_x
        self.mouse_delta_y = self.mouse_y - self.mouse_prev_y

        if event.value == 'PRESS':
            self.pressed.add(event.type)
        elif event.type in self.pressed:
            self.pressed.remove(event.type)


class EventCopy:
    '''Copy of a Blender event. Used to send inputs to widgets.

    Mouse move events ignore `press` `shift` `ctrl` `alt`.

    Release events ignore `shift` `ctrl` `alt`.
    '''

    def __init__(self, type: str, press: bool = False, shift: bool = False, ctrl: bool = False, alt: bool = False):
        if type == 'MOUSEMOVE':
            press, shift, ctrl, alt = (None, None, None, None)
        elif not press:
            shift, ctrl, alt = (None, None, None)

        self._type = type
        self._press = press
        self._shift = shift
        self._ctrl = ctrl
        self._alt = alt

        self._hash = hash((self._type, self._press, self._shift, self._ctrl, self._alt))

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: EventCopy) -> bool:
        return hash(self) == hash(other)

    @property
    def type(self) -> str:
        return self._type

    @property
    def press(self) -> Union[bool, None]:
        return self._press

    @property
    def shift(self) -> Union[bool, None]:
        return self._shift

    @property
    def ctrl(self) -> Union[bool, None]:
        return self._ctrl

    @property
    def alt(self) -> Union[bool, None]:
        return self._alt

    @classmethod
    def from_event(cls, event: Event) -> EventCopy:
        return EventCopy(event.type, (event.value == 'PRESS'), event.shift, event.ctrl, event.alt)
