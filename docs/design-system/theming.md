# ThemeManager Architecture

This document describes the theming architecture for the Pixoo Commander design system, based on the planning session specifications. The ThemeManager enables flexible, dynamic theming to support light and dark modes, ensuring a consistent and adaptable user experience. It integrates with the [token system](tokens.md) for semantic styling and applies themes globally via Qt mechanisms.

The architecture is designed for extensibility, allowing future custom themes or system-based switching.

## Overview

Theming ensures the UI adapts to user preferences or system settings, improving accessibility and comfort. Key goals from planning:

- Centralized management of theme states.
- Seamless switching without restarting the application.
- Support for light/dark modes with token overrides.
- Persistence of user-selected themes.
- Minimal performance impact on theme changes.

## ThemeManager Class Structure

**Description**: A singleton or application-wide instance that loads, applies, and manages themes.

**Key Components**:

- **Theme Data Model**: Themes defined as JSON objects with token overrides.
  Example:

  ```bash
  {
    "name": "Light",
    "tokens": {
      "color-background": "#FFFFFF",
      "color-surface": "#F8F9FA",
      "color-text-primary": "#212529"
    }
  }
  ```

- **Loader**: Parses theme files from a `themes/` directory or embedded resources.
- **Applier**: Generates and sets Qt stylesheets (QSS) or QPalettes for the entire application.
- **Observer**: Listens for system theme changes (e.g., via QSettings or platform APIs) or user toggles.
- **Persister**: Saves user preference to QSettings.

**Inheritance/Integration**: Subclass `QObject` for signal-slot communication; emit `themeChanged(Theme)` signal on updates.

## Supported Modes

- **Light Mode** (Default): Bright backgrounds, dark text; suitable for daytime use.
  - Token Overrides: As defined in [tokens.md](tokens.md) light variants.
- **Dark Mode**: Dark backgrounds, light text; reduces eye strain in low light.
  - Token Overrides: Dark variants (e.g., `color-background: #121212`).
- **Auto Mode**: Follows system preference (e.g., Windows dark mode detection via registry or macOS APIs).
- **Custom Modes**: Extensible via additional JSON files; e.g., high-contrast for accessibility.

Toggle via menu bar item (e.g., View > Theme > Light/Dark/Auto).

## Implementation Details

**Loading Themes**:

1. On app startup, load default (light) theme.
2. Check QSettings for user preference; apply if available.
3. Parse JSON tokens and map to QSS variables (e.g., using string templating).

**Applying Themes**:

- **Global Stylesheet**: Set `app.setStyleSheet(generated_qss)` where QSS interpolates tokens:

  ```bash
  QWidget {
      background-color: {{color-background}};
      color: {{color-text-primary}};
      font-family: {{font-family-base}};
  }
  QPushButton {
      background-color: {{color-primary}};
      border-radius: {{border-radius-s}}px;
  }
  /* Component-specific overrides */
  ```

- **Palette Approach**: For finer control, set `QApplication.palette()` with color roles (e.g., QPalette.Window = token color).
- **Widget-Specific**: Use stylesheets on parent widgets (e.g., main window) to cascade.

**Dynamic Updates**:

- On theme change: Recursively update stylesheet on all top-level widgets; emit signal for custom components to refresh (e.g., preview pane redraw).
- Use `QTimer::singleShot(0, this, &ThemeManager::applyTheme)` for deferred application to avoid UI blocking.

**Error Handling**:

- Fallback to default theme if loading fails.
- Log invalid tokens; provide UI feedback for custom theme errors.

**Performance Considerations**:

- Cache generated QSS strings.
- Avoid per-widget updates; prefer global app-level changes.
- Debounce system theme detection (e.g., poll every 5s).

## Integration with Other Systems

- **Tokens**: ThemeManager injects mode-specific token values; components reference semantic tokens.
- **Components**: Each component's QSS uses token placeholders, resolved at apply time (see [components.md](components.md)).
- **Accessibility**: High-contrast themes as variants; integrate with [accessibility.md](accessibility.md) guidelines.
- **Motion**: Theme changes include fade transition (300ms) for smooth switch (see [motion.md](motion.md)).
- **Persistence**: Projects save relative to theme, but UI themes are app-global.

**Code Example** (Pseudocode):

```python
class ThemeManager(QObject):
    themeChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self.themes = self.load_themes('themes/')
        self.current_theme = 'light'

    def switch_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            qss = self.generate_qss(self.themes[theme_name])
            QApplication.instance().setStyleSheet(qss)
            self.themeChanged.emit(theme_name)
            self.save_preference(theme_name)

    def generate_qss(self, theme):
        # Template with token substitution
        return qss_template.format(**theme['tokens'])
```

## Testing and Validation

- Unit Tests: Mock QSS generation; assert correct token mapping.
- Integration: Switch themes and verify component rendering (screenshots or pixel diffs).
- Accessibility: Test contrast ratios post-theme apply.

This architecture supports the phased implementation in [roadmap.md](roadmap.md). For asset theming (e.g., icons), see [assets.md](assets.md).
