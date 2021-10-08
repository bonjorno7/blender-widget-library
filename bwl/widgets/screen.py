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

    def compute_layout(self, context: Context):
        self.style.width = context.area.width - self.style.margin.width - self.style.border_thickness * 2
        self.style.height = context.area.height - self.style.margin.height - self.style.border_thickness * 2
        super().compute_layout(context)

    def handle_event(self, state: ModalState, event: EventCopy) -> bool:
        children = [child for child in self.children if child.style.display != Display.NONE]

        # Mouse clicks focus the clicked widget.
        if event.type in ('LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE', 'BUTTON4MOUSE', 'BUTTON5MOUSE') and event.press:
            for child in reversed(children):
                if child.is_mouse_inside(state):
                    self.children.remove(child)
                    self.children.append(child)

                    child.handle_event(state, event)
                    return True

        # Mouse scroll and move are allowed on non-focused widgets.
        elif event.type in ('WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'MOUSEMOVE'):
            for child in reversed(children):
                if child.is_mouse_inside(state):
                    child.handle_event(state, event)
                    return True

        # Other events are handled by the focused widget.
        else:
            if children and children[-1].handle_event(state, event):
                return True

            # If the cursor is on any widget, we consume the event.
            for child in reversed(children):
                if child.is_mouse_inside(state):
                    return True

        # If the event was not handled, it is passed through to Blender.
        return False
