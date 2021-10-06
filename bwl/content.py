from __future__ import annotations

from pathlib import Path

import bpy

from .style import TextStyle


class Image:

    def __init__(self, path: Path):
        self.data = bpy.data.images.load(str(path), check_existing=True)
        self.data.colorspace_settings.name = 'Raw'

    @property
    def width(self) -> int:
        return self.data.size[0]

    @property
    def height(self) -> int:
        return self.data.size[1]

    @property
    def bindcode(self) -> int:
        return self.data.bindcode

    def gl_load(self) -> int:
        return self.data.gl_load()

    def gl_free(self):
        self.data.gl_free()

    def remove(self):
        bpy.data.images.remove(self.data)


class Text:

    def __init__(self, data: str, style: TextStyle = None):
        self.data = data
        self.style: TextStyle = style if (style is not None) else TextStyle()
