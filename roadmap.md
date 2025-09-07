# Scenes Editor Roadmap

This roadmap turns the current PySide6 app into a user-friendly "Scenes" editor for composing and scheduling displays (system info, images, text, etc.) for Pixoo devices.

## Goals

- Visual scene management (create, edit, reorder, duplicate, delete).
- Scene types: System Info, Image, Text (extendable later: Clock, Gallery, Animation).
- Playlist playback with per-scene duration and seamless rotation.
- Non-blocking device updates and immediate preview.
- Persistent projects (save/load JSON).

## Progress To Date

- Core packages scaffolded (`core/device.py`, `core/project.py`, `core/player.py`, `core/scenes/*`).
- Scenes tab: add/delete, inline duration editing, drag-and-drop with handle, Alt+Up/Down reordering.
- Editors: Text (text, x/y, color, scroll, speed, direction), Image (path, fit contain/cover/stretch), SysInfo (theme).
- Live preview: QImage-based; SysInfo updates 1s; scrolling text animates in preview.
- Playback: per-scene durations, next/prev, play/pause, scrolling text animation to device.
- Persistence: JSON save/load, recent projects, relative image paths, relink missing assets.
- Menu bar: New/Open/Save/Save As/Relink/Exit; unsaved-changes prompting; dirty indicator in title.
- Pytest harness: config + one converted test; CLI demo (`tools/demo_project.py`).

## Architecture Changes

- Core module split:
  - `core/device.py`: Thin wrapper over `Pixoo` with safe calls, timeouts, and a mockable interface.
  - `core/scenes/`: `base.py` (Scene interface) + `text.py`, `image.py`, `sysinfo.py` implementations.
  - `core/player.py`: Scheduler/engine (play, pause, next, previous, loop, random).
  - `core/project.py`: Project model (scenes list, metadata, versioned JSON serialization).
- UI layer:
  - `ui/scenes_tab.py`: Models, views, editors, and preview pane.
  - Use `QAbstractListModel` (or `QStandardItemModel`) for scenes + drag-reorder.

## Data Model

- Scene interface:
  - id: string (uuid), type: enum, name: string, duration_s: int
  - config: dict (type-specific: e.g., Text: {text, color, x, y}; Image: {path, fit_mode}; SysInfo: {metrics, theme})
  - methods: `render(device)`, `preview(qimage)`, `validate()`
- Project JSON (example):

  ```json
  {
    "version": 1,
    "device": { "screen_size": 64 },
    "scenes": [
      {
        "id": "...",
        "type": "text",
        "name": "Title",
        "duration_s": 8,
        "config": { "text": "Hello", "color": "#FFFFFF", "x": 0, "y": 0 }
      },
      {
        "id": "...",
        "type": "image",
        "name": "Logo",
        "duration_s": 10,
        "config": { "path": "assets/logo.png", "fit": "contain" }
      }
    ]
  }
  ```

## UX Plan

- New "Scenes" tab with three panes:
  - Left: Scenes list (name, type, duration) + buttons |Add| |Duplicate| |Delete|; drag to reorder.
  - Center: Scene editor (fields tailored to type; inline validation; file picker for images; color picker for text).
  - Right: Live preview (render to `QImage` via scene `preview()`); Play controls (▶, ⏸, ⏭, ⏮, loop toggle) and interval input.
- Global toolbar: New Project, Open, Save, Save As, Export/Import.
- Status bar: device connection state and last push result.

## Engine & Performance

- Player runs on a `QTimer` with cooperative updates (no blocking calls on UI thread). Use a worker `QThread` for network push.
- Debounced apply: editing a scene updates preview immediately; device push only on Play or explicit "Send to device".
- Error reporting: toast or log panel entry; keep playback running even if one scene fails.

## Persistence & Compatibility

- Save to `projects/*.json`; validate on load with versioned schema; migrate if needed.
- Store image paths as relative to project file when possible; warn on missing files and allow relink.

## Testing Strategy

- Unit: scene `validate()` and `preview()` produce expected pixels (golden images for core cases).
- Device-free integration: mock `device.push()` to capture draw calls; assert sequence per scene.
- Network: `@pytest.mark.network` tests for end-to-end push with `PIXOO_IP`.

## Milestones

1. Core refactor (device wrapper, project model, base Scene). DONE
2. Implement Text/Image/SysInfo scenes with render. DONE (preview lives in UI for now)
3. Scenes tab: list model, editors, preview. DONE (basic; iterate on UX)
4. Player engine + controls. DONE (loop/shuffle pending)
5. Persistence: save/load, recent, relink, relative paths. DONE
6. Polishing: keyboard shortcuts, drag handle, deprecation warnings. DONE (more validation pending)
7. Tests + docs. PARTIAL (pytest harness added; expand coverage)

## Nice-to-Haves (post-MVP)

- Schedules (time-of-day, weekdays), transitions, per-scene animations.
- Asset manager with thumbnails; drag-drop images.
- Template gallery and import/export of individual scenes.
- Plugin system: register new scene types via entry points.

## Next Up

- Loop/repeat/shuffle options in player with indicators.
- Move preview logic into scene classes (`preview(width,height)`).
- Inline validation messages (missing image, out-of-range coords) and toast UX.
- Image relative path management UI (convert to relative, browse from project root).
- Better error boundaries around device pushes; retry/backoff on transient failures.

## Developer Notes

- Keep `Pixoo` calls centralized in `core/device.py` to simplify mocking and retries.
- Maintain a single source of truth for current project in a controller (signals: projectChanged, sceneChanged).
- Prefer small, testable classes; avoid business logic in UI widgets.
