from __future__ import annotations

from typing import Dict, List, Union

from bpy.types import Context

from ..content import Image, Text
from ..input import ModalEvent, ModalState, Subscription
from ..layout import Layout, compute_layout
from ..render import render_widget
from ..style import Display, Style, Visibility


class Widget:
    '''Widget which can render and handle events.'''

    def __init__(self, parent: Union[Widget, None] = None):
        if parent is not None:
            parent.children.append(self)

        self.children: List[Widget] = []
        self.subscriptions: Dict[ModalEvent, Subscription] = {}

        self.layout = Layout()
        self.style = Style()

        self.image: Union[Image, None] = None
        self.text: Union[Text, None] = None

    def subscribe(self, event: ModalEvent, subscription: Subscription):
        '''Add an event to this widget.'''
        self.subscriptions[event] = subscription

    def unsubscribe(self, event: ModalEvent):
        '''Remove an event from this widget.'''
        if event in self.subscriptions:
            self.subscriptions.pop(event)

    def is_mouse_inside(self, state: ModalState) -> bool:
        '''Check whether the cursor is inside the border of this widget.'''
        return self.layout.border.contains(state.mouse_x, state.mouse_y)

    def handle_event(self, state: ModalState) -> bool:
        '''Handle event for this widget and its children, return whether it was handled.'''
        if self.style.display == Display.NONE:
            return False

        subscriptions_reverse: List[Subscription] = []
        subscriptions: List[Subscription] = []

        for event, subscription in self.subscriptions.items():
            if event.compare(state.event):
                if subscription.reverse:
                    subscriptions_reverse.append(subscription)
                else:
                    subscriptions.append(subscription)

        for subscription in subscriptions_reverse:
            if not subscription.area or self.is_mouse_inside(state):
                if subscription.callback(state):
                    return True

        for child in reversed(self.children):
            if child.handle_event(state):
                return True

        for subscription in subscriptions:
            if not subscription.area or self.is_mouse_inside(state):
                if subscription.callback(state):
                    return True

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
