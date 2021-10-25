from __future__ import annotations

from typing import List, Set, Tuple, Union

from .content import Texture
from .input import ModalState
from .layout import Layout, compute_layout
from .render import compile_shaders, render_widget
from .style import DEFAULT_STYLE, Display, Style, compute_style
from .utils import abstract, is_abstract


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
        self.texture: Union[Texture, None] = None
        self.text: Union[str, None] = None

    @property
    def parent(self) -> Union[Widget, None]:
        '''The parent of this widget.'''
        return self._parent

    @property
    def children(self) -> Tuple[Widget]:
        '''The children of this widget.'''
        return tuple(self._children)

    @property
    def hover(self) -> bool:
        '''Whether the cursor is inside the border of this widget.'''
        return self._hover

    @property
    def active(self) -> bool:
        '''Whether the mouse is pressed on this widget.'''
        return self._active

    @property
    def select(self) -> bool:
        '''Whether this widget is selected.'''
        return self._select

    @property
    def focus(self) -> bool:
        '''Whether this widget is focused.'''
        return self._focus

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
        if self._style.display is Display.NONE:
            return False

        for child in reversed(self._children):
            if child.handle(state):
                return True

        if state.is_move:
            hover = self._layout.under_mouse(state)

            if not is_abstract(self.on_mouse_move):
                self.on_mouse_move(state)

            if not self._hover and hover:
                self._hover = hover

                if not is_abstract(self.on_mouse_enter):
                    self.on_mouse_enter(state)

            elif self._hover and not hover:
                self._hover = hover

                if not is_abstract(self.on_mouse_leave):
                    self.on_mouse_leave(state)

        elif state.is_mouse:
            if state.event.value == 'PRESS':
                if self._hover:
                    self._pressed.add(state.event.type)
                    self._active = bool(self._pressed)

                    if not is_abstract(self.on_mouse_press):
                        self.on_mouse_press(state)
                        return True

            elif state.event.value == 'RELEASE':
                if state.event.type in self._pressed:
                    self._pressed.remove(state.event.type)
                    self._active = bool(self._pressed)

                    if self._hover:
                        if not is_abstract(self.on_mouse_release):
                            self.on_mouse_release(state)
                            return True

        elif state.is_scroll:
            if not is_abstract(self.on_mouse_scroll):
                if self._hover:
                    self.on_mouse_scroll(state)
                    return True

        elif state.is_keyboard:
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
            if not is_abstract(self.on_misc_event):
                self.on_misc_event(state)
                return True

        return False

    @abstract
    def on_mouse_move(self, state: ModalState):
        '''Called on mouse move events.'''
        ...

    @abstract
    def on_mouse_enter(self, state: ModalState):
        '''Called when the cursor enters this widget's border.'''
        ...

    @abstract
    def on_mouse_leave(self, state: ModalState):
        '''Called when the cursor leaves this widget's border.'''
        ...

    @abstract
    def on_mouse_scroll(self, state: ModalState):
        '''Called on mouse scroll events inside this widget.'''
        ...

    @abstract
    def on_mouse_press(self, state: ModalState):
        '''Called on mouse press events inside this widget.'''
        ...

    @abstract
    def on_mouse_release(self, state: ModalState):
        '''Called on mouse release events inside this widget, if the button was pressed inside this widget.'''
        ...

    @abstract
    def on_key_press(self, state: ModalState):
        '''Called on key press events, if this widget is focused.'''
        ...

    @abstract
    def on_key_release(self, state: ModalState):
        '''Called on key release events, if this widget is focused.'''
        ...

    @abstract
    def on_misc_event(self, state: ModalState):
        '''Called on miscellaneous events.'''
        ...