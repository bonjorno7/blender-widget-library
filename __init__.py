bl_info = {
    'name': 'BWL Example',
    'author': 'bonjorno7, Almaas',
    'description': 'Example addon for the Blender Widget Library',
    'blender': (2, 80, 0),
    'version': (1, 0, 1),
    'category': '3D View',
    'location': 'View3D',
}

from pathlib import Path

from bpy.types import Context, Event, Operator, SpaceView3D, WindowManager
from bpy.utils import register_class, unregister_class

from .bwl.content import Font, Texture
from .bwl.input import ModalState
from .bwl.style import Align, Color, Corners, Criteria, Direction, Display, Sides, Size, Style, Visibility
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
            res_texture_blender = Texture.from_file(resources_path.joinpath('blender.png'))
            res_texture_cross = Texture.from_file(resources_path.joinpath('cross.png'))
            res_font_roboto = Font(resources_path.joinpath('roboto.ttf'))

            self.resources = (
                res_texture_blender,
                res_texture_cross,
                res_font_roboto,
            )

            # Setup root widget.
            class Root(Widget):

                def on_key_press(self, state: ModalState):
                    if (state.event.type == 'ESC') and (state.event.value == 'PRESS'):
                        operator: ExampleOperator = state.operator
                        operator.should_close = True

            self.root = Root()
            self.root.styles = [
                Style(
                    visibility=Visibility.HIDDEN,
                    width=Size.relative(),
                    height=Size.relative(),
                    align_x=Align.CENTER,
                    align_y=Align.CENTER,
                ),
            ]

            # Setup window. Windows 11 themed.
            class Window(Widget):

                def handle(self, state: ModalState) -> bool:
                    handled = super().handle(state)

                    # Consume all events when the cursor is inside the window.
                    return handled or self._hover

            window = Window(parent=self.root)
            window.styles = [
                Style(
                    direction=Direction.VERTICAL,
                    width=Size.absolute(800),
                    height=Size.absolute(600),
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
                    width=Size.relative(),
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
            spacer.styles = [Style(visibility=Visibility.HIDDEN, width=Size.relative())]

            # Setup exit button.
            class Button(Widget):

                def on_mouse_release(self, state: ModalState):
                    if state.event.type == 'LEFTMOUSE':
                        operator: ExampleOperator = state.operator
                        operator.should_close = True

            exit_button = Button(parent=header)
            exit_button.styles = [
                Style(
                    background_color=Color(0, 0),
                    width=Size.absolute(45),
                    height=Size.relative(),
                    border_radius=Corners(0, 0, 9, 0),
                    align_x=Align.CENTER,
                    align_y=Align.CENTER,
                ),
                Style(
                    criteria=Criteria(hover=True),
                    background_color=Color(0.769, 0.169, 0.110),
                ),
                Style(
                    criteria=Criteria(active=True),
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
                    width=Size.relative(),
                    height=Size.relative(),
                    background_color=Color(0.25),
                    padding=Sides(5),
                    border_radius=Corners(0, 9),
                ),
            ]

            # Create scroll box widget type.
            class ScrollBox(Widget):

                def on_mouse_scroll(self, state: ModalState):
                    if state.event.type == 'WHEELUPMOUSE':
                        self.styles[0].scroll = max(0, self.styles[0].scroll - 10)
                    else:
                        if self.styles[0].direction is Direction.HORIZONTAL:
                            limit = self._layout.content.width - self._layout.inside.width
                        elif self.styles[0].direction is Direction.VERTICAL:
                            limit = self._layout.content.height - self._layout.inside.height
                        self.styles[0].scroll = min(limit, self.styles[0].scroll + 10)

            class ScrollBoxItem(Widget):

                def on_mouse_release(self, state: ModalState):
                    if self._hover:
                        if state.event.type == 'LEFTMOUSE':
                            if state.event.ctrl:
                                self._select = not self._select
                            else:
                                for sibling in self._parent._children:
                                    sibling._select = False
                                self._select = True

            # Setup scroll boxes.
            for direction in Direction:
                scroll_box = ScrollBox(parent=frame)
                scroll_box.styles = [
                    Style(
                        display=Display.SCROLL,
                        scroll=0,
                        direction=direction,
                        width=Size.relative() if direction is Direction.HORIZONTAL else Size.children(),
                        height=Size.relative() if direction is Direction.VERTICAL else Size.children(),
                        margin=Sides(20, 20, 5 if direction is Direction.HORIZONTAL else 20),
                        padding=Sides(4),
                        background_color=Color(0.35),
                        border_color=Color(0.15),
                        border_radius=Corners(5),
                        border_thickness=1,
                    ),
                    Style(
                        criteria=Criteria(hover=True),
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
                            criteria=Criteria(hover=True),
                            foreground_color=Color(1.0),
                            background_color=Color(0.4),
                        ),
                        Style(
                            criteria=Criteria(select=True),
                            background_color=Color(0.25, 0.45, 0.65),
                        ),
                        Style(
                            criteria=Criteria(select=True, hover=True),
                            background_color=Color(0.35, 0.55, 0.75),
                        ),
                    ]
                    element.text = f'Item number {number}'

            # Finally compute layout and styles.
            self.root.compute(self.state)

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
        hide_hud(context, sidebar=True, redo=True, overlays=True)

        self.draw_handler = SpaceView3D.draw_handler_add(self.draw_callback, (), 'WINDOW', 'POST_PIXEL')
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
