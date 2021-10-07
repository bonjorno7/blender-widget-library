from __future__ import annotations

from typing import Callable, Dict, List, Union

from bpy.types import Context

from ..content import Image, Text
from ..input import ModalEvent, ModalState
from ..layout import Layout, compute_layout
from ..render import render_widget
from ..style import Display, Style, Visibility


class Widget:
    '''Widget which can render and handle events.'''

    def __init__(self, parent: Widget = None):
        if parent is not None:
            parent.children.append(self)

        self.children: List[Widget] = []
        self.events: Dict[ModalEvent, Callable] = {}

        self.layout = Layout()
        self.style = Style()

        self.image: Union[Image, None] = None
        self.text: Union[Text, None] = None

    def subscribe(self, event: ModalEvent, function: Callable):
        '''Add an event to this widget.'''
        self.events[event] = function

    def unsubscribe(self, event: ModalEvent):
        '''Remove an event from this widget.'''
        if event in self.events:
            self.events.pop(event)

    def handle_event(self, state: ModalState, event: ModalEvent) -> bool:
        '''Handle event for this widget and its children, return whether it was handled.'''
        if self.style.display == Display.NONE:
            return False

        if event._area:
            if not self.layout.border.contains(state.mouse_x, state.mouse_y):
                return False

        function = self.events.get(event)

        if event._reverse:
            if (function is not None) and function(state):
                return True

        for child in self.children:
            if child.handle_event(state, event):
                return True

        if not event._reverse:
            if (function is not None) and function(state):
                return True

        return False

    def compute_layout(self, context: Context):
        '''Compute layout of this widget and its children.'''
        if self.style.display != Display.NONE:
            compute_layout(self)

    def render(self, context: Context):
        '''Render this widget and its children.'''
        if self.style.display == Display.NONE:
            return

        if self.style.visibility != Visibility.HIDDEN:
            render_widget(self, context)

        if self.style.display == Display.SCROLL:
            for child in self.children:
                if child.layout.scissor.contains(child.layout.border, True):
                    child.render(context)

        else:
            for child in self.children:
                child.render(context)
