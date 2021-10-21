from __future__ import annotations

from pathlib import Path

import blf
import bpy


class Image:

    def __init__(self, data: bpy.types.Image):
        self.data = data

    @classmethod
    def from_file(cls, path: Path) -> Image:
        data = bpy.data.images.load(str(path), check_existing=True)
        data.colorspace_settings.name = 'Raw'
        return cls(data)

    @classmethod
    def from_buffer(cls, name: str, buffer: bytes, width: int, height: int) -> Image:
        data = bpy.data.images.new(name, width, height, is_data=True)
        data.pack(buffer, len(buffer))
        return cls(data)

    def remove(self):
        bpy.data.images.remove(self.data)

    def gl_load(self) -> int:
        return self.data.gl_load()

    def gl_free(self):
        self.data.gl_free()

    @property
    def width(self) -> int:
        return self.data.size[0]

    @property
    def height(self) -> int:
        return self.data.size[1]

    @property
    def bindcode(self) -> int:
        return self.data.bindcode


class Font:

    def __init__(self, path: Path = None):
        self.path = path
        self.id = blf.load(str(path)) if (self.path is not None) else 0

    def remove(self):
        if self.id > 0:
            blf.unload(str(self.path))
            self.id = 0
