from __future__ import annotations

from pathlib import Path

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

    def gl_load(self) -> int:
        return self.data.gl_load()

    def gl_free(self):
        self.data.gl_free()

    @property
    def bindcode(self) -> int:
        return self.data.bindcode
