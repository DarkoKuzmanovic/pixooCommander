from __future__ import annotations

from dataclasses import dataclass, field

from .base import BaseScene, SceneType


@dataclass
class ImageScene(BaseScene):
    type: SceneType = field(default=SceneType.IMAGE, init=False)

    def render(self, device) -> None:
        self.validate()
        path = self.config.get("path")
        if not path:
            raise ValueError("ImageScene requires config['path']")
        device.clear()
        device.draw_image_path(path)
        device.push()
