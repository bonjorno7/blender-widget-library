from __future__ import annotations

from typing import List, Set, Tuple, Union

from bpy.types import Context, Event

from .content import Texture
from .event import is_keyboard, is_mouse, is_move, is_scroll
from .layout import Layout, compute_layout
from .render import compile_shaders, render_widget
from .style import DEFAULT_STYLE, Display, Style, compute_style
from .utility import abstract, is_abstract


class Widget:
    '''Widget which can render and handle events.'''

    def __init__(self, parent: Union[Widget, None] = None):
        if parent is not None:
            parent._children.append(self)

        self._parent: Union[Widget, None] = parent
        self._children: List[Widget] = []

        self._style: Style = DEFAULT_STYLE
        self._layout: Layout = Layout()

        self._hover: bool = False
        self._buttons: Set[str] = set()
        self._keys: Set[str] = set()

        self.styles: List[Style] = []
        self.texture: Union[Texture, None] = None
        self.text: Union[str, None] = None

    @property
    def parent(self) -> Union[Widget, None]:
        '''The parent of this widget.'''
        return self._parent

    @property
    def siblings(self) -> Tuple[Widget, ...]:
        '''This widget and its siblings.'''
        return self.parent.children if (self.parent is not None) else (self,)

    @property
    def children(self) -> Tuple[Widget, ...]:
        '''The children of this widget.'''
        return tuple(self._children)

    @property
    def hover(self) -> bool:
        '''Whether the cursor is inside the border of this widget.'''
        return self._hover

    @property
    def buttons(self) -> Set[str]:
        '''The mouse buttons that are pressed on this widget.'''
        return self._buttons.copy()

    @property
    def keys(self) -> Set[str]:
        '''The keyboard keys that are pressed on this widget.'''
        return self._keys.copy()

    def compute(self, context: Context):
        '''Compute style and layout of this widget and its children.'''
        compute_style(self, context)
        compute_layout(self, context)

    def render(self, context: Context):
        '''Render this widget and its children.'''
        compile_shaders(recompile=False)
        render_widget(self, context)

    def handle(self, context: Context, event: Event) -> bool:
        '''Handle event for this widget and its children, return whether it was handled.'''
        if self._style.display is Display.NONE:
            return False

        for child in reversed(self._children):
            if child.handle(context, event):
                return True

        if is_move(event):
            self._hover = self._layout.under_mouse(context, event)

            if not is_abstract(self.on_mouse_move):
                self.on_mouse_move(context, event)

        elif is_mouse(event):
            if event.value == 'PRESS':
                if self._hover:
                    self._buttons.add(event.type)

                    if not is_abstract(self.on_mouse_press):
                        self.on_mouse_press(context, event)
                        return True

            elif event.value == 'RELEASE':
                if event.type in self._buttons:
                    self._buttons.remove(event.type)

                    if self._hover:
                        if not is_abstract(self.on_mouse_release):
                            self.on_mouse_release(context, event)
                            return True

        elif is_scroll(event):
            if not is_abstract(self.on_mouse_scroll):
                if self._hover:
                    self.on_mouse_scroll(context, event)
                    return True

        elif is_keyboard(event):
            if event.value == 'PRESS':
                if self._hover:
                    self._keys.add(event.type)

                    if not is_abstract(self.on_key_press):
                        self.on_key_press(context, event)
                        return True

            elif event.value == 'RELEASE':
                if event.type in self._keys:
                    self._keys.remove(event.type)

                    if self._hover:
                        if not is_abstract(self.on_key_release):
                            self.on_key_release(context, event)
                            return True

        return False

    @abstract
    def on_mouse_move(self, context: Context, event: Event):
        '''Called on mouse move events.'''
        ...

    @abstract
    def on_mouse_press(self, context: Context, event: Event):
        '''Called on mouse press events inside this widget.'''
        ...

    @abstract
    def on_mouse_release(self, context: Context, event: Event):
        '''Called on mouse release events inside this widget, if the button was pressed inside this widget.'''
        ...

    @abstract
    def on_mouse_scroll(self, context: Context, event: Event):
        '''Called on mouse scroll events inside this widget.'''
        ...

    @abstract
    def on_key_press(self, context: Context, event: Event):
        '''Called on key press events inside this widget.'''
        ...

    @abstract
    def on_key_release(self, context: Context, event: Event):
        '''Called on key release events inside this widget, if the key was pressed inside this widget.'''
        ...
