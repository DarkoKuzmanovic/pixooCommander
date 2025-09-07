"""Device wrapper around `pixoo.Pixoo` with a simple, mockable API.

Keep all direct Pixoo calls here to ease testing and retries later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:
    from pixoo import Pixoo  # type: ignore
except Exception:  # pragma: no cover - optionally absent in some envs
    Pixoo = None  # type: ignore


@dataclass
class DeviceConfig:
    ip: str
    screen_size: int = 64


class Device:
    """Thin convenience wrapper over the Pixoo client."""

    def __init__(self, config: DeviceConfig):
        self.config = config
        self._client: Optional[Pixoo] = None

    def connect(self) -> None:
        if Pixoo is None:
            raise RuntimeError("pixoo library not available")
        self._client = Pixoo(self.config.ip, self.config.screen_size)
        # Simple probe
        _ = self.get_device_time()

    # Low-level passthroughs (kept small for now)
    def get_device_time(self):
        self._ensure()
        return self._client.get_device_time()

    def clear(self) -> None:
        self._ensure()
        self._client.clear()

    def draw_text_rgb(self, text: str, x: int, y: int, r: int, g: int, b: int) -> None:
        self._ensure()
        self._client.draw_text_at_location_rgb(text, x, y, r, g, b)

    def draw_image_path(self, path: str) -> None:
        self._ensure()
        self._client.draw_image(path)

    def push(self) -> None:
        self._ensure()
        self._client.push()

    # Internal helpers
    def _ensure(self) -> None:
        if self._client is None:
            raise RuntimeError("Device not connected. Call connect() first.")

