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

from .bwl.content import Image
from .bwl.input import ModalEvent, ModalState
from .bwl.render import compile_shaders
from .bwl.style import Align, Color, Corners, Direction, Sides, Size
from .bwl.utils import hide_hud, show_hud
from .bwl.widget import Widget


class ExampleOperator(Operator):
    bl_idname = 'bwl.example'
    bl_label = 'BWL Example'
    bl_description = 'Test the Blender Widget Library'
    bl_options = {'REGISTER'}

    def invoke(self, context: Context, event: Event) -> set:
        try:
            compile_shaders()
            self.image = Image(Path(__file__).parent.joinpath('resources', 'blender.png'))

            self.state = ModalState(context, event)
            self.event_esc = ModalEvent('ESC')

            self.root = Widget()
            self.root.style.color = Color(0.8, 0.4, 0.2, 0.2)
            self.root.style.padding = Sides(5)
            self.root.style.width = 800
            self.root.style.height = 800
            self.root.style.border_radius = Corners(20)
            self.root.style.border_thickness = 1
            self.root.style.direction = Direction.HORIZONTAL

            container_a = Widget(parent=self.root)
            container_a.style.direction = Direction.VERTICAL
            container_a.style.width = 400
            container_a.style.height = 500
            container_a.style.align_x = Align.CENTER
            container_a.style.align_y = Align.CENTER
            container_a.style.color = Color(0.0, 0.5, 1.0, 0.3)
            container_a.style.margin = Sides(5)
            container_a.style.padding = Sides(5)
            container_a.style.border_radius = Corners(5)

            widget_a = Widget(parent=container_a)
            widget_a.style.margin = Sides(5)
            widget_a.image = self.image
            widget_a.style.width = Size.IMAGE
            widget_a.style.height = Size.IMAGE

            widget_b = Widget(parent=container_a)
            widget_b.style.margin = Sides(5)
            widget_b.style.color = Color(0.2, 0.2, 0.2)
            widget_b.style.width = 200
            widget_b.style.height = 50
            widget_b.style.border_radius = Corners(5)
            widget_b.style.border_thickness = 20

            container_b = Widget(parent=self.root)
            container_b.style.direction = Direction.HORIZONTAL
            container_b.style.width = Size.FLEX
            container_b.style.height = Size.FLEX
            container_b.style.align_x = Align.END
            container_b.style.align_y = Align.END
            container_b.style.color = Color(0.0, 0.5, 1.0, 0.3)
            container_b.style.margin = Sides(5)
            container_b.style.padding = Sides(5)
            container_b.style.border_radius = Corners(5)

            widget_c = Widget(parent=container_b)
            widget_c.style.margin = Sides(5)
            widget_c.style.color = Color(0.6, 0.6, 0.6, 0.6)
            widget_c.style.width = Size.FLEX
            widget_c.style.height = 50
            widget_c.style.border_thickness = 50
            widget_c.style.border_radius = Corners(400, 20, 5, 0)
            widget_c.style.border_color = Color(1.0, 1.0, 1.0, 0.4)

            widget_d = Widget(parent=container_b)
            widget_d.style.margin = Sides(5)
            widget_d.style.color = Color(0.2, 0.2, 0.2)
            widget_d.style.width = 150
            widget_d.style.height = Size.FLEX

            self.root.style.x = self.state.mouse_x
            self.root.style.y = self.state.mouse_y
            self.root.compute_layout()

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

            self.root.style.x = self.state.mouse_x
            self.root.style.y = self.state.mouse_y
            self.root.compute_layout()

            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

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
