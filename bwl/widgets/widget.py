from __future__ import annotations

from typing import List, Set, Union

from ..content import Image
from ..input import KEYS, MOUSE_BUTTONS, SCROLL, ModalState
from ..layout import Layout, compute_layout
from ..render import compile_shaders, render_widget
from ..style import DEFAULT_STYLE, Display, Style, compute_style


def abstract(func):
    func.abstract = True
    return func


def is_abstract(func) -> bool:
    return getattr(func, 'abstract', False)


class Widget:
    '''Widget which can render and handle events.'''

    def __init__(self, parent: Union[Widget, None] = None):
        if parent is not None:
            parent._children.append(self)

        self._parent: Union[Widget, None] = parent
        self._children: List[Widget] = []

        self._style: Style = DEFAULT_STYLE
        self._layout: Layout = Layout()
        self._pressed: Set[str] = set()

        self._hover: bool = False
        self._active: bool = False
        self._select: bool = False
        self._focus: bool = False

        self.styles: List[Style] = []
        self.image: Union[Image, None] = None
        self.text: Union[str, None] = None

        if not is_abstract(self.on_init):
            self.on_init(parent)

    def compute(self, state: ModalState):
        '''Compute style and layout of this widget and its children.'''
        compute_style(self, state)
        compute_layout(self, state)

    def render(self, state: ModalState):
        '''Render this widget and its children.'''
        compile_shaders(recompile=False)
        render_widget(self, state)

    def handle(self, state: ModalState) -> bool:
        '''Handle event for this widget and its children, return whether it was handled.'''
        if self._style.display == Display.NONE:
            return False

        for child in reversed(self._children):
            if child.handle(state):
                return True

        return self.on_event(state)

    def on_event(self, state: ModalState) -> bool:
        '''Called when this widget receives an event.'''
        if state.event.type == 'MOUSEMOVE':
            hover = self.under_mouse(state)

            if not is_abstract(self.on_mouse_move):
                self.on_mouse_move(state)

            if not is_abstract(self.on_mouse_enter):
                if not self._hover and hover:
                    self.on_mouse_enter(state)

            if not is_abstract(self.on_mouse_leave):
                if self._hover and not hover:
                    self.on_mouse_leave(state)

            self._hover = hover

        elif state.event.type in SCROLL:
            if not is_abstract(self.on_mouse_scroll):
                if self._hover:
                    self.on_mouse_scroll(state)
                    return True

        elif state.event.type in MOUSE_BUTTONS:
            if state.event.value == 'PRESS':
                if self._hover:
                    self._pressed.add(state.event.type)

                    if not is_abstract(self.on_mouse_press):
                        self.on_mouse_press(state)
                        return True

            elif state.event.value == 'RELEASE':
                if state.event.type in self._pressed:
                    self._pressed.remove(state.event.type)

                    if not is_abstract(self.on_mouse_release):
                        self.on_mouse_release(state)
                        return True

            self._active = bool(self._pressed)

        elif state.event.type in KEYS:
            if self._focus:
                if state.event.value == 'PRESS':
                    if not is_abstract(self.on_key_press):
                        self.on_key_press(state)
                        return True

                elif state.event.value == 'RELEASE':
                    if not is_abstract(self.on_key_release):
                        self.on_key_release(state)
                        return True

        else:
            if not is_abstract(self.on_misc):
                self.on_misc(state)
                return True

        return False

    def under_mouse(self, state: ModalState) -> bool:
        '''Check whether the cursor is inside the border of this widget.'''
        if self._layout.scissor is not None:
            if not self._layout.scissor.contains(state.mouse_x, state.mouse_y):
                return False

        if not self._layout.border.contains(state.mouse_x, state.mouse_y):
            return False

        return True

    @abstract
    def on_init(self, parent: Union[Widget, None]):
        ...

    @abstract
    def on_mouse_move(self, state: ModalState):
        ...

    @abstract
    def on_mouse_enter(self, state: ModalState):
        ...

    @abstract
    def on_mouse_leave(self, state: ModalState):
        ...

    @abstract
    def on_mouse_scroll(self, state: ModalState):
        ...

    @abstract
    def on_mouse_press(self, state: ModalState):
        ...

    @abstract
    def on_mouse_release(self, state: ModalState):
        ...

    @abstract
    def on_key_press(self, state: ModalState):
        ...

    @abstract
    def on_key_release(self, state: ModalState):
        ...

    @abstract
    def on_misc(self, state: ModalState):
        ...
