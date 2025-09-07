# Token System Specification

The token system provides a foundational set of reusable values to ensure consistency in the Pixoo Commander design system. Tokens are semantic primitives for colors, typography, spacing, and other UI elements, derived directly from the planning session specifications for a modular and maintainable UI.

Tokens are defined in a centralized configuration (e.g., JSON or Qt resource) and applied via the ThemeManager. They support theming by allowing overrides for different modes (light/dark).

## Color Tokens

Colors are defined as semantic aliases mapping to hex values, ensuring accessibility and brand consistency. All colors meet WCAG contrast requirements where applicable.

- **Primary Colors**:
  - `color-primary`: #007BFF - Main brand color for buttons, links, and active states.
  - `color-primary-variant`: #0056B3 - Darker shade for hover/focus states.

- **Secondary Colors**:
  - `color-secondary`: #6C757D - For secondary actions, borders, and subtle text.
  - `color-secondary-variant`: #495057 - Darker for emphasis.

- **Feedback Colors**:
  - `color-success`: #28A745 - Positive actions (e.g., connection success).
  - `color-warning`: #FFC107 - Cautions (e.g., unsaved changes).
  - `color-error`: #DC3545 - Errors (e.g., validation failures).
  - `color-info`: #17A2B8 - Informational states.

- **Neutral Colors**:
  - `color-background`: #FFFFFF (light) / #121212 (dark) - Main background.
  - `color-surface`: #F8F9FA (light) / #1E1E1E (dark) - Cards and panes.
  - `color-text-primary`: #212529 - Main text.
  - `color-text-secondary`: #6C757D - Subtle text.
  - `color-border`: #DEE2E6 - Dividers and borders.
  - `color-shadow`: rgba(0, 0, 0, 0.1) - For elevations.

Usage: Apply via Qt stylesheets, e.g., `QPushButton { background-color: {{color-primary}}; }`.

## Typography Tokens

Typography ensures readable and hierarchical text presentation.

- **Font Family**:
  - `font-family-base`: system-ui, -apple-system, sans-serif (falls back to system fonts like Segoe UI).

- **Font Sizes**:
  - `font-size-h1`: 24px - Major headings (e.g., tab titles).
  - `font-size-h2`: 20px - Section headings.
  - `font-size-h3`: 16px - Subheadings.
  - `font-size-body`: 14px - Main content.
  - `font-size-label`: 12px - Form labels and small text.

- **Font Weights**:
  - `font-weight-light`: 300
  - `font-weight-normal`: 400
  - `font-weight-medium`: 500
  - `font-weight-bold`: 700

- **Line Heights**:
  - `line-height-tight`: 1.25 - For headings.
  - `line-height-normal`: 1.5 - For body text.

Usage: Define in QFont or stylesheet, e.g., `QLabel { font-size: {{font-size-body}}px; }`.

## Spacing Tokens

Spacing creates rhythm and alignment in layouts.

- `spacing-xs`: 4px - Tight padding (e.g., button internals).
- `spacing-s`: 8px - Small gaps (e.g., between form fields).
- `spacing-m`: 16px - Standard margin/padding (e.g., pane separations).
- `spacing-l`: 24px - Section spacing.
- `spacing-xl`: 32px - Major divisions (e.g., between tabs).

Usage: Apply as margins/padding in layouts or stylesheets.

## Sizing Tokens

For components and icons.

- `size-xs`: 8px - Small icons or borders.
- `size-s`: 16px - Standard button height.
- `size-m`: 24px - Toolbar icons.
- `size-l`: 32px - Large previews.
- `size-xl`: 64px - Device screen simulation.

## Border and Shadow Tokens

- **Border Radius**:
  - `border-radius-s`: 4px - Buttons and inputs.
  - `border-radius-m`: 8px - Cards and previews.

- **Shadows**:
  - `shadow-low`: 0 1px 3px {{color-shadow}} - Subtle elevation.
  - `shadow-medium`: 0 4px 6px {{color-shadow}} - Card shadows.
  - `shadow-high`: 0 8px 16px {{color-shadow}} - Modal overlays.

## Implementation Guidelines

- **Reference**: Tokens are referenced semantically (e.g., `color-primary` instead of hex) in code and stylesheets.
- **Validation**: Use linters or build tools to ensure token usage; no hardcoded values.
- **Updates**: Changes to tokens propagate via ThemeManager reload.
- **Cross-References**: Integrate with [components.md](components.md) for component-specific applications and [theming.md](theming.md) for mode-specific overrides.

This system scales with future features like custom themes or plugins.
