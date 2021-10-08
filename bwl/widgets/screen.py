from __future__ import annotations

from bpy.types import Context

from ..input import EventCopy, ModalState
from ..style import Display, Visibility
from . import Widget

# TODO: Allow scroll events on windows that are not focused.


class Screen(Widget):
    '''Window manager for the 3D view.'''

    def __init__(self):
        super().__init__()
        self.style.visibility = Visibility.HIDDEN

    def compute_layout(self, context: Context):
        self.style.width = context.area.width - self.style.margin.width - self.style.border_thickness * 2
        self.style.height = context.area.height - self.style.margin.height - self.style.border_thickness * 2
        super().compute_layout(context)

    def handle_event(self, state: ModalState, event: EventCopy) -> bool:
        children = [child for child in self.children if child.style.display != Display.NONE]

        # You should not call this on a screen with no children.
        if not children:
            return False

        # Mouse clicks focus the clicked widget.
        if event.type in ('LEFTMOUSE', 'RIGHTMOUSE') and event.press:
            for child in reversed(children):
                if child.is_mouse_inside(state):
                    self.children.remove(child)
                    self.children.append(child)

                    # Mouse clicks inside a widget are handled exclusively.
                    child.handle_event(state, event)
                    return True

        # Other events are handled by the focused widget.
        if children[-1].handle_event(state, event):
            return True

        # If the cursor is on a widget, we always consider the event handled.
        for child in reversed(children):
            if child.is_mouse_inside(state):
                return True

        return False
