from __future__ import annotations

from typing import Set

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


class ModalEvent:
    '''Class for comparing against Blender events.'''

    def __init__(self, type: str, value: str = None, shift: bool = False, ctrl: bool = False, alt: bool = False):
        '''If value is None, it will not be checked.'''
        self._hash = hash((type, value, shift, ctrl, alt))
        self._type = type
        self._value = value
        self._shift = shift
        self._ctrl = ctrl
        self._alt = alt

    def __hash__(self) -> int:
        '''Get the hash of this event, for use as dictionary key.'''
        return self._hash

    def check(self, state: ModalState):
        '''Check whether this event is triggered in the given state.'''
        return all(
            (a is None) or (a == b) for (a, b) in (
                (self._type, state.event.type),
                (self._value, state.event.value),
                (self._shift, state.event.shift),
                (self._ctrl, state.event.ctrl),
                (self._alt, state.event.alt),
            )
        )
