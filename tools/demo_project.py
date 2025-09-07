#!/usr/bin/env python3
"""
Minimal CLI to render a sample project to a Pixoo device.

Usage:
  python tools/demo_project.py --ip 192.168.0.103 [--image path] [--size 64]

Environment alternative:
  PIXOO_IP=192.168.0.103 python tools/demo_project.py
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from core.device import Device, DeviceConfig
from core.player import Player
from core.project import Project
from core.scenes.image import ImageScene
from core.scenes.sysinfo import SysInfoScene
from core.scenes.text import TextScene


def build_sample_project(image_path: str | None) -> Project:
    p = Project()
    p.scenes.append(TextScene(name="Hello", duration_s=5, config={"text": "Hello Pixoo!", "x": 0, "y": 0, "color": (255, 255, 255)}))
    if image_path:
        p.scenes.append(ImageScene(name="Image", duration_s=6, config={"path": image_path}))
    p.scenes.append(SysInfoScene(name="System", duration_s=5, config={}))
    return p


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a sample project to Pixoo")
    parser.add_argument("--ip", default=os.getenv("PIXOO_IP"), help="Device IP (or set PIXOO_IP)")
    parser.add_argument("--size", type=int, default=64, help="Screen size (default 64)")
    parser.add_argument("--image", type=str, default=None, help="Optional image file to include as a scene")
    args = parser.parse_args()

    if not args.ip:
        parser.error("--ip is required (or set PIXOO_IP)")

    if args.image is not None:
        img = Path(args.image)
        if not img.exists():
            parser.error(f"Image not found: {img}")

    project = build_sample_project(args.image)
    device = Device(DeviceConfig(ip=args.ip, screen_size=args.size))
    device.connect()

    player = Player(device)
    player.set_scenes(project.scenes)

    # Simple linear playback once
    for scene in list(project.scenes):
        print(f"Rendering scene: {scene.name} ({scene.type}) for {scene.duration_s}s")
        player.render_current()
        time.sleep(max(1, int(scene.duration_s)))
        player.next()

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

