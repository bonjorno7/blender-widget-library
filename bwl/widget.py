from __future__ import annotations

from typing import List, Set, Tuple, Union

from bpy.types import Context, Event

from .content import Texture
from .event import CustomEvent, is_custom, is_keyboard, is_mouse, is_move, is_scroll
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
    def siblings(self) -> Tuple[Widget]:
        '''This widget and its siblings.'''
        return self.parent.children if (self.parent is not None) else tuple()

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

    def compute(self, context: Context):
        '''Compute style and layout of this widget and its children.'''
        compute_style(self, context)
        compute_layout(self, context)

    def render(self, context: Context):
        '''Render this widget and its children.'''
        compile_shaders(recompile=False)
        render_widget(self, context)

    def handle(self, context: Context, event: Union[Event, CustomEvent]) -> bool:
        '''Handle event for this widget and its children, return whether it was handled.'''
        if self._style.display is Display.NONE:
            return False

        for child in reversed(self._children):
            if child.handle(context, event):
                return True

        if is_custom(event):
            if not is_abstract(self.on_custom_event):
                return self.on_custom_event(context, event)

        elif is_move(event):
            hover = self._layout.under_mouse(context, event)

            if not is_abstract(self.on_mouse_move):
                self.on_mouse_move(context, event)

            if not self._hover and hover:
                self._hover = hover

                if not is_abstract(self.on_mouse_enter):
                    self.on_mouse_enter(context, event)

            elif self._hover and not hover:
                self._hover = hover

                if not is_abstract(self.on_mouse_leave):
                    self.on_mouse_leave(context, event)

        elif is_mouse(event):
            if event.value == 'PRESS':
                if self._hover:
                    self._pressed.add(event.type)
                    self._active = bool(self._pressed)

                    if not is_abstract(self.on_mouse_press):
                        self.on_mouse_press(context, event)
                        return True

            elif event.value == 'RELEASE':
                if event.type in self._pressed:
                    self._pressed.remove(event.type)
                    self._active = bool(self._pressed)

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
            if self._focus:
                if event.value == 'PRESS':
                    if not is_abstract(self.on_key_press):
                        self.on_key_press(context, event)
                        return True

                elif event.value == 'RELEASE':
                    if not is_abstract(self.on_key_release):
                        self.on_key_release(context, event)
                        return True

        else:
            if not is_abstract(self.on_misc_event):
                return self.on_misc_event(context, event)

        return False

    @abstract
    def on_custom_event(self, context: Context, event: CustomEvent) -> bool:
        '''Handle custom event, return whether it was handled.'''
        ...

    @abstract
    def on_mouse_move(self, context: Context, event: Event):
        '''Called on mouse move events.'''
        ...

    @abstract
    def on_mouse_enter(self, context: Context, event: Event):
        '''Called when the cursor enters this widget's border.'''
        ...

    @abstract
    def on_mouse_leave(self, context: Context, event: Event):
        '''Called when the cursor leaves this widget's border.'''
        ...

    @abstract
    def on_mouse_scroll(self, context: Context, event: Event):
        '''Called on mouse scroll events inside this widget.'''
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
    def on_key_press(self, context: Context, event: Event):
        '''Called on key press events, if this widget is focused.'''
        ...

    @abstract
    def on_key_release(self, context: Context, event: Event):
        '''Called on key release events, if this widget is focused.'''
        ...

    @abstract
    def on_misc_event(self, context: Context, event: Event) -> bool:
        '''Handle miscellaneous event, return whether it was handled.'''
        ...
