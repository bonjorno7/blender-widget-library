from __future__ import annotations

from bpy.types import Context

from ..input import EventCopy, ModalState
from ..style import Display, Visibility
from . import Widget


class Screen(Widget):
    '''Window manager for the 3D view.'''

    def __init__(self):
        super().__init__()

        # Don't render the screen itself.
        self.style.visibility = Visibility.HIDDEN

    def handle_event(self, state: ModalState, event: EventCopy) -> bool:
        # Mouse clicks bring the clicked widget to the front.
        if event.press and event.type in ('LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE', 'BUTTON4MOUSE', 'BUTTON5MOUSE'):
            for child in reversed(self.children):
                if child.style.display != Display.NONE:
                    if child.is_mouse_inside(state):
                        self.children.remove(child)
                        self.children.append(child)
                        break

        return super().handle_event(state, event)

    def compute_layout(self, context: Context):
        # Stretch screen to fill the 3D view.
        self.style.width = context.area.width - self.style.margin.width - self.style.border_thickness * 2
        self.style.height = context.area.height - self.style.margin.height - self.style.border_thickness * 2

        super().compute_layout(context)
