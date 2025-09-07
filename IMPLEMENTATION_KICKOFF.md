# Implementation Kickoff: Starting Phase 0 for Design System

This document serves as the quick-start guide to begin Phase 0 (Foundation) of the Pixoo Commander design system implementation, as outlined in [docs/design-system/roadmap.md](docs/design-system/roadmap.md). Phase 0 focuses on setup, planning, and baselining the existing application to prepare for visual uplift. Although core scaffolding is already in place, this guide ensures a clean start for refinements, doc reviews, and initial integrations.

Follow these steps sequentially in a development environment. Estimated time: 1-2 hours. Prerequisites: Python 3.7+, PySide6, and the project cloned (d:/source/repos/pixooCommander).

## Step 1: Environment Setup

1. **Install Dependencies**:
   - Run `pip install -r requirements.txt` to ensure all runtime deps (PySide6, pixoo, psutil) are installed.
   - For development: `pip install pytest` for testing.

2. **Virtual Environment (Recommended)**:

   ```bash
   py -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

   - Reinstall deps in venv.

3. **Verify Current App**:
   - Run `python main.py` to launch the app.
   - Test basic functionality: Connect to a mock or real Pixoo device (use PIXOO_IP env var for tests).
   - Note any UI pain points (e.g., hardcoded styles) in a temp log.

## Step 2: Review Existing Codebase

1. **Audit UI Files**:
   - Open `main.py` and inspect scenes tab (if exists) or main window widgets.
   - Look for hardcoded colors, fonts, spacing: e.g., search for `setStyleSheet` or `QPalette` usages.
   - Document findings: Create a simple checklist in comments or a temp .md (e.g., "Button colors hardcoded in line 150").

2. **Core Modules Check**:
   - Review `core/device.py`, `core/project.py`, `core/player.py`, `core/scenes/*`.
   - Ensure scene interfaces support preview/render (e.g., `preview(qimage)` method).
   - Run tests: `pytest -q` for non-network; `PIXOO_IP=192.168.0.103 pytest -m network` if device available.

3. **Baseline Metrics**:
   - Manually time preview renders or app startup.
   - Screenshot current UI for before/after comparisons (store in `docs/screenshots/baseline/`).

## Step 3: Design System Documentation Review

1. **Read Master Plan**:
   - Review [DESIGN_SYSTEM_PLAN.md](DESIGN_SYSTEM_PLAN.md) for overall specs.
   - Cross-check with sub-docs:
     - [tokens.md](docs/design-system/tokens.md): Ensure JSON token file is created (e.g., `design_tokens.json` in root).
     - [components.md](docs/design-system/components.md): Identify first components to refactor (e.g., buttons).
     - [theming.md](docs/design-system/theming.md): Prototype ThemeManager class in a new file `core/theming.py`.
     - [accessibility.md](docs/design-system/accessibility.md): Flag a11y gaps in current UI.
     - [motion.md](docs/design-system/motion.md): Note animation opportunities (e.g., in preview).
     - [assets.md](docs/design-system/assets.md): Set up `assets/` folder structure.
     - [roadmap.md](docs/design-system/roadmap.md): Confirm phase alignments.
     - [metrics.md](docs/design-system/metrics.md): Set up basic logging for future tracking.

2. **Create Token JSON**:
   - Based on [tokens.md](docs/design-system/tokens.md), create `design_tokens.json`:

     ```json
     {
       "colors": {
         "primary": "#007BFF",
         "background": "#FFFFFF"
       },
       "typography": {
         "font-size-body": 14
       }
     }
     ```

   - Validate: Write a simple script to load and print tokens.

## Step 4: Initial Prototyping

1. **ThemeManager Stub**:
   - In `core/theming.py`, implement basic class from [theming.md](docs/design-system/theming.md):

     ```python
     from PySide6.QtCore import QObject, Signal
     from PySide6.QtWidgets import QApplication
     import json

     class ThemeManager(QObject):
         themeChanged = Signal(str)

         def __init__(self):
             super().__init__()
             self.load_themes()

         def load_themes(self):
             with open('design_tokens.json', 'r') as f:
                 self.tokens = json.load(f)

         def apply_theme(self, theme_name='light'):
             # Stub: Generate QSS
             qss = "QWidget { background-color: white; }"
             QApplication.instance().setStyleSheet(qss)
             self.themeChanged.emit(theme_name)
     ```

   - Test: Import in main.py and call apply_theme.

2. **Component Prototype**:
   - Create a test button using [components.md](docs/design-system/components.md) specs.
   - Add to a temp dialog: Apply token-based style.

## Step 5: Planning and Next Steps

1. **Risk Assessment**:
   - List potential issues: e.g., Qt stylesheet performance, cross-platform theming.
   - Prioritize: Focus on scenes tab first.

2. **Team Alignment**:
   - Share baseline screenshots and audit notes.
   - Schedule Phase 1 kickoff after completing prototypes.

3. **Commit and Branch**:
   - Create branch `feat/design-system-phase0`.
   - Commit: `docs: add design system documentation` and prototypes.
   - Push and PR for review.

## Troubleshooting

- **Qt Issues**: Ensure PySide6 version >=6.4; check docs for stylesheet syntax.
- **Device Testing**: Use mock mode in device.py for offline dev.
- **Metrics Baseline**: If timing hard, add print statements with time.perf_counter().

## Resources

- [AGENTS.md](AGENTS.md): Coding style and commit guidelines.
- [QWEN.md](QWEN.md): Project overview and challenges.
- [README.md](README.md): Run and test commands.

Once Phase 0 is complete (docs reviewed, prototypes working, baseline established), proceed to Phase 1: Core UI Refactor. Track progress against [metrics.md](docs/design-system/metrics.md). For questions, reference the master [plan](DESIGN_SYSTEM_PLAN.md).
