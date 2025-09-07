# Component Redesign Guidelines

This document outlines the redesign guidelines for key UI components in the Pixoo Commander design system. These guidelines are based on the planning session specifications, focusing on modularity, usability, and integration with the token system. Components are redesigned to support the three-pane scenes editor layout, ensuring consistency and accessibility.

All components adhere to the [token system](tokens.md) for styling and the [theming architecture](theming.md) for mode support. They prioritize Qt6 native behaviors while applying custom styles for enhanced UX.

## Core Principles

- **Consistency**: Use tokens for all visual properties (colors, spacing, typography).
- **Accessibility**: Include focus indicators, keyboard support, and ARIA attributes where applicable (see [accessibility.md](accessibility.md)).
- **Responsiveness**: Components adapt to window resizing; use Qt layouts for fluid behavior.
- **State Management**: Support default, hover, focus, active, disabled, and error states.
- **Motion**: Apply smooth transitions as per [motion.md](motion.md).

## Button Component

**Description**: Standard interactive elements for actions like Add, Delete, Play.

**Variants**:

- Primary: For main actions (e.g., Connect, Save). Uses `color-primary` background.
- Secondary: For minor actions (e.g., Duplicate). Outlined with `color-secondary` border.
- Icon-only: For toolbar controls (e.g., play ▶). 24px square with icon.

**Specs**:

- Size: `size-s` (16px height) for inline; `size-m` (24px) for toolbar.
- Padding: `spacing-s` horizontal, `spacing-xs` vertical.
- Border Radius: `border-radius-s` (4px).
- Typography: `font-size-body` (14px), `font-weight-medium`.
- States:
  - Hover: Increase opacity by 10%, add `shadow-low`.
  - Focus: Outline with `color-primary` (2px width).
  - Disabled: 50% opacity, `color-text-secondary`.
- Motion: 200ms ease-in-out on hover/focus.

**Implementation**: Extend `QPushButton`; apply QSS for variants, e.g.,

```bash
QPushButton[primary="true"] {
    background-color: {{color-primary}};
    color: white;
}
```

**Usage Example**: In scenes tab for Add/Duplicate/Delete buttons.

## List View Component (Scenes List)

**Description**: Displays and manages the list of scenes with reordering capabilities.

**Specs**:

- Structure: Use `QListView` with `QAbstractListModel` for data binding.
- Items: Each row shows name, type icon, duration (editable inline).
- Drag-and-Drop: Visual handle (grip icon); opacity 0.5 during drag; drop zones highlighted.
- Selection: Single selection with highlight using `color-primary`.
- Spacing: `spacing-m` between items.
- Border: Subtle `color-border` on focus.
- States: Highlight errors (e.g., invalid scene) with `color-error` border.

**Motion**: 300ms slide animation on insert/remove; fade on reorder.

**Implementation**: Custom delegate for rendering items; handle `QDragEnterEvent` for reordering.

**Cross-Reference**: Integrates with project model in core/project.py.

## Editor Fields Component

**Description**: Type-specific input fields for scene configuration (text, image path, color, etc.).

**Variants**:

- Text Input: `QLineEdit` for scene names, text content.
- Numeric Input: `QSpinBox` for duration, positions (x/y).
- Color Picker: `QPushButton` triggering `QColorDialog`; shows swatch.
- File Picker: `QPushButton` for image paths, integrating `QFileDialog`.
- Select: `QComboBox` for enums (e.g., fit mode: contain/cover/stretch).

**Specs**:

- Size: `size-m` height.
- Padding: `spacing-s`.
- Border: `border-radius-s`; `color-border` default, `color-error` on validation fail.
- Typography: `font-size-body`.
- Validation: Real-time; show tooltip or inline message on error.
- States: Focus glow with `color-primary`.

**Motion**: 150ms expand on focus for multi-line text.

**Implementation**: Wrapper class for validation logic; signal for changes to update preview.

**Usage**: Center pane of scenes tab, tailored per scene type (e.g., text editor shows lines array).

## Preview Pane Component

**Description**: Live rendering of the current scene for immediate feedback.

**Specs**:

- Structure: Custom `QWidget` overriding `paintEvent` to draw `QImage`.
- Size: Fixed aspect ratio simulating device screen (64x64 pixels scaled up).
- Background: `color-surface` with `shadow-medium`.
- Overlay: Play controls at bottom; progress bar for duration.
- Updates: Real-time for sysinfo (1s interval); animated for scrolling text.
- Border Radius: `border-radius-m` (8px).

**Motion**: Fade transition (300ms) on scene change; smooth scroll animation.

**Implementation**: Call scene's `preview(width, height)` method; use `QTimer` for updates.

**Cross-Reference**: Uses scene interfaces from core/scenes/base.py.

## Play Controls Component

**Description**: Toolbar for playback management (play, pause, next, previous, loop).

**Specs**:

- Structure: `QToolBar` with icon buttons.
- Icons: Standard Qt icons or custom SVGs (16x16).
- Spacing: `spacing-s` between buttons.
- Toggle: Loop button changes icon/state.
- Disabled States: Gray out when not applicable (e.g., pause when stopped).

**Motion**: Icon rotation or pulse on active playback.

**Implementation**: Connect to player engine in core/player.py; update via signals.

## Status Bar Component

**Description**: Bottom bar showing connection and operation status.

**Specs**:

- Elements: `QLabel` for text (e.g., "Connected to 192.168.0.103"); progress for pushes.
- Colors: `color-success` for connected, `color-error` for disconnected.
- Spacing: `spacing-m`.
- Persistent: Shows last action result (e.g., "Pushed to device").

**Implementation**: Use `QStatusBar`; update via device wrapper signals.

## Guidelines for New Components

- **Extension**: Inherit from Qt base classes; apply tokens via QSS.
- **Testing**: Unit test rendering and interactions; accessibility audits.
- **Documentation**: Add docstrings with token references.
- **Deprecation**: For legacy UI elements, migrate to new components in phases.

These redesigns align with the UX plan in [roadmap.md](../../../roadmap.md), ensuring a cohesive experience. For implementation phases, see [roadmap.md](roadmap.md) in docs.
