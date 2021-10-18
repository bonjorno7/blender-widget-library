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

from .bwl.content import Font, Image
from .bwl.input import ModalState
from .bwl.render import compile_shaders
from .bwl.style import Align, Color, Corners, Direction, Display, Sides, Size, Style, Visibility
from .bwl.utils import hide_hud, show_hud
from .bwl.widgets import Widget


class ExampleOperator(Operator):
    bl_idname = 'bwl.example'
    bl_label = 'BWL Example'
    bl_description = 'Test the Blender Widget Library'
    bl_options = {'REGISTER'}

    def invoke(self, context: Context, event: Event) -> set:
        try:
            self.state = ModalState(self, context, event)
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
            class Root(Widget):

                def on_key_press(self, state: ModalState):
                    if (state.event.type == 'ESC') and (state.event.value == 'PRESS'):
                        operator: ExampleOperator = state.operator
                        operator.should_close = True

            self.root = Root()
            self.root.style = Style(
                visibility=Visibility.HIDDEN,
                width=Size.FLEX,
                height=Size.FLEX,
                align_x=Align.CENTER,
                align_y=Align.CENTER,
            )

            # Setup window. Windows 11 themed.
            class Window(Widget):

                def on_event(self, state: ModalState) -> bool:
                    # Consume all events when the cursor is inside the window.
                    return self.under_mouse(state)

            window = Window(parent=self.root)
            window.style = Style(
                direction=Direction.VERTICAL,
                width=800,
                height=600,
                background_color=Color(0.15),
                border_color=Color(0.15),
                border_radius=Corners(10),
                border_thickness=1,
            )

            # Setup title bar.
            header = Widget(parent=window)
            header.style = Style(
                direction=Direction.HORIZONTAL,
                width=Size.FLEX,
                height=32,
                align_x=Align.CENTER,
                align_y=Align.CENTER,
                foreground_color=Color(0.75),
                background_color=Color(0.2),
                border_radius=Corners(9, 0),
            )
            header.text = 'Blender Widget Library'

            # Setup window icon.
            image_blender = Widget(parent=header)
            image_blender.style = Style(width=Size.IMAGE, height=Size.IMAGE, margin=Sides(8))
            image_blender.image = res_image_blender

            # Title bar spacer.
            spacer = Widget(parent=header)
            spacer.style = Style(visibility=Visibility.HIDDEN, width=Size.FLEX)

            # Setup exit button.
            class Button(Widget):

                # def mouse_enter_event(self, state: ModalState):
                #     if 'LEFTMOUSE' in self._pressed:
                #         self.style_current = self.style_press
                #     else:
                #         self.style_current = self.style_hover

                # def mouse_leave_event(self, state: ModalState):
                #     if 'LEFTMOUSE' in self._pressed:
                #         self.style_current = self.style_press
                #     else:
                #         self.style_current = self.style

                # def mouse_press_event(self, state: ModalState):
                #     if state.event.type == 'LEFTMOUSE':
                #         self.style_current = self.style_press

                def on_mouse_release(self, state: ModalState):
                    if state.event.type == 'LEFTMOUSE':
                        # if self._hovered:
                        #     self.style_current = self.style_hover
                        # else:
                        #     self.style_current = self.style

                        if self._hovered:
                            self.execute(state)

                def execute(self, state: ModalState):
                    operator: ExampleOperator = state.operator
                    operator.should_close = True

            exit_button = Button(parent=header)
            exit_button.style = Style(
                background_color=Color(0, 0),
                width=45,
                height=header.style.height,
                border_radius=Corners(0, 0, 9, 0),
                align_x=Align.CENTER,
                align_y=Align.CENTER,
            )
            exit_button.style_hover = Style(background_color=Color(0.769, 0.169, 0.110))
            exit_button.style_press = Style(background_color=Color(0.698, 0.165, 0.114))

            # Setup exit button icon.
            cross_icon = Widget(parent=exit_button)
            cross_icon.style = Style(width=Size.IMAGE, height=Size.IMAGE)
            cross_icon.image = res_image_cross

            # Setup content frame.
            frame = Widget(parent=window)
            frame.style = Style(
                direction=Direction.VERTICAL,
                width=Size.FLEX,
                height=Size.FLEX,
                background_color=Color(0.25),
                padding=Sides(5),
                border_radius=Corners(0, 9),
            )

            # Create scroll box widget type.
            class ScrollBox(Widget):

                def on_mouse_scroll(self, state: ModalState):
                    if state.event.type == 'WHEELUPMOUSE':
                        self.style.scroll = max(0, self.style.scroll - 10)
                    else:
                        if self.style.direction == Direction.HORIZONTAL:
                            limit = self._layout.content.width - self._layout.inside.width
                        elif self.style.direction == Direction.VERTICAL:
                            limit = self._layout.content.height - self._layout.inside.height
                        self.style.scroll = min(limit, self.style.scroll + 10)

            # Setup scroll boxes.
            for direction in Direction:
                scroll_box = ScrollBox(parent=frame)
                scroll_box.style = Style(
                    display=Display.SCROLL,
                    scroll=0,
                    direction=direction,
                    width=Size.FLEX if direction == Direction.HORIZONTAL else Size.AUTO,
                    height=Size.FLEX if direction == Direction.VERTICAL else Size.AUTO,
                    margin=Sides(20, 20, 5 if direction == Direction.HORIZONTAL else 20),
                    padding=Sides(4),
                    background_color=Color(0.35),
                    border_color=Color(0.15),
                    border_radius=Corners(5),
                    border_thickness=1,
                )
                scroll_box.style_hover = Style(
                    padding=Sides(3),
                    border_thickness=2,
                )

                # Setup scroll box items.
                for _ in range(10):
                    element = Widget(parent=scroll_box)
                    element.style = Style(
                        align_x=Align.CENTER,
                        align_y=Align.CENTER,
                        width=200,
                        height=70,
                        margin=Sides(2),
                        foreground_color=Color(0.85),
                        background_color=Color(0.3),
                        border_color=Color(0.15),
                        border_thickness=1,
                    )
                    element.style_hover = Style(foreground_color=Color(1.0))
                    element.text = 'I am inside a scroll box'

            # Finally compute the layout.
            self.root.compute(self.state)
            compile_shaders()

            self.setup(context)
            return {'RUNNING_MODAL'}

        except:
            self.cleanup(context)
            raise

    def modal(self, context: Context, event: Event) -> set:
        try:
            # This happens on workspace switch. Can't restore HUD unfortunately.
            if context.area is None:
                self.cleanup(context)
                return {'FINISHED'}

            self.state = ModalState(self, context, event)
            handled = self.root.handle(self.state)

            if self.should_close:
                self.cleanup(context)
                return {'FINISHED'}

            self.root.compute(self.state)
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
