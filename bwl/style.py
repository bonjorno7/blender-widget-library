from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, Iterator, overload

from bpy.types import Context

from .content import Font

if TYPE_CHECKING:
    from .widget import Widget


class Criteria:
    '''When to use the style.'''

    def __init__(
        self,
        hover: bool = False,
        active: bool = False,
        select: bool = False,
        focus: bool = False,
        custom: Callable[[Widget, Context], bool] = None,
    ):
        self.hover = hover
        self.active = active
        self.select = select
        self.focus = focus
        self.custom = custom


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


class Size:
    '''The size along an axis.'''

    class Type(Enum):
        '''How to calculate the size.'''
        ABSOLUTE = auto()
        RELATIVE = auto()
        FLEXIBLE = auto()
        CHILDREN = auto()
        TEXTURE = auto()

    def __init__(self, type: Type, value: float = None):
        self.type = type
        self.value = value

    @classmethod
    def absolute(cls, pixels: float):
        return cls(cls.Type.ABSOLUTE, pixels)

    @classmethod
    def relative(cls, factor: float):
        return cls(cls.Type.RELATIVE, factor)

    @classmethod
    def flexible(cls, weight: float = 1):
        return cls(cls.Type.FLEXIBLE, weight)

    @classmethod
    def children(cls):
        return cls(cls.Type.CHILDREN)

    @classmethod
    def texture(cls):
        return cls(cls.Type.TEXTURE)


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

    def copy(self) -> Sides:
        return Sides(self.top, self.right, self.bottom, self.left)


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

    def copy(self) -> Corners:
        return Corners(self.top_left, self.bottom_left, self.top_right, self.bottom_right)


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

    def copy(self) -> Color:
        return Color(self.red, self.green, self.blue, self.alpha)


class Style:
    '''Visual properties of a widget.'''

    def __init__(
        self,
        criteria: Criteria = None,
        display: Display = None,
        visibility: Visibility = None,
        direction: Direction = None,
        scroll: float = None,
        align_x: Align = None,
        align_y: Align = None,
        offset_x: float = None,
        offset_y: float = None,
        width: Size = None,
        height: Size = None,
        margin: Sides = None,
        padding: Sides = None,
        foreground_color: Color = None,
        background_color: Color = None,
        border_color: Color = None,
        border_radius: Corners = None,
        border_thickness: float = None,
        font: Font = None,
        font_size: int = None,
    ):
        self.criteria = criteria

        self.display = display
        self.visibility = visibility

        self.direction = direction
        self.scroll = scroll

        self.align_x = align_x
        self.align_y = align_y

        self.offset_x = offset_x
        self.offset_y = offset_y

        self.width = width
        self.height = height

        self.margin = margin
        self.padding = padding

        self.foreground_color = foreground_color
        self.background_color = background_color
        self.border_color = border_color

        self.border_radius = border_radius
        self.border_thickness = border_thickness

        self.font = font
        self.font_size = font_size

    def __add__(self, other: Style) -> Style:
        return Style(
            criteria=other.criteria if (other.criteria is not None) else self.criteria,
            display=other.display if (other.display is not None) else self.display,
            visibility=other.visibility if (other.visibility is not None) else self.visibility,
            direction=other.direction if (other.direction is not None) else self.direction,
            scroll=other.scroll if (other.scroll is not None) else self.scroll,
            align_x=other.align_x if (other.align_x is not None) else self.align_x,
            align_y=other.align_y if (other.align_y is not None) else self.align_y,
            offset_x=other.offset_x if (other.offset_x is not None) else self.offset_x,
            offset_y=other.offset_y if (other.offset_y is not None) else self.offset_y,
            width=other.width if (other.width is not None) else self.width,
            height=other.height if (other.height is not None) else self.height,
            margin=other.margin if (other.margin is not None) else self.margin,
            padding=other.padding if (other.padding is not None) else self.padding,
            foreground_color=other.foreground_color if (other.foreground_color is not None) else self.foreground_color,
            background_color=other.background_color if (other.background_color is not None) else self.background_color,
            border_color=other.border_color if (other.border_color is not None) else self.border_color,
            border_radius=other.border_radius if (other.border_radius is not None) else self.border_radius,
            border_thickness=other.border_thickness if (other.border_thickness is not None) else self.border_thickness,
            font=other.font if (other.font is not None) else self.font,
            font_size=other.font_size if (other.font_size is not None) else self.font_size,
        )

    def copy(self) -> Style:
        return Style(
            criteria=self.criteria,
            display=self.display,
            visibility=self.visibility,
            direction=self.direction,
            scroll=self.scroll,
            align_x=self.align_x,
            align_y=self.align_y,
            offset_x=self.offset_x,
            offset_y=self.offset_y,
            width=self.width,
            height=self.height,
            margin=self.margin,
            padding=self.padding,
            foreground_color=self.foreground_color,
            background_color=self.background_color,
            border_color=self.border_color,
            border_radius=self.border_radius,
            border_thickness=self.border_thickness,
            font=self.font,
            font_size=self.font_size,
        )


DEFAULT_STYLE = Style(
    criteria=Criteria(),
    display=Display.STANDARD,
    visibility=Visibility.VISIBLE,
    direction=Direction.VERTICAL,
    scroll=0,
    align_x=Align.START,
    align_y=Align.START,
    offset_x=0,
    offset_y=0,
    width=Size.children(),
    height=Size.children(),
    margin=Sides(0),
    padding=Sides(0),
    foreground_color=Color(1),
    background_color=Color(1),
    border_color=Color(0),
    border_radius=Corners(0),
    border_thickness=0,
    font=Font(None),
    font_size=14,
)


def compute_style(widget: Widget, context: Context):
    '''Compute style for the given widget and its children.'''
    widget._style = DEFAULT_STYLE

    for style in widget.styles:
        if style.criteria is not None:
            if style.criteria.hover and not widget._hover:
                continue
            if style.criteria.active and not widget._active:
                continue
            if style.criteria.select and not widget._select:
                continue
            if style.criteria.focus and not widget._focus:
                continue
            if callable(style.criteria.custom) and not style.criteria.custom(widget, context):
                continue

        widget._style += style

    for child in widget._children:
        compute_style(child, context)
