from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, List, Union

from .base import BaseScene, SceneType


@dataclass
class TextScene(BaseScene):
    type: SceneType = field(default=SceneType.TEXT, init=False)

    def render(self, device) -> None:
        self.validate()
        device.clear()

        # Check if we're using the new multi-line format
        if "lines" in self.config:
            self._render_multiline(device)
        else:
            # Legacy single-line format
            self._render_single_line(device)

        device.push()

    def _render_multiline(self, device) -> None:
        """Render multi-line text format."""
        text_options = self.config.get("text_options", {})
        lines = self.config.get("lines", [])
        align = text_options.get("align", "left")
        global_color = tuple(text_options.get("color", (255, 255, 255)))

        # Render each line
        for i, line_config in enumerate(lines):
            text = line_config.get("text", "")
            if not text:
                continue

            # Calculate Y position
            y = int(line_config.get("y", i * 12))  # Default line height of 12 pixels
            line_color = tuple(line_config.get("color", global_color))
            r, g, b = [int(c) for c in line_color]

            # Calculate X position based on alignment or use specific x value if provided
            if "x" in line_config:
                x = int(line_config["x"])
            else:
                x = self._calculate_x_position(device, text, align)

            device.draw_text_rgb(text, x, y, r, g, b)

    def _render_single_line(self, device) -> None:
        """Render legacy single-line format."""
        text: str = self.config.get("text", "")
        x: int = int(self.config.get("x", 0))
        y: int = int(self.config.get("y", 0))
        color: Tuple[int, int, int] = tuple(self.config.get("color", (255, 255, 255)))  # type: ignore
        r, g, b = [int(c) for c in color]

        if text:
            device.draw_text_rgb(text, x, y, r, g, b)

    def _calculate_x_position(self, device, text: str, align: str) -> int:
        """
        Calculate X position based on text alignment.
        Uses a simple character width estimation since we can't get actual text dimensions from Pixoo.
        """
        # Estimate text width (assuming ~6 pixels per character)
        # This is a rough estimation that works reasonably well for most ASCII characters
        estimated_width = len(text) * 6

        if align == "center":
            return max(0, (device.config.screen_size - estimated_width) // 2)
        elif align == "right":
            return max(0, device.config.screen_size - estimated_width)
        else:  # left align
            return 0

    def validate(self) -> None:
        super().validate()

        # Migrate old format to new format if needed
        if "text" in self.config and "lines" not in self.config:
            self._migrate_legacy_format()

        # Validate new format if present
        if "lines" in self.config:
            text_options = self.config.get("text_options", {})
            if not isinstance(text_options, dict):
                raise ValueError("text_options must be a dictionary")

            lines = self.config.get("lines", [])
            if not isinstance(lines, list):
                raise ValueError("lines must be a list")

            align = text_options.get("align", "left")
            if align not in ["left", "center", "right"]:
                raise ValueError("align must be 'left', 'center', or 'right'")

            for i, line in enumerate(lines):
                if not isinstance(line, dict):
                    raise ValueError(f"line {i} must be a dictionary")
                if "text" not in line:
                    raise ValueError(f"line {i} must contain 'text' field")
        elif "text" not in self.config:
            # Allow empty text but keep key present for clarity
            self.config.setdefault("text", "")

    def _migrate_legacy_format(self) -> None:
        """Migrate legacy single-line format to new multi-line format."""
        # Extract values from legacy format
        text = self.config.get("text", "")
        x = self.config.get("x", 0)
        y = self.config.get("y", 0)
        color = self.config.get("color", (255, 255, 255))

        # Determine alignment based on x value
        align = "left"
        has_explicit_x = False

        # Check if x is a string representing alignment
        if isinstance(x, str):
            if x == "center":
                align = "center"
            elif x == "right":
                align = "right"
        # Check if x is an integer representing explicit position
        elif isinstance(x, int):
            has_explicit_x = True

        # Create new format
        new_config: Dict[str, Any] = {
            "text_options": {
                "align": align,
                "line_spacing": 2,
                "color": list(color) if isinstance(color, tuple) else color
            },
            "lines": [
                {
                    "text": text,
                    "y": y
                }
            ]
        }

        # If x was a specific integer position, we'll use that for the line
        if has_explicit_x and isinstance(x, int) and x > 0:
            # For explicit x position, we override the calculated position
            # by adding it to the line config
            new_config["lines"][0]["x"] = x

        # Update config - remove old keys and add new structure
        keys_to_remove = ["text", "x", "y", "color"]
        for key in keys_to_remove:
            self.config.pop(key, None)

        self.config.update(new_config)
