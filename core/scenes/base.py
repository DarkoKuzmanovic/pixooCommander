"""Scene abstractions and serialization helpers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Type


class SceneType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    SYSINFO = "sysinfo"


@dataclass
class BaseScene:
    type: SceneType = field(init=False)
    name: str
    duration_s: int = 8
    config: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Rendering hooks (to be implemented by concrete scenes)
    def render(self, device) -> None:  # device: core.device.Device
        raise NotImplementedError

    def preview(self, width: int, height: int):  # returns QImage or None
        return None

    def validate(self) -> None:
        if self.duration_s <= 0:
            raise ValueError("duration_s must be > 0")

    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "duration_s": self.duration_s,
            "config": self.config,
        }


def scene_from_dict(data: Dict[str, Any]) -> BaseScene:
    stype = SceneType(data["type"])  # may raise KeyError/ValueError intentionally
    from .image import ImageScene
    from .text import TextScene
    from .sysinfo import SysInfoScene

    cls_map: Dict[SceneType, Type[BaseScene]] = {
        SceneType.TEXT: TextScene,
        SceneType.IMAGE: ImageScene,
        SceneType.SYSINFO: SysInfoScene,
    }
    cls = cls_map[stype]
    return cls(
        name=data.get("name", stype.value.title()),
        duration_s=int(data.get("duration_s", 8)),
        config=data.get("config", {}),
        id=data.get("id") or str(uuid.uuid4()),
    )
