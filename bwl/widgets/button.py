from __future__ import annotations

from typing import Callable, Union

from ..input import EventCopy, ModalState
from ..style import Style
from . import Widget


class Button(Widget):

    def __init__(self, parent: Widget = None):
        super().__init__(parent)

        self.style_hover = Style()
        self.style_press = Style()
        self._style: Style = None

        self.subscribe(EventCopy(type='LEFTMOUSE', press=True), self._on_press, area=True)
        self.subscribe(EventCopy(type='LEFTMOUSE', press=False), self._on_release, area=False)
        self.subscribe(EventCopy(type='MOUSEMOVE'), self._on_mouse_move, area=False)

        self._callback: Union[Callable, None] = None
        self._is_pressed = False
        self._is_hovering = False

    def setup_callback(self, function: Callable):
        self._callback = function

    def _on_press(self, state: ModalState) -> bool:
        self._is_pressed = True
        self.style = self.style_press
        return True

    def _on_release(self, state: ModalState) -> bool:
        if self._is_pressed:
            self._is_pressed = False

            if self._is_hovering:
                self.style = self.style_hover

                if self._callback is None:
                    raise Exception('Button must have a callback function.')

                self._callback()

            else:
                self.style = self._style

            return True

        return False

    def _on_mouse_move(self, state: ModalState) -> bool:
        is_mouse_inside = self.is_mouse_inside(state)

        if (not self._is_hovering) and is_mouse_inside:
            self._is_hovering = True
            self._on_begin_hover()
            return True

        elif self._is_hovering and (not is_mouse_inside):
            self._is_hovering = False
            self._on_end_hover()
            return True

        return False

    def _on_begin_hover(self):
        if not self._is_pressed:
            self._style = self.style
            self.style = self.style_hover

    def _on_end_hover(self):
        if not self._is_pressed:
            self.style = self._style
