from __future__ import annotations

from ..input import EventCopy, ModalState
from ..style import Direction, Display, Size
from . import Widget

# TODO: Implement resize.


class Window(Widget):
    '''Window which can be moved and resized.'''

    def __init__(self, parent: Widget = None):
        super().__init__(parent=parent)

        self.style.display = Display.FLOAT
        self.style.direction = Direction.VERTICAL

        self.header = Widget(parent=self)
        self.header.style.direction = Direction.HORIZONTAL
        self.header.style.width = Size.FLEX
        self.header.style.height = 32

        self.frame = Widget(parent=self)
        self.frame.style.direction = Direction.VERTICAL
        self.frame.style.width = Size.FLEX
        self.frame.style.height = Size.FLEX

        self.header.subscribe(EventCopy(type='LEFTMOUSE', press=True), self._on_lmb_press, area=True)
        self.header.subscribe(EventCopy(type='LEFTMOUSE', press=False), self._on_lmb_release, area=False)

        self._mouse_offset_x = 0
        self._mouse_offset_y = 0

    def handle_event(self, state: ModalState, event: EventCopy) -> bool:
        if super().handle_event(state, event):
            return True

        # Consume press events if cursor is inside.
        elif event.press:
            return self.is_mouse_inside(state)

    def _on_lmb_press(self, state: ModalState) -> bool:
        self.header.subscribe(EventCopy(type='MOUSEMOVE'), self._on_mouse_move, area=False)
        self._mouse_offset_x = state.mouse_x - self.style.x
        self._mouse_offset_y = state.mouse_y - self.style.y
        return True

    def _on_lmb_release(self, state: ModalState) -> bool:
        self.header.unsubscribe(EventCopy(type='MOUSEMOVE'))
        return False

    def _on_mouse_move(self, state: ModalState) -> bool:
        self.style.x = min(
            state.context.area.width - self.layout.margin.width,
            max(0, state.mouse_x - self._mouse_offset_x),
        )
        self.style.y = min(
            state.context.area.height - self.layout.margin.height,
            max(0, state.mouse_y - self._mouse_offset_y),
        )
        return True
