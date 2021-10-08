from __future__ import annotations

from bpy.types import Context

from ..input import EventCopy, ModalState
from ..style import Display, Visibility
from . import Widget


class Screen(Widget):
    '''Window manager for the 3D view.'''

    def __init__(self):
        super().__init__()

        self.style.visibility = Visibility.HIDDEN

    def handle_event(self, state: ModalState, event: EventCopy) -> bool:
        if event.press and event.type in ('LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE', 'BUTTON4MOUSE', 'BUTTON5MOUSE'):
            for child in reversed(self.children):
                if child.style.display != Display.NONE:
                    if child.is_mouse_inside(state):
                        self.children.remove(child)
                        self.children.append(child)
                        break

        return super().handle_event(state, event)

    def compute_layout(self, context: Context):
        self.style.width = context.area.width - self.style.margin.width - self.style.border_thickness * 2
        self.style.height = context.area.height - self.style.margin.height - self.style.border_thickness * 2

        super().compute_layout(context)
