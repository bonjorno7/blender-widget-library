from __future__ import annotations

from enum import Enum, auto
from typing import Union

import bpy

from ..input import ModalEvent, ModalState, Subscription
from ..style import Direction, Display, Size, Visibility
from . import Widget


class Axis(Enum):
    X = auto()
    Y = auto()
    BOTH = auto()


class ResizeHandle(Widget):

    def __init__(
        self,
        parent: Union[Widget, None] = None,
        resize_widget: Resizable = None,
        size: float = 5,
        axis: Axis = Axis.X,
        move_x: bool = False,
        move_y: bool = False,
    ):
        super().__init__(parent=parent)

        self.resize_widget = resize_widget
        self.axis = axis
        self.move_x = move_x
        self.move_y = move_y

        self.style.visibility = Visibility.HIDDEN
        self.style.height = size if (axis in (Axis.Y, Axis.BOTH)) else Size.FLEX
        self.style.width = size if (axis in (Axis.X, Axis.BOTH)) else Size.FLEX

        self.subscribe(
            ModalEvent(type='LEFTMOUSE', value='PRESS'),
            Subscription(self._on_lmb_press, area=True),
        )
        self.subscribe(
            ModalEvent(type='LEFTMOUSE', value='RELEASE'),
            Subscription(self._on_lmb_release, area=False),
        )
        self.subscribe(
            ModalEvent(type='MOUSEMOVE'),
            Subscription(self._on_mouse_move, area=False),
        )

        self._cursor = 'MOVE_X' if (axis == Axis.X) else 'MOVE_Y' if (axis == Axis.Y) else 'SCROLL_XY'

        self._is_hovering = False
        self._is_dragging = False

        self._original_x = 0
        self._original_y = 0
        self._original_width = 0
        self._original_height = 0

    def _on_lmb_press(self, state: ModalState) -> bool:
        self._is_dragging = True
        self._original_x = self.resize_widget.style.x
        self._original_y = self.resize_widget.style.y
        self._original_width = self.resize_widget.style.width
        self._original_height = self.resize_widget.style.height
        return True

    def _on_lmb_release(self, state: ModalState) -> bool:
        self._is_dragging = False
        return False

    def _on_mouse_move(self, state: ModalState) -> bool:
        if self._is_dragging:
            if self.axis in (Axis.X, Axis.BOTH):
                x = self._original_x
                width = 0

                if self.move_x:
                    x = state.mouse_x
                    width = self._original_width + self._original_x - state.mouse_x
                else:
                    width = state.mouse_x - self._original_x

                if width >= self.resize_widget.min_width:
                    self.resize_widget.style.x = x
                    self.resize_widget.style.width = width

            if self.axis in (Axis.Y, Axis.BOTH):
                y = self._original_y
                height = 0

                if self.move_y:
                    y = state.mouse_y
                    height = self._original_height + self._original_y - state.mouse_y
                else:
                    height = state.mouse_y - self._original_y

                if height >= self.resize_widget.min_height:
                    self.resize_widget.style.y = y
                    self.resize_widget.style.height = height

            return True

        else:
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
        bpy.context.window.cursor_set(self._cursor)

    def _on_end_hover(self):
        bpy.context.window.cursor_set('DEFAULT')


class Resizable(Widget):

    def __init__(self, parent: Union[Widget, None] = None, handle_size: float = 5):
        super().__init__(parent=parent)

        self.min_width = 20
        self.min_height = 20

        resize_handle_container = Widget(parent=self)
        resize_handle_container.style.display = Display.FLOAT
        resize_handle_container.style.visibility = Visibility.HIDDEN
        resize_handle_container.style.direction = Direction.HORIZONTAL
        resize_handle_container.style.width = Size.FLEX
        resize_handle_container.style.height = Size.FLEX

        left_container = Widget(parent=resize_handle_container)
        left_container.style.visibility = Visibility.HIDDEN
        left_container.style.direction = Direction.VERTICAL
        left_container.style.width = handle_size
        left_container.style.height = Size.FLEX

        center_container = Widget(parent=resize_handle_container)
        center_container.style = left_container.style.copy()
        center_container.style.width = Size.FLEX

        right_container = Widget(parent=resize_handle_container)
        right_container.style = left_container.style

        handle_top_left = ResizeHandle(left_container, self, handle_size, Axis.BOTH, True, True)
        handle_left = ResizeHandle(left_container, self, handle_size, Axis.X, True, False)
        handle_bottom_left = ResizeHandle(left_container, self, handle_size, Axis.BOTH, True, False)
        handle_top = ResizeHandle(center_container, self, handle_size, Axis.Y, False, True)

        center_spacer = Widget(parent=center_container)
        center_spacer.style.visibility = Visibility.HIDDEN
        center_spacer.style.width = Size.FLEX
        center_spacer.style.height = Size.FLEX

        handle_bottom = ResizeHandle(center_container, self, handle_size, Axis.Y, False, False)
        handle_top_right = ResizeHandle(right_container, self, handle_size, Axis.BOTH, False, True)
        handle_right = ResizeHandle(right_container, self, handle_size, Axis.X, False, False)
        handle_bottom_right = ResizeHandle(right_container, self, handle_size, Axis.BOTH, False, False)
