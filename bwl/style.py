from __future__ import annotations

from enum import Enum, auto
from typing import Iterator, Union, overload


class Display(Enum):
    '''How to display the widget.'''
    STANDARD = auto()
    SCROLL = auto()
    FLOAT = auto()
    NONE = auto()


class Visibility(Enum):
    '''How a widget should be rendered.'''
    VISIBLE = auto()
    HIDDEN = auto()


class Direction(Enum):
    '''The axis to place content along.'''
    HORIZONTAL = auto()
    VERTICAL = auto()


class Align(Enum):
    '''How to place items along an axis.'''
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

    @overload
    def __init__(self):
        ...

    @overload
    def __init__(self, value: float):
        ...

    @overload
    def __init__(self, vertical: float, horizontal: float):
        ...

    @overload
    def __init__(self, top: float, horizontal: float, bottom: float):
        ...

    @overload
    def __init__(self, top: float, right: float, bottom: float, left: float):
        ...

    def __init__(self, top: float = None, right: float = None, bottom: float = None, left: float = None):
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


class Corners:
    '''Values used for border radius.'''

    @overload
    def __init__(self):
        ...

    @overload
    def __init__(self, value: float):
        ...

    @overload
    def __init__(self, top: float, bottom: float):
        ...

    @overload
    def __init__(self, top_left: float, bottom: float, top_right: float):
        ...

    @overload
    def __init__(self, top_left: float, bottom_left: float, top_right: float, bottom_right: float):
        ...

    def __init__(
        self,
        top_left: float = None,
        bottom_left: float = None,
        top_right: float = None,
        bottom_right: float = None,
    ):
        self.top_left = top_left if (top_left is not None) else 0
        self.bottom_left = bottom_left if (bottom_left is not None) else self.top_left
        self.top_right = top_right if (top_right is not None) else self.top_left
        self.bottom_right = bottom_right if (bottom_right is not None) else self.bottom_left

    def __iter__(self) -> Iterator[float]:
        return iter((self.top_left, self.bottom_left, self.top_right, self.bottom_right))

    def clamped(self, size: float) -> Corners:
        half_size = size / 2
        return Corners(
            min(half_size, self.top_left),
            min(half_size, self.bottom_left),
            min(half_size, self.top_right),
            min(half_size, self.bottom_right),
        )


class Color:
    '''Color in float values including alpha.'''

    @overload
    def __init__(self):
        ...

    @overload
    def __init__(self, gray: float):
        ...

    @overload
    def __init__(self, gray: float, alpha: float):
        ...

    @overload
    def __init__(self, red: float, green: float, blue: float):
        ...

    @overload
    def __init__(self, red: float, green: float, blue: float, alpha: float):
        ...

    def __init__(self, *args: float):
        if len(args) == 0:
            self.red, self.green, self.blue, self.alpha = (0, 0, 0, 1)
        elif len(args) == 1:
            self.red, self.green, self.blue, self.alpha = (args[0], args[0], args[0], 1)
        elif len(args) == 2:
            self.red, self.green, self.blue, self.alpha = (args[0], args[0], args[0], args[1])
        elif len(args) == 3:
            self.red, self.green, self.blue, self.alpha = (args[0], args[1], args[2], 1)
        elif len(args) == 4:
            self.red, self.green, self.blue, self.alpha = (args[0], args[1], args[2], args[3])

    def __iter__(self) -> Iterator[float]:
        return iter((self.red, self.green, self.blue, self.alpha))


class Style:
    '''Visual properties of a widget.'''

    def __init__(self):
        self.display: Display = Display.STANDARD
        self.visibility: Visibility = Visibility.VISIBLE

        self.direction: Direction = Direction.VERTICAL
        self.scroll: float = 0

        self.align_x: Align = Align.START
        self.align_y: Align = Align.START

        self.x: float = 0
        self.y: float = 0

        self.width: Union[Size, float] = Size.AUTO
        self.height: Union[Size, float] = Size.AUTO

        self.margin: Sides = Sides()
        self.padding: Sides = Sides()

        self.color: Color = Color(1)
        self.border_color: Color = Color(0)

        self.border_radius: Corners = Corners()
        self.border_thickness: float = 0


class TextStyle:
    '''Visual properties of text.'''

    def __init__(self):
        self.color: Color = Color(1)
        self.font_id = 0
        self.font_size: int = 14
