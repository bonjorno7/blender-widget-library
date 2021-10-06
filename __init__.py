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

from .bwl.content import Image, Text
from .bwl.input import ModalEvent, ModalState
from .bwl.render import compile_shaders
from .bwl.style import Align, Color, Corners, Direction, Display, Sides, Size, Visibility
from .bwl.utils import hide_hud, show_hud
from .bwl.widget import Widget


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

            # Load images and fonts.
            resources = Path(__file__).parent.joinpath('resources')
            self.image_blender = Image(resources.joinpath('blender.png'))
            self.image_cross = Image(resources.joinpath('cross.png'))

            # Setup events.
            self.state = ModalState(context, event)
            self.event_esc = ModalEvent('ESC', 'PRESS')
            self.event_lmb_press = ModalEvent('LEFTMOUSE', 'PRESS')
            self.event_lmb_release = ModalEvent('LEFTMOUSE', 'RELEASE', shift=None, ctrl=None, alt=None, area=False)
            self.event_lmb_release_area = ModalEvent('LEFTMOUSE', 'RELEASE', shift=None, ctrl=None, alt=None)
            self.event_mw_up = ModalEvent('WHEELUPMOUSE', 'PRESS')
            self.event_mw_dn = ModalEvent('WHEELDOWNMOUSE', 'PRESS')
            # NEEDS TO BE TESTED, MIGHT NEED MORE NONEING.
            self.event_mouse_move = ModalEvent('MOUSEMOVE', area=False)

            # Setup root widget.
            self.root = Widget()
            self.root.style.direction = Direction.VERTICAL
            self.root.style.x = 150
            self.root.style.y = 150
            self.root.style.width = 800
            self.root.style.height = 600
            self.root.style.color = Color(0.15)
            self.root.style.border_color = self.root.style.color
            self.root.style.border_radius = Corners(10)
            self.root.style.border_thickness = 1

            # TODO: Implement window dragging and resizing.

            # Setup title bar.
            title_bar = Widget(parent=self.root)
            title_bar.style.direction = Direction.HORIZONTAL
            title_bar.style.align_x = Align.CENTER
            title_bar.style.align_y = Align.CENTER
            title_bar.style.width = Size.FLEX
            title_bar.style.height = 30
            title_bar.style.color = Color(0.2)
            title_bar.style.border_radius = Corners(9, 0)
            title_bar.text = Text('Blender Widget Library')

            def event_lmb_press_title_bar(state: ModalState):
                return True

            def event_lmb_release_title_bar(state: ModalState):
                return False

            title_bar.subscribe(self.event_lmb_press, event_lmb_press_title_bar)
            title_bar.subscribe(self.event_lmb_release, event_lmb_release_title_bar)

            # Setup window icon.
            image_blender = Widget(parent=title_bar)
            image_blender.style.width = Size.IMAGE
            image_blender.style.height = Size.IMAGE
            image_blender.style.margin = Sides(8)
            image_blender.image = self.image_blender

            # Title bar spacer.
            spacer = Widget(parent=title_bar)
            spacer.style.visibility = Visibility.HIDDEN
            spacer.style.width = Size.FLEX

            # Setup exit button.
            exit_button = Widget(parent=title_bar)
            exit_button.style.width = 45
            exit_button.style.height = title_bar.style.height
            exit_button.style.color = Color(0.769, 0.169, 0.110, 0.5)
            exit_button.style.border_radius = Corners(0, 0, 9, 0)
            exit_button.style.align_x = Align.CENTER
            exit_button.style.align_y = Align.CENTER

            def event_lmb_press_exit_button(state: ModalState):
                self.exit_pressed = True
                return True

            def event_lmb_release_area_exit_button(state: ModalState):
                if self.exit_pressed:
                    self.exit_released = True
                    return True
                return False

            def event_lmb_release_exit_button(state: ModalState):
                self.exit_pressed = False
                return False

            exit_button.subscribe(self.event_lmb_press, event_lmb_press_exit_button)
            exit_button.subscribe(self.event_lmb_release_area, event_lmb_release_area_exit_button)
            exit_button.subscribe(self.event_lmb_release, event_lmb_release_exit_button)

            # Setup exit button icon.
            cross_icon = Widget(parent=exit_button)
            cross_icon.style.width = Size.IMAGE
            cross_icon.style.height = Size.IMAGE
            cross_icon.image = self.image_cross

            frame = Widget(parent=self.root)
            frame.style.direction = Direction.VERTICAL
            frame.style.color = Color(0.25)
            frame.style.padding = Sides(5)
            frame.style.width = Size.FLEX
            frame.style.height = Size.FLEX
            frame.style.border_radius = Corners(0, 9)

            # Setup scroll boxes.
            for direction in Direction:
                scroll_box = Widget(parent=frame)
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

                # FIXME: Second scroll box eats events from both.

                def event_scroll_up(state: ModalState):
                    scroll_box.style.scroll = max(0, scroll_box.style.scroll - 10)
                    return True

                def event_scroll_dn(state: ModalState):
                    if scroll_box.style.direction == Direction.HORIZONTAL:
                        limit = scroll_box.layout.content.width - scroll_box.layout.inside.width
                    elif scroll_box.style.direction == Direction.VERTICAL:
                        limit = scroll_box.layout.content.height - scroll_box.layout.inside.height

                    scroll_box.style.scroll = min(limit, scroll_box.style.scroll + 10)
                    return True

                scroll_box.subscribe(self.event_mw_up, event_scroll_up)
                scroll_box.subscribe(self.event_mw_dn, event_scroll_dn)

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
            self.root.compute_layout()
            compile_shaders()

            self.setup(context)
            return {'RUNNING_MODAL'}

        except:
            self.cleanup(context)
            raise

    def modal(self, context: Context, event: Event) -> set:
        try:
            self.state.update(context, event)

            if self.event_esc.check(self.state):
                self.cleanup(context)
                return {'FINISHED'}

            checked_events = [
                event for event in (
                    self.event_lmb_press,
                    self.event_lmb_release_area,
                    self.event_lmb_release,
                    self.event_mw_up,
                    self.event_mw_dn,
                    self.event_mouse_move,
                ) if event.check(self.state)
            ]

            for event in checked_events:
                self.root.handle_event(self.state, event)

            if self.exit_released:
                self.cleanup(context)
                return {'FINISHED'}

            if checked_events:
                self.root.compute_layout()
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}

            return {'PASS_THROUGH'}

        except:
            self.cleanup(context)
            raise

    def draw_callback(self, context: Context):
        self.root.render(context)

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

        try:
            self.image.remove()
        except:
            pass


classes = (ExampleOperator,)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
