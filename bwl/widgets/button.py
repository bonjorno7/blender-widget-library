from __future__ import annotations

from typing import Callable, Union

from ..input import ModalEvent, ModalState, Subscription
from ..style import Style
from . import Widget


class Button(Widget):

    def __init__(self, parent: Union[Widget, None] = None):
        super().__init__(parent)

        self.style_hover = Style()
        self.style_press = Style()
        self._style_backup: Style = None

        self.subscribe(
            ModalEvent(type='LEFTMOUSE', value='PRESS'),
            Subscription(self._on_press, area=True),
        )
        self.subscribe(
            ModalEvent(type='LEFTMOUSE', value='RELEASE'),
            Subscription(self._on_release, area=False),
        )
        self.subscribe(
            ModalEvent(type='MOUSEMOVE'),
            Subscription(self._on_mouse_move, area=False),
        )

        self._callback: Union[Callable, None] = None
        self._is_pressed = False
        self._is_hovering = False

    def set_callback(self, function: Callable):
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
                self.style = self._style_backup

            return True

        return False

    def _on_mouse_move(self, state: ModalState) -> bool:
        is_mouse_inside = self.is_mouse_inside(state)

        if not self._is_hovering and is_mouse_inside:
            self._is_hovering = True
            self._on_begin_hover()
            return True

        elif self._is_hovering and not is_mouse_inside:
            self._is_hovering = False
            self._on_end_hover()
            return True

        return False

    def _on_begin_hover(self):
        if not self._is_pressed:
            self._style_backup = self.style
            self.style = self.style_hover

    def _on_end_hover(self):
        if not self._is_pressed:
            self.style = self._style_backup
