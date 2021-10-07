from __future__ import annotations

from bpy.types import Context

from ..input import ModalEvent, ModalState
from ..style import Display, Visibility
from . import Widget


class Screen(Widget):
    '''Window manager for the 3D view.'''

    def __init__(self):
        super().__init__()
        self.style.visibility = Visibility.HIDDEN

    def compute_layout(self, context: Context):
        self.style.width = context.area.width - self.style.margin.width - self.style.border_thickness * 2
        self.style.height = context.area.height - self.style.margin.height - self.style.border_thickness * 2
        super().compute_layout(context)

    def handle_event(self, state: ModalState, event: ModalEvent) -> bool:
        children = [child for child in self.children if child.style.display != Display.NONE]
        if not children:
            return False

        # Mouse clicks focus the clicked window.
        if event.type in ('LEFTMOUSE', 'RIGHTMOUSE') and event.value == 'PRESS':
            for child in reversed(children):
                if child.layout.border.contains(state.mouse_x, state.mouse_y):
                    self.children.remove(child)
                    self.children.append(child)

                    # Mouse clicks inside a window are handled exclusively.
                    child.handle_event(state, event)
                    return True

        # Other events are handled by the focused window.
        return children[-1].handle_event(state, event)
