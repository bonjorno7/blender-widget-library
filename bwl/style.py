from __future__ import annotations

from enum import Enum, auto
from typing import Iterator, Union


class Display(Enum):
    '''How to display the widget.'''
    VISIBLE = auto()
    HIDDEN = auto()
    NONE = auto()


class Direction(Enum):
    '''The axis to place content along.'''
    HORIZONTAL = auto()
    VERTICAL = auto()


class Justify(Enum):
    '''How to place items along the main axis.'''
    START = auto()
    CENTER = auto()
    END = auto()
    SPACE = auto()


class Align(Enum):
    '''How to place items along the cross axis.'''
    START = auto()
    CENTER = auto()
    END = auto()


class Size(Enum):
    '''How to calculate the size along an axis.'''
    AUTO = auto()
    FLEX = auto()
    IMAGE = auto()


class Sides:
    '''Values used for margin and padding.'''

    def __init__(self, top: float = None, right: float = None, bottom: float = None, left: float = None):
        '''Supports CSS margin/padding shorthand.'''
        self.top = top if (top is not None) else 0
        self.right = right if (right is not None) else self.top
        self.bottom = bottom if (bottom is not None) else self.top
        self.left = left if (left is not None) else self.right

    @property
    def width(self) -> float:
        '''Sum of the left and right values.'''
        return self.left + self.right

    @property
    def height(self) -> float:
        '''Sum of the top and bottom values.'''
        return self.top + self.bottom


class Color:
    '''Color in float values including alpha.'''

    def __init__(self, red: float, green: float, blue: float, alpha: float = 1):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def __iter__(self) -> Iterator[float]:
        '''Iterate over the color channels.'''
        return iter((self.red, self.green, self.blue, self.alpha))


class Style:
    '''Visual properties of a widget.'''

    def __init__(self):
        '''Styles do not cascade.'''
        self.display: Display = Display.VISIBLE

        self.direction: Direction = Direction.VERTICAL
        self.justify: Justify = Justify.START
        self.align: Align = Align.START

        self.x: float = 0
        self.y: float = 0

        self.width: Union[Size, float] = Size.AUTO
        self.height: Union[Size, float] = Size.AUTO

        self.margin: Sides = Sides()
        self.padding: Sides = Sides()

        self.color: Color = Color(1, 1, 1)
        self.border_color: Color = Color(0, 0, 0)

        self.border_radius: float = 0
        self.border_thickness: float = 0
