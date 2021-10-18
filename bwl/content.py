from __future__ import annotations

from pathlib import Path

import blf
import bpy


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
        if self.data is not None:
            bpy.data.images.remove(self.data)
            self.data = None


class Font:

    def __init__(self, path: Path = None):
        self.path = path
        self.id = blf.load(str(path)) if (self.path is not None) else 0

    def remove(self):
        if self.id > 0:
            blf.unload(str(self.path))
            self.id = 0
