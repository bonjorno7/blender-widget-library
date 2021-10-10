from __future__ import annotations

from ..input import ModalEvent, ModalState, Subscription
from ..style import Display, Size, Visibility
from . import Widget


class Screen(Widget):
    '''Window manager for the 3D view.'''

    def __init__(self):
        # Screen does not need a parent.
        super().__init__()

        # Don't render the screen itself.
        self.style.visibility = Visibility.HIDDEN

        # Stretch the screen to the 3D view.
        self.style.width = Size.FLEX
        self.style.height = Size.FLEX

        # Subscribe to every mouse click, handle before children.
        for type in ('LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE', 'BUTTON4MOUSE', 'BUTTON5MOUSE'):
            self.subscribe(
                ModalEvent(type, value='PRESS'),
                Subscription(self._on_click, reverse=True),
            )

    def _on_click(self, state: ModalState) -> bool:
        # Mouse clicks bring the clicked widget to the front.
        for child in reversed(self.children):
            if child.style.display == Display.FLOAT:
                if child.is_mouse_inside(state):
                    self.children.remove(child)
                    self.children.append(child)
                    break

        # Allow other widgets to handle this event too.
        return False
