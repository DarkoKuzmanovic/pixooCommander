# Accessibility (A11y) and Internationalization (i18n) Guidelines

This document provides guidelines for accessibility and internationalization in the Pixoo Commander design system, derived from the planning session specifications. These ensure the application is inclusive, usable by people with disabilities, and adaptable to different languages and regions. Compliance targets WCAG 2.1 Level AA, integrated with [tokens](tokens.md) for contrast and [theming](theming.md) for adaptable modes.

Accessibility is foundational to the UX plan, supporting keyboard navigation in the three-pane layout and semantic labeling for screen readers. i18n prepares for global users, using Qt's built-in translation system.

## Accessibility Principles

Follow POUR (Perceivable, Operable, Understandable, Robust) from WCAG:

- **Perceivable**: Content must be presented in ways users can perceive.
- **Operable**: Interface components and navigation must be operable.
- **Understandable**: Information and operation must be understandable.
- **Robust**: Content must be robust enough for assistive technologies.

### Color and Contrast

- **Contrast Ratios**: Minimum 4.5:1 for normal text, 3:1 for large text (18pt+). Use [token colors](tokens.md) verified with tools like WAVE or Contrast Checker.
  - Examples: `color-text-primary` on `color-background` must pass AA.
  - Avoid relying solely on color for information (e.g., add icons or text for success/error states).
- **Theming Integration**: High-contrast mode as a theme variant; auto-adjust tokens in [ThemeManager](theming.md).
- **Guidelines**: No red-green color combinations for critical info; use patterns or labels.

### Keyboard Navigation

- **Full Support**: All interactive elements (buttons, lists, editors) accessible via Tab, Enter, Arrow keys.
  - Scenes list: Arrow keys for navigation, Enter to edit/select.
  - Panes: Logical tab order (left to right, top to bottom).
  - Shortcuts: Alt+Up/Down for reordering (from planning); document in tooltips.
- **Focus Indicators**: Visible outlines (2px `color-primary`) on focus; ensure `focus-visible` in QSS.
- **Skip Links**: Optional for longer pages, but prioritize in modal dialogs.

### Screen Readers and ARIA

- **Semantic HTML/Qt Equivalents**: Use native Qt roles where possible; add ARIA for custom widgets.
  - Buttons: `QPushButton` (role="button").
  - Lists: `QListView` (role="list"); items as "listitem".
  - Editors: `QLineEdit` (role="textbox"); label with `buddy` or accessibleName.
  - Preview: `QWidget` with role="img", accessibleDescription="Live preview of scene".
- **Labels and Descriptions**: Every input has a visible label; use `setAccessibleName` for screen readers.
  - Example: For color picker, "Choose text color for scene".
- **Live Regions**: Use `QAccessible.announce` for dynamic updates (e.g., "Scene added", "Connection established").
- **Error Handling**: Announce validation errors; associate with fields via `setAccessibleDescription`.

### Resize and Zoom

- **Responsive Design**: Layouts use QSplitter for resizable panes; support up to 200% zoom without loss of functionality.
- **Reflow**: Content doesn't require horizontal scrolling at 400% zoom.
- **Touch Targets**: Minimum 44x44px for buttons (scalable for desktop).

### Other A11y Features

- **Timing**: Adjustable durations for animations (see [motion.md](motion.md)); pause on reduced motion preference.
- **Seizure Safety**: No flashing content >3 flashes/sec.
- **Testing**: Use NVDA/JAWS for screen reader tests; keyboard-only walkthroughs; automated tools like axe-core for Qt.

## Internationalization (i18n) Guidelines

i18n enables localization without code changes, supporting future languages beyond English.

### Qt Translation System

- **Markup**: Use `tr()` for all user-facing strings in Python code.
  - Example: `self.connect_button.setText(self.tr("Connect"))`
- **Extraction**: Use `pylupdate6` to generate .ts files from source.
- **Translation Files**: Store in `translations/` (e.g., pixoo_commander_en.ts, pixoo_commander_fr.ts).
- **Loading**: In main.py, `translator = QTranslator(); app.installTranslator(translator); translator.load("pixoo_commander_" + locale)`.
- **Locale Detection**: Use `QLocale.system()` for auto-detection; allow user override in settings.

### RTL and Layout Support

- **Right-to-Left Languages**: Set `layoutDirection = Qt.RightToLeft` based on locale.
  - Panes: Mirror layout (e.g., text alignment flips).
  - Icons: Use mirrored variants if needed (e.g., arrows).
- **Date/Time Formats**: Use `QLocale` for system info display (e.g., CPU/RAM with localized units).

### Text Handling

- **BiDi Support**: Qt handles mixed LTR/RTL text automatically.
- **Font Fallback**: Ensure `font-family-base` supports international characters (e.g., add system fallbacks).
- **Input**: Support IME for non-Latin scripts in text editors.

### Cultural Considerations

- **Icons/Assets**: Neutral icons; avoid culture-specific symbols (see [assets.md](assets.md)).
- **Number Formats**: Use locale for decimals, currencies if extended.
- **Testing**: Verify with sample translations; check for truncation in UI.

## Implementation Workflow

1. **Audit Existing Code**: Identify all strings; wrap in tr().
2. **Generate Translations**: Run extraction tools; translate key files.
3. **Integrate A11y**: Add accessibleName/Description to widgets; test with tools.
4. **Phased Rollout**: Start with core UI (scenes tab); expand to menus/status bar (align with [roadmap](roadmap.md)).
5. **Validation**: Include a11y checks in tests; user testing with diverse groups.

## Cross-References

- **Components**: Apply a11y to all [redesigned components](components.md).
- **Metrics**: Track a11y compliance in [success criteria](metrics.md).
- **Roadmap**: A11y audits in Phase 3 polishing.

These guidelines ensure Pixoo Commander is usable by all, aligning with inclusive design principles from planning.
