# Project Status

Date: 2025-09-06

## Completed

- Core modules: `core/device.py`, `core/project.py` (JSON save/load, relative paths), `core/player.py`, `core/scenes/{base,text,image,sysinfo}.py`.
- Scenes UI: add/delete, inline duration editing, drag-and-drop with handle, Alt+Up/Down reordering.
- Editors:
  - Text: content, x/y, color picker, scroll toggle, speed (px/s), direction (left/right).
  - Image: file path with missing-file highlight, fit (contain/cover/stretch).
  - SysInfo: theme (light/accent/mono).
- Preview: live QImage preview; SysInfo refresh every 1s; scrolling text animation.
- Playback: play/pause/prev/next, per-scene durations, device-side scrolling animation.
- Persistence: New/Open/Save/Save As, recent projects, asset relink, relative image paths on save.
- Menu bar: File actions + Exit; unsaved-changes (dirty) tracking and close prompt.
- DX: pytest harness, one converted test, and CLI demo (`tools/demo_project.py`).
- Stability: fixed recursion in list updates; drag limited to handle; Qt6 deprecation warnings resolved.

## In Progress / Next

- Player options: loop/repeat-one/shuffle + UI indicators.
- Scene-driven preview (move preview logic into scene classes).
- Validation UX: inline messages/toasts for missing assets, invalid inputs.
- Robust device error handling and retry/backoff.
- Expand test coverage (unit + integration with mock device); CI wiring.

## Known Limitations

- Preview font metrics approximate device rendering; long text wrapping is basic.
- No global project settings pane (e.g., default screen size, theme presets).
- No drag handle only drag-start enforcement on touch devices.

## How to Run

- Install: `python -m pip install -r requirements.txt`
- App: `python main.py`
- Tests: `pytest -q` (network: `PIXOO_IP=... pytest -m network -q`)
- CLI demo: `python tools/demo_project.py --ip 192.168.0.103 --image path.png`
