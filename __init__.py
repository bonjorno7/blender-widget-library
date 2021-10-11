bl_info = {
    'name': 'BWL Example',
    'author': 'bonjorno7, Almaas',
    'description': 'Example addon for the Blender Widget Library',
    'blender': (2, 80, 0),
    'version': (0, 1, 0),
    'category': '3D View',
    'location': 'View3D',
}

from pathlib import Path
from typing import Callable

from bpy.types import Context, Event, Operator, SpaceView3D, WindowManager
from bpy.utils import register_class, unregister_class

from .bwl.content import Font, Image, Text
from .bwl.input import ModalEvent, ModalState, Subscription
from .bwl.render import compile_shaders
from .bwl.style import Align, Color, Corners, Direction, Display, Sides, Size, Visibility
from .bwl.utils import hide_hud, show_hud
from .bwl.widgets import Widget


class ExampleOperator(Operator):
    bl_idname = 'bwl.example'
    bl_label = 'BWL Example'
    bl_description = 'Test the Blender Widget Library'
    bl_options = {'REGISTER'}

    def invoke(self, context: Context, event: Event) -> set:
        try:
            self.state = ModalState(context, event)
            self.should_close = False

            # Load resources.
            resources_path = Path(__file__).parent.joinpath('resources')
            res_image_blender = Image(resources_path.joinpath('blender.png'))
            res_image_cross = Image(resources_path.joinpath('cross.png'))
            res_font_roboto = Font(resources_path.joinpath('roboto.ttf'))

            self.resources = (
                res_image_blender,
                res_image_cross,
                res_font_roboto,
            )

            # Setup root widget.
            self.root = Widget()
            self.root.style.visibility = Visibility.HIDDEN
            self.root.style.width = Size.FLEX
            self.root.style.height = Size.FLEX
            self.root.style.align_x = Align.CENTER
            self.root.style.align_y = Align.CENTER

            def escape_callback(state: ModalState) -> bool:
                self.should_close = True
                return True

            self.root.subscribe(
                ModalEvent(type='ESC', value='PRESS'),
                Subscription(escape_callback, reverse=True),
            )

            # Setup window A. Windows 11 themed.
            window = Widget(parent=self.root)
            window.style.direction = Direction.VERTICAL
            window.style.width = 800
            window.style.height = 600
            window.style.color = Color(0.15)
            window.style.border_color = window.style.color
            window.style.border_radius = Corners(10)
            window.style.border_thickness = 1

            # Consume all events where the cursor is on the window.
            window.subscribe(ModalEvent(), Subscription(lambda state: True, area=True))

            # Setup title bar.
            header = Widget(parent=window)
            header.style.direction = Direction.HORIZONTAL
            header.style.width = Size.FLEX
            header.style.height = 32
            header.style.align_x = Align.CENTER
            header.style.align_y = Align.CENTER
            header.style.color = Color(0.2)
            header.style.border_radius = Corners(9, 0)
            header.text = Text('Blender Widget Library')
            header.text.style.color = Color(0.8)

            # Setup window icon.
            image_blender = Widget(parent=header)
            image_blender.style.width = Size.IMAGE
            image_blender.style.height = Size.IMAGE
            image_blender.style.margin = Sides(8)
            image_blender.image = res_image_blender

            # Title bar spacer.
            spacer = Widget(parent=header)
            spacer.style.visibility = Visibility.HIDDEN
            spacer.style.width = Size.FLEX

            # Setup exit button.
            class Button(Widget):

                def __init__(self, parent: Widget, callback: Callable):
                    super().__init__(parent)
                    self.callback = callback

                    self.subscribe(
                        ModalEvent(type='LEFTMOUSE', value='PRESS'),
                        Subscription(self.on_press, area=True),
                    )
                    self.subscribe(
                        ModalEvent(type='LEFTMOUSE', value='RELEASE'),
                        Subscription(self.on_release, area=False),
                    )

                    self.pressed = False

                def on_press(self, state: ModalState) -> bool:
                    self.pressed = True
                    return True

                def on_release(self, state: ModalState) -> bool:
                    if self.pressed:
                        self.pressed = False
                        self.callback(state)

                    return False

            def exit_button_callback(state: ModalState):
                self.should_close = True

            exit_button = Button(header, exit_button_callback)
            exit_button.style.width = 45
            exit_button.style.height = header.style.height
            exit_button.style.color = Color(0.698, 0.165, 0.114)
            exit_button.style.border_radius = Corners(0, 0, 9, 0)
            exit_button.style.align_x = Align.CENTER
            exit_button.style.align_y = Align.CENTER

            # Setup exit button icon.
            cross_icon = Widget(parent=exit_button)
            cross_icon.style.width = Size.IMAGE
            cross_icon.style.height = Size.IMAGE
            cross_icon.image = res_image_cross

            # Setup content frame.
            frame = Widget(parent=window)
            frame.style.direction = Direction.VERTICAL
            frame.style.width = Size.FLEX
            frame.style.height = Size.FLEX
            frame.style.color = Color(0.2)
            frame.style.color = Color(0.25)
            frame.style.padding = Sides(5)
            frame.style.border_radius = Corners(0, 9)

            # Create scroll box widget type.
            class ScrollBox(Widget):

                def on_scroll_up(self, state: ModalState):
                    self.style.scroll = max(0, self.style.scroll - 10)
                    return True

                def on_scroll_dn(self, state: ModalState):
                    if self.style.direction == Direction.HORIZONTAL:
                        limit = self.layout.content.width - self.layout.inside.width
                    elif self.style.direction == Direction.VERTICAL:
                        limit = self.layout.content.height - self.layout.inside.height

                    self.style.scroll = min(limit, self.style.scroll + 10)
                    return True

            # Setup scroll boxes.
            for direction in Direction:
                scroll_box = ScrollBox(parent=frame)
                scroll_box.style.display = Display.SCROLL
                scroll_box.style.direction = direction
                scroll_box.style.width = Size.FLEX if direction == Direction.HORIZONTAL else Size.AUTO
                scroll_box.style.height = Size.FLEX if direction == Direction.VERTICAL else Size.AUTO
                scroll_box.style.margin = Sides(20, 20, 5 if direction == Direction.HORIZONTAL else 20)
                scroll_box.style.padding = Sides(4)
                scroll_box.style.color = Color(0.35)
                scroll_box.style.border_color = Color(0.15)
                scroll_box.style.border_radius = Corners(5)
                scroll_box.style.border_thickness = 1

                scroll_box.subscribe(
                    ModalEvent(type='WHEELUPMOUSE', value='PRESS'),
                    Subscription(scroll_box.on_scroll_up),
                )
                scroll_box.subscribe(
                    ModalEvent(type='WHEELDOWNMOUSE', value='PRESS'),
                    Subscription(scroll_box.on_scroll_dn),
                )

                # Setup scroll box items.
                for _ in range(10):
                    element = Widget(parent=scroll_box)
                    element.style.align_x = Align.CENTER
                    element.style.align_y = Align.CENTER
                    element.style.width = 200
                    element.style.height = 70
                    element.style.margin = Sides(2)
                    element.style.color = Color(0.3)
                    element.style.border_color = Color(0.15)
                    element.style.border_thickness = 1
                    element.text = Text('I am inside a scroll box')

            # Finally compute the layout.
            self.root.compute_layout(self.state)
            compile_shaders()

            self.setup(context)
            return {'RUNNING_MODAL'}

        except:
            self.cleanup(context)
            raise

    def modal(self, context: Context, event: Event) -> set:
        try:
            self.state = ModalState(context, event)
            handled = self.root.handle_event(self.state)

            if self.should_close:
                self.cleanup(context)
                return {'FINISHED'}

            self.root.compute_layout(self.state)
            context.area.tag_redraw()

            return {'RUNNING_MODAL'} if handled else {'PASS_THROUGH'}

        except:
            self.cleanup(context)
            raise

    def draw_callback(self):
        self.root.render(self.state)

    def setup(self, context: Context) -> bool:
        hide_hud(context)

        self.draw_handler = SpaceView3D.draw_handler_add(self.draw_callback, (), 'WINDOW', 'POST_PIXEL')
        context.area.tag_redraw()

        if not WindowManager.modal_handler_add(self):
            raise Exception('Failed to add modal handler')

    def cleanup(self, context: Context):
        # Every step is in a try block because this function can not fail.
        try:
            show_hud(context)
        except:
            pass

        try:
            SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
        except:
            pass

        try:
            context.area.tag_redraw()
        except:
            pass

        for resource in self.resources:
            try:
                resource.remove()
            except:
                pass


classes = (ExampleOperator,)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
