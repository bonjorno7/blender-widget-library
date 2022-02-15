bl_info = {
    'name': 'BWL Example',
    'author': 'bonjorno7, Almaas',
    'description': 'Example addon for the Blender Widget Library',
    'blender': (2, 80, 0),
    'version': (1, 0, 5),
    'category': '3D View',
    'location': 'View3D',
}

from pathlib import Path
from typing import Tuple, Union

from bpy.app.timers import register as register_timer
from bpy.types import Context, Event, Operator, SpaceView3D, WindowManager
from bpy.utils import register_class, unregister_class

from .bwl.content import Font, Texture
from .bwl.style import Align, Color, Corners, Direction, Display, Sides, Size, Style, Visibility
from .bwl.utility import hide_hud, show_hud
from .bwl.widget import Widget


class ExampleOperator(Operator):
    bl_idname = 'bwl.example'
    bl_label = 'BWL Example'
    bl_description = 'Test the Blender Widget Library'
    bl_options = {'REGISTER'}

    # Store global variables on the class.
    should_close = False

    def invoke(self, context: Context, event: Event) -> set:
        try:
            ExampleOperator.should_close = False

            # Load resources.
            resources_path = Path(__file__).parent.joinpath('resources')
            res_texture_blender = Texture.from_file(resources_path.joinpath('blender.png'))
            res_texture_cross = Texture.from_file(resources_path.joinpath('cross.png'))
            res_font_roboto = Font(resources_path.joinpath('roboto.ttf'))

            self.resources = (
                res_texture_blender,
                res_texture_cross,
                res_font_roboto,
            )

            # Setup root widget.
            self.root = Widget()
            self.root.styles = [
                Style(
                    visibility=Visibility.HIDDEN,
                    width=Size.flexible(),
                    height=Size.flexible(),
                    align_x=Align.CENTER,
                    align_y=Align.CENTER,
                ),
            ]

            # Setup window. Windows 11 themed.
            class Window(Widget):

                def handle(self, context: Context, event: Event) -> bool:
                    handled = super().handle(context, event)

                    # Consume all events when the cursor is inside the window.
                    return handled or self._hover

                def on_key_press(self, context: Context, event: Event):
                    if event.type == 'ESC':
                        ExampleOperator.should_close = True

            window = Window(parent=self.root)
            window.styles = [
                Style(
                    direction=Direction.VERTICAL,
                    width=Size.relative(0.5),
                    height=Size.relative(0.5),
                    background_color=Color(0.15),
                    border_color=Color(0.15),
                    border_radius=Corners(10),
                    border_thickness=1,
                ),
            ]

            # Setup title bar.
            header = Widget(parent=window)
            header.styles = [
                Style(
                    direction=Direction.HORIZONTAL,
                    width=Size.flexible(),
                    height=Size.absolute(32),
                    align_x=Align.CENTER,
                    align_y=Align.CENTER,
                    foreground_color=Color(0.75),
                    background_color=Color(0.2),
                    border_radius=Corners(9, 0),
                    font=res_font_roboto,
                ),
            ]
            header.text = 'Blender Widget Library'

            # Setup window icon.
            icon_blender = Widget(parent=header)
            icon_blender.styles = [Style(width=Size.texture(), height=Size.texture(), margin=Sides(8))]
            icon_blender.texture = res_texture_blender

            # Title bar spacer.
            spacer = Widget(parent=header)
            spacer.styles = [Style(visibility=Visibility.HIDDEN, width=Size.flexible())]

            # Setup exit button.
            class Button(Widget):

                def on_mouse_release(self, context: Context, event: Event):
                    if event.type == 'LEFTMOUSE':
                        ExampleOperator.should_close = True

            exit_button = Button(parent=header)
            exit_button.styles = [
                Style(
                    background_color=Color(0, 0),
                    width=Size.absolute(45),
                    height=Size.flexible(),
                    border_radius=Corners(0, 0, 9, 0),
                    align_x=Align.CENTER,
                    align_y=Align.CENTER,
                ),
                Style(
                    criteria=lambda widget, context: widget.hover,
                    background_color=Color(0.769, 0.169, 0.110),
                ),
                Style(
                    criteria=lambda widget, context: widget.buttons,
                    background_color=Color(0.698, 0.165, 0.114),
                ),
            ]

            # Setup exit button icon.
            icon_cross = Widget(parent=exit_button)
            icon_cross.styles = [Style(width=Size.texture(), height=Size.texture())]
            icon_cross.texture = res_texture_cross

            # Setup content frame.
            frame = Widget(parent=window)
            frame.styles = [
                Style(
                    direction=Direction.VERTICAL,
                    width=Size.flexible(),
                    height=Size.flexible(),
                    background_color=Color(0.25),
                    padding=Sides(5),
                    border_radius=Corners(0, 9),
                ),
            ]

            # Create scroll box widget type.
            class ScrollBox(Widget):
                moving: bool = False

                def get_limit(self) -> int:
                    if self._style.direction is Direction.HORIZONTAL:
                        return self._layout.content.width - self._layout.inside.width
                    elif self._style.direction is Direction.VERTICAL:
                        return self._layout.content.height - self._layout.inside.height

                def get_mouse_pos(self, context: Context, event: Event) -> int:
                    if self._style.direction is Direction.HORIZONTAL:
                        return event.mouse_region_x
                    elif self._style.direction is Direction.VERTICAL:
                        return context.area.height - event.mouse_region_y

                def on_mouse_press(self, context: Context, event: Event):
                    if event.type == 'LEFTMOUSE':
                        self.mouse_prev = self.get_mouse_pos(context, event)

                def on_mouse_release(self, context: Context, event: Event):
                    if event.type == 'LEFTMOUSE':
                        self.moving = False

                def on_mouse_move(self, context: Context, event: Event):
                    if 'LEFTMOUSE' in self.buttons:
                        mouse = self.get_mouse_pos(context, event)
                        delta = mouse - self.mouse_prev

                        if self.moving:
                            self.styles[0].scroll = max(0, min(self.get_limit(), self.styles[0].scroll - delta))
                            self.mouse_prev = mouse

                        elif abs(delta) > 10:
                            self.moving = True
                            self.mouse_prev = mouse

                def on_mouse_scroll(self, context: Context, event: Event):
                    wheel = 10 if event.type == 'WHEELUPMOUSE' else -10
                    self.styles[0].scroll = max(0, min(self.get_limit(), self.styles[0].scroll - wheel))

            # Create scroll box item widget type.
            class ScrollBoxItem(Widget):
                select: bool = False

                def on_mouse_release(self, context: Context, event: Event):
                    if not self.parent.moving:
                        if event.type == 'LEFTMOUSE':
                            if event.ctrl:
                                self.select = not self.select
                            else:
                                for sibling in self.siblings:
                                    sibling.select = False
                                self.select = True

            # Setup scroll boxes.
            for direction in Direction:
                scroll_box = ScrollBox(parent=frame)
                scroll_box.styles = [
                    Style(
                        display=Display.SCROLL,
                        scroll=0,
                        direction=direction,
                        width=Size.flexible() if direction is Direction.HORIZONTAL else Size.children(),
                        height=Size.flexible() if direction is Direction.VERTICAL else Size.children(),
                        margin=Sides(20, 20, 5 if direction is Direction.HORIZONTAL else 20),
                        padding=Sides(4),
                        background_color=Color(0.35),
                        border_color=Color(0.15),
                        border_radius=Corners(5),
                        border_thickness=1,
                    ),
                    Style(
                        criteria=lambda widget, context: widget.hover,
                        padding=Sides(3),
                        border_thickness=2,
                    ),
                ]

                # Setup scroll box items.
                for number in range(1, 11):
                    element = ScrollBoxItem(parent=scroll_box)
                    element.styles = [
                        Style(
                            align_x=Align.CENTER,
                            align_y=Align.CENTER,
                            width=Size.absolute(200),
                            height=Size.absolute(70),
                            margin=Sides(2),
                            foreground_color=Color(0.85),
                            background_color=Color(0.3),
                            border_color=Color(0.15),
                            border_thickness=1,
                            font=res_font_roboto,
                        ),
                        Style(
                            criteria=lambda widget, context: widget.hover,
                            foreground_color=Color(1.0),
                            background_color=Color(0.4),
                        ),
                        Style(
                            criteria=lambda widget, context: widget.select,
                            background_color=Color(0.25, 0.45, 0.65),
                        ),
                        Style(
                            criteria=lambda widget, context: widget.hover and widget.select,
                            background_color=Color(0.35, 0.55, 0.75),
                        ),
                    ]
                    element.text = f'Item number {number}'

            # Finally compute layout and styles.
            self.root.compute(context)

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

            handled = self.root.handle(context, event)

            if ExampleOperator.should_close:
                self.cleanup(context)
                return {'FINISHED'}

            self.root.compute(context)
            context.area.tag_redraw()

            return {'RUNNING_MODAL'} if handled else {'PASS_THROUGH'}

        except:
            self.cleanup(context)
            raise

    def draw_callback(self, context: Context):
        self.root.render(context)

    def setup(self, context: Context) -> bool:
        hide_hud(context, sidebar=True, redo=True)

        self.draw_handler = SpaceView3D.draw_handler_add(self.draw_callback, (context,), 'WINDOW', 'POST_PIXEL')
        context.area.tag_redraw()

        if not WindowManager.modal_handler_add(self):
            raise Exception('Failed to add modal handler')

    def cleanup(self, context: Context):
        # Every step is in a try block because this function can not fail.
        for step in (
            lambda: show_hud(context),
            lambda: SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW'),
            lambda: context.area.tag_redraw(),
        ):
            try:
                step()
            except:
                pass

        # Clean up textures and fonts.
        def cleanup_resources(resources: Tuple[Union[Texture, Font], ...]):
            for resource in resources:
                try:
                    resource.remove()
                except:
                    pass

        # Delay resource cleanup until operator is likely finished.
        register_timer(lambda: cleanup_resources(self.resources), first_interval=5)


classes = (ExampleOperator,)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
