from __future__ import annotations

from typing import Dict, List, Union

from ..content import Image, Text
from ..input import ModalEvent, ModalState, Subscription
from ..layout import Layout, compute_layout
from ..render import render_widget
from ..style import Display, Style


class Widget:
    '''Widget which can render and handle events.'''

    def __init__(self, parent: Union[Widget, None] = None):
        if parent is not None:
            parent.children.append(self)

        self.parent = parent
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

        # Get lists of subscriptions to be handled before and after children.
        subscriptions_matched = [s for (e, s) in self.subscriptions.items() if e.compare(state.event)]
        subscriptions_reverse = [s for s in subscriptions_matched if s.reverse]
        subscriptions_regular = [s for s in subscriptions_matched if not s.reverse]

        # Check area if necessary, return if the subscription handled the event.
        def handle_subscription(s: Subscription) -> bool:
            return (not s.area or self.is_mouse_inside(state)) and s.callback(state)

        # Call all reverse subscriptions, return if any of them handled the event.
        if any(list(map(handle_subscription, subscriptions_reverse))):
            return True

        # Send the event to each child, return early if one handled it.
        for child in reversed(self.children):
            if child.handle_event(state):
                return True

        # Call all regular subscriptions, return if any of them handled the event.
        if any(list(map(handle_subscription, subscriptions_regular))):
            return True

        # The event was not handled by this widget or its children.
        return False

    def compute_layout(self, state: ModalState):
        '''Compute layout of this widget and its children.'''
        compute_layout(self, state)

    def render(self, state: ModalState):
        '''Render this widget and its children.'''
        render_widget(self, state)
