"""Playback engine stub for sequencing scenes.

Later: move to QThread and signals; for now, provide a simple iterator API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from .device import Device
from .scenes.base import BaseScene


@dataclass
class Player:
    device: Device
    scenes: List[BaseScene] = field(default_factory=list)
    index: int = 0

    def set_scenes(self, scenes: Iterable[BaseScene]) -> None:
        self.scenes = list(scenes)
        self.index = 0

    def current(self) -> Optional[BaseScene]:
        if not self.scenes:
            return None
        return self.scenes[self.index]

    def next(self) -> Optional[BaseScene]:
        if not self.scenes:
            return None
        self.index = (self.index + 1) % len(self.scenes)
        return self.current()

    def previous(self) -> Optional[BaseScene]:
        if not self.scenes:
            return None
        self.index = (self.index - 1) % len(self.scenes)
        return self.current()

    def render_current(self) -> None:
        scene = self.current()
        if scene is None:
            return
        scene.render(self.device)

