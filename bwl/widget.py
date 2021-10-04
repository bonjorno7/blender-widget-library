from __future__ import annotations

from typing import Callable, Dict, List, Tuple, Union

from bpy.types import Context

from .content import Image, Text
from .input import ModalEvent, ModalState
from .layout import Layout, compute_layout
from .render import render_widget
from .style import Display, Style


class Widget:
    '''Widget which can render and handle events.'''

    def __init__(self, parent: Union[Widget, None] = None):
        self._parent: Union[Widget, None] = parent
        self._children: List[Widget] = []

        if self._parent is not None:
            self._parent._children.append(self)

        self._events: Dict[ModalEvent, Callable] = {}

        self.layout = Layout()
        self.style = Style()

        self.image: Union[Image, None] = None
        self.text: Union[Text, None] = None

    @property
    def parent(self) -> Union[Widget, None]:
        '''Widget that owns this widget.'''
        return self._parent

    @property
    def children(self) -> Tuple[Widget]:
        '''Widgets owned by this widget.'''
        return tuple(self._children)

    def subscribe(self, event: ModalEvent, function: Callable):
        '''Add an event to this widget.'''
        self._events[event] = function

    def unsubscribe(self, event: ModalEvent):
        '''Remove an event from this widget.'''
        if event in self._events:
            self._events.pop(event)

    def handle_event(self, state: ModalState, event: ModalEvent) -> bool:
        '''Handle event for this widget and its children, return whether it was handled.'''
        if any(child.handle(state, event) for child in self.children if child.style.display != Display.NONE):
            return True

        function = self._events.get(event)
        return function(state) if function else False

    def compute_layout(self):
        '''Compute layout of this widget and its children.'''
        compute_layout(self)

    def render(self, context: Context):
        '''Render this widget and its children.'''
        if self.style.display != Display.NONE:
            if self.style.display != Display.HIDDEN:
                render_widget(context, self)

            for child in self.children:
                child.render(context)
