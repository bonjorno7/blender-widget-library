from __future__ import annotations

from typing import Callable, Dict, List, Tuple, Union

from bpy.types import Context

from ..content import Image, Text
from ..input import EventCopy, ModalState
from ..layout import Layout, compute_layout
from ..render import render_widget
from ..style import Display, Style, Visibility


class Widget:
    '''Widget which can render and handle events.'''

    def __init__(self, parent: Widget = None):
        if parent is not None:
            parent.children.append(self)

        self.children: List[Widget] = []
        self.events: Dict[EventCopy, Tuple[Callable, bool, bool]] = {}

        self.layout = Layout()
        self.style = Style()

        self.image: Union[Image, None] = None
        self.text: Union[Text, None] = None

    def subscribe(self, event: EventCopy, function: Callable, area: bool = True, reverse: bool = False):
        '''Add an event to this widget.'''
        self.events[event] = (function, area, reverse)

    def unsubscribe(self, event: EventCopy):
        '''Remove an event from this widget.'''
        if event in self.events:
            self.events.pop(event)

    def is_mouse_inside(self, state: ModalState) -> bool:
        '''Check whether the cursor is inside the border of this widget.'''
        return self.layout.border.contains(state.mouse_x, state.mouse_y)

    def handle_event(self, state: ModalState, event: EventCopy) -> bool:
        '''Handle event for this widget and its children, return whether it was handled.'''
        if self.style.display == Display.NONE:
            return False

        function, area, reverse = self.events.get(event, (None, None, None))

        if not reverse:
            for child in reversed(self.children):
                if child.handle_event(state, event):
                    return True

        if not area or self.is_mouse_inside(state):
            if function and function(state):
                return True

        if reverse:
            for child in self.children:
                if child.handle_event(state, event):
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
