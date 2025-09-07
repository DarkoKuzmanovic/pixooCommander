"""Project model: a collection of scenes and device settings with JSON I/O."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from .device import DeviceConfig
from .scenes.base import BaseScene, SceneType, scene_from_dict


PROJECT_VERSION = 1


@dataclass
class Project:
    device: DeviceConfig = field(default_factory=lambda: DeviceConfig(ip="0.0.0.0", screen_size=64))
    scenes: List[BaseScene] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: int = PROJECT_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "id": self.id,
            "device": asdict(self.device),
            "scenes": [s.to_dict() for s in self.scenes],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        version = int(data.get("version", 1))
        if version != PROJECT_VERSION:
            # For now, accept but do not migrate; future: implement migrations
            pass
        device = DeviceConfig(**data.get("device", {}))
        scenes = [scene_from_dict(sd) for sd in data.get("scenes", [])]
        return cls(device=device, scenes=scenes, id=data.get("id", str(uuid.uuid4())), version=version)

    def save(self, path: Path) -> None:
        # Relativize asset paths (e.g., image scene paths) relative to project file location
        base = path.parent
        data = self.to_dict()
        for sd in data.get("scenes", []):
            if sd.get("type") == SceneType.IMAGE.value:
                cfg = sd.get("config", {})
                p = cfg.get("path")
                if p:
                    try:
                        rel = str(Path(p).resolve().relative_to(base.resolve()))
                        cfg["path"] = rel
                    except Exception:
                        # If not relative to base, keep as-is
                        pass
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "Project":
        data = json.loads(path.read_text())
        proj = cls.from_dict(data)
        base = path.parent
        # Absolutize image scene paths relative to project file location when needed
        for s in proj.scenes:
            try:
                if s.type == SceneType.IMAGE:
                    p = s.config.get("path")
                    if p and not Path(p).is_absolute():
                        abs_path = (base / p).resolve()
                        s.config["path"] = str(abs_path)
            except Exception:
                continue
        return proj
