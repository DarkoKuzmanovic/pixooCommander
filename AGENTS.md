# Repository Guidelines

This repository hosts a Python application for controlling Pixoo devices with both Qt6 desktop and NiceGUI web interfaces. Use this guide to develop, test, and contribute changes consistently.

## Project Structure & Module Organization

- `main.py`: Qt6 GUI entry point and app logic (preserved for backward compatibility).
- `qt_app.py`: Qt6 desktop application (original implementation).
- `web_app.py`: NiceGUI web application entry point.
- `requirements.txt`: Runtime dependencies.
- `README.md`: User-facing setup and usage.
- `QWEN.md`: Development notes and architecture context.
- `test/`: Utility scripts and ad-hoc tests (e.g., `test_simple.py`, `test_device_endpoints.py`).
- `core/`: Core business logic modules (device communication, scene management, playback).
- `ui/`: NiceGUI web interface components.

## Build, Test, and Development Commands

- Install deps: `python -m pip install -r requirements.txt`
- Run Qt6 app: `python qt_app.py`
- Run NiceGUI app: `python web_app.py`
- Run test scripts: `python test/test_simple.py` (or any `test/*.py`)
- Optional venv (Windows): `py -m venv .venv && .venv\Scripts\activate`

## Coding Style & Naming Conventions

- Indentation: 4 spaces; follow PEP 8.
- Naming: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Qt widgets: prefer clear names (e.g., `connect_button`, `status_label`).
- NiceGUI components: follow NiceGUI naming conventions and patterns.
- Imports: standard lib, third‑party, local — grouped and alphabetized within groups.
- Docstrings: concise triple‑quoted summaries for public functions/classes.

## Web UI Development Guidelines

- **Component Structure**: Organize UI into modular components in the `ui/` directory
- **State Management**: Use class-based components with clear state management
- **Async Operations**: Use async/await for non-blocking operations
- **Error Handling**: Implement comprehensive error handling with user feedback
- **Responsive Design**: Ensure UI works well on different screen sizes
- **Theme Support**: Use CSS variables for consistent theming
- **Performance**: Optimize rendering and avoid blocking the event loop

## Testing Guidelines

- Location: all scripts in `test/` (no pytest harness yet).
- Execution: run directly via `python test/<file>.py`.
- Networking: some tests hit device IPs (`requests`); mock or guard with timeouts when possible.
- Naming: use `test_*.py` and small, focused functions.
- Add reproducible examples (inputs/IP placeholders) and print concise diagnostics.

## Commit & Pull Request Guidelines

- Commits: use Conventional Commits (e.g., `feat: add screen rotation`, `fix: handle connection error`).
- Scope: group related changes; keep commits small and descriptive.
- PRs: include summary, rationale, screenshots/GIFs for UI changes, steps to verify, and any device/IP assumptions.
- Link issues with `Closes #<id>` when applicable. Update `README.md` if commands or usage change.

## Security & Configuration Tips

- Do not commit secrets or real device IPs; use examples like `192.168.0.100`.
- Validate user input (IP/screen size). Handle network timeouts and exceptions.
- Keep dependencies minimal; pin only when required by compatibility.
