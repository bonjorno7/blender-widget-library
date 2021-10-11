from __future__ import annotations

from typing import Callable

from bpy.types import Context, Event

from .layout import Area


class ModalState:
    '''Current operator state.'''

    def __init__(self, context: Context, event: Event):
        self.context = context
        self.area = Area(0, 0, context.area.width, context.area.height)

        self.event = event
        self.mouse_x = event.mouse_region_x
        self.mouse_y = context.area.height - event.mouse_region_y


class ModalEvent:
    '''Event which widgets can subscribe to.'''

    def __init__(self, type: str = None, value: str = None, shift: bool = None, ctrl: bool = None, alt: bool = None):
        self.type = type
        self.value = value
        self.shift = shift
        self.ctrl = ctrl
        self.alt = alt

    # We need both __hash__ and __eq__ to use this class as dictionary key.
    def __hash__(self) -> int:
        return hash((self.type, self.value, self.shift, self.ctrl, self.alt))

    def __eq__(self, other: ModalEvent) -> bool:
        return hash(self) == hash(other)

    def compare(self, event: Event) -> bool:
        '''Compare this ModalEvent to a Blender Event.'''
        return all(
            (a is None) or (a == b) for (a, b) in (
                (self.type, event.type),
                (self.value, event.value),
                (self.shift, event.shift),
                (self.ctrl, event.ctrl),
                (self.alt, event.alt),
            )
        )


class Subscription:
    '''Event subscription for a widget.'''

    def __init__(self, callback: Callable[[ModalState], bool], area: bool = True, reverse: bool = False):
        self.callback = callback
        self.area = area
        self.reverse = reverse
