from __future__ import annotations

from dataclasses import dataclass, field

from .base import BaseScene, SceneType

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore


@dataclass
class SysInfoScene(BaseScene):
    type: SceneType = field(default=SceneType.SYSINFO, init=False)

    def render(self, device) -> None:
        self.validate()
        if psutil is None:
            raise RuntimeError("psutil not available")
        cpu_percent = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory().percent
        # Choose colors based on theme
        theme = str(self.config.get("theme", "light"))
        if theme == "accent":
            cpu_color = (255, 255, 0)
            ram_color = (0, 255, 255)
        elif theme == "mono":
            cpu_color = ram_color = (220, 220, 220)
        else:  # light/default
            cpu_color = ram_color = (255, 255, 255)

        device.clear()
        device.draw_text_rgb(f"CPU: {cpu_percent:.1f}%", 0, 0, *cpu_color)
        device.draw_text_rgb(f"RAM: {mem:.1f}%", 0, 10, *ram_color)
        device.push()
