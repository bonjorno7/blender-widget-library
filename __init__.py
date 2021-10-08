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

from bpy.types import Context, Event, Operator, SpaceView3D, WindowManager
from bpy.utils import register_class, unregister_class

from .bwl.content import Font, Image, Text
from .bwl.input import EventCopy, ModalState
from .bwl.render import compile_shaders
from .bwl.style import Align, Color, Corners, Direction, Display, Sides, Size, Visibility
from .bwl.utils import hide_hud, show_hud
from .bwl.widgets import Screen, Widget, Window


class ExampleOperator(Operator):
    bl_idname = 'bwl.example'
    bl_label = 'BWL Example'
    bl_description = 'Test the Blender Widget Library'
    bl_options = {'REGISTER'}

    def invoke(self, context: Context, event: Event) -> set:
        try:
            # TODO: Move to button class.
            self.exit_pressed = False
            self.exit_released = False

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

            # Setup events.
            self.state = ModalState(context, event)
            self.event_esc = EventCopy(type='ESC', press=True)

            # Setup screen.
            self.screen = Screen()
            self.screen.style.visibility = Visibility.VISIBLE
            self.screen.style.color = Color(0, 0.8)

            # Setup window A.
            window_a = Window(parent=self.screen)
            window_a.style.direction = Direction.VERTICAL
            window_a.style.x = 150
            window_a.style.y = 150
            window_a.style.width = 800
            window_a.style.height = 600
            window_a.style.margin = Sides(10)
            window_a.style.color = Color(0.15)
            window_a.style.border_color = window_a.style.color
            window_a.style.border_radius = Corners(10)
            window_a.style.border_thickness = 1

            # Setup title bar.
            window_a.header.style.direction = Direction.HORIZONTAL
            window_a.header.style.align_x = Align.CENTER
            window_a.header.style.align_y = Align.CENTER
            window_a.header.style.color = Color(0.2)
            window_a.header.style.border_radius = Corners(9, 0)
            window_a.header.text = Text('Blender Widget Library')
            window_a.header.text.style.font = res_font_roboto
            window_a.header.text.style.color = Color(0.8)

            # Setup window icon.
            image_blender = Widget(parent=window_a.header)
            image_blender.style.width = Size.IMAGE
            image_blender.style.height = Size.IMAGE
            image_blender.style.margin = Sides(8)
            image_blender.image = res_image_blender

            # Title bar spacer.
            spacer = Widget(parent=window_a.header)
            spacer.style.visibility = Visibility.HIDDEN
            spacer.style.width = Size.FLEX

            # Setup exit button.
            exit_button = Widget(parent=window_a.header)
            exit_button.style.width = 45
            exit_button.style.height = window_a.header.style.height
            exit_button.style.color = Color(0.769, 0.169, 0.110, 0.5)
            exit_button.style.border_radius = Corners(0, 0, 9, 0)
            exit_button.style.align_x = Align.CENTER
            exit_button.style.align_y = Align.CENTER

            def on_lmb_press_exit_button(state: ModalState):
                self.exit_pressed = True
                return True

            def on_lmb_release_exit_button(state: ModalState):
                if self.exit_pressed:
                    self.exit_pressed = False
                    self.exit_released = exit_button.is_mouse_inside(state)
                return False

            exit_button.subscribe(EventCopy(type='LEFTMOUSE', press=True), on_lmb_press_exit_button, area=True)
            exit_button.subscribe(EventCopy(type='LEFTMOUSE', press=False), on_lmb_release_exit_button, area=False)

            # Setup exit button icon.
            cross_icon = Widget(parent=exit_button)
            cross_icon.style.width = Size.IMAGE
            cross_icon.style.height = Size.IMAGE
            cross_icon.image = res_image_cross

            window_a.frame.style.color = Color(0.25)
            window_a.frame.style.padding = Sides(5)
            window_a.frame.style.border_radius = Corners(0, 9)

            # Setup window B.
            window_b = Window(parent=self.screen)
            window_b.style.x = 500
            window_b.style.y = 500
            window_b.style.width = 400
            window_b.style.height = 600
            window_b.style.color = Color(0.157, 0.173, 0.204)
            window_b.style.margin = Sides(10)

            # Setup title bar.
            window_b.header.style.align_x = Align.CENTER
            window_b.header.style.align_y = Align.CENTER
            window_b.header.style.color.alpha = 0
            window_b.header.text = Text('One Dark Pro')
            window_b.header.text.style.color = Color(0.61)

            # Setup frame.
            window_b.frame.style.color = Color(0.129, 0.145, 0.169)

            # Create scroll box widget type.
            class ScrollBox(Widget):

                def event_scroll_up(self, state: ModalState):
                    self.style.scroll = max(0, self.style.scroll - 10)
                    return True

                def event_scroll_dn(self, state: ModalState):
                    if self.style.direction == Direction.HORIZONTAL:
                        limit = self.layout.content.width - self.layout.inside.width
                    elif self.style.direction == Direction.VERTICAL:
                        limit = self.layout.content.height - self.layout.inside.height

                    self.style.scroll = min(limit, self.style.scroll + 10)
                    return True

            # Setup scroll boxes.
            for direction in Direction:
                scroll_box = ScrollBox(parent=window_a.frame)
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

                scroll_box.subscribe(EventCopy(type='WHEELUPMOUSE', press=True), scroll_box.event_scroll_up)
                scroll_box.subscribe(EventCopy(type='WHEELDOWNMOUSE', press=True), scroll_box.event_scroll_dn)

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
            self.screen.compute_layout(context)
            compile_shaders()

            self.setup(context)
            return {'RUNNING_MODAL'}

        except:
            self.cleanup(context)
            raise

    def modal(self, context: Context, event: Event) -> set:
        try:
            self.state.update(context, event)

            event_copy = EventCopy.from_event(event)

            if event_copy == self.event_esc:
                self.cleanup(context)
                return {'FINISHED'}

            handled = self.screen.handle_event(self.state, event_copy)

            if self.exit_released:
                self.cleanup(context)
                return {'FINISHED'}

            if handled:
                self.screen.compute_layout(context)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}

            return {'PASS_THROUGH'}

        except:
            self.cleanup(context)
            raise

    def draw_callback(self, context: Context):
        self.screen.render(context)

    def setup(self, context: Context) -> bool:
        hide_hud(context)

        self.draw_handler = SpaceView3D.draw_handler_add(self.draw_callback, (context,), 'WINDOW', 'POST_PIXEL')
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
