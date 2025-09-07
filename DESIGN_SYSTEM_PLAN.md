# Design System Plan for Pixoo Commander

This document serves as the comprehensive master document for the design system of Pixoo Commander. It preserves the visual uplift plan from the planning session (detailed in [roadmap.md](roadmap.md)) and establishes the implementation workflow. All content is based on the specifications developed during planning, without introducing new requirements or modifications.

The design system focuses on creating a modern, intuitive user interface for the scenes editor, enhancing the existing PySide6 application. It emphasizes modularity, consistency, and usability for managing Pixoo device displays.

## Visual Direction

The visual direction aims for a clean, professional interface that prioritizes usability for scene composition and scheduling. Key principles from the planning session:

- **Layout and Structure**: Use a tabbed interface with a dedicated "Scenes" tab featuring a three-pane layout:
  - Left pane: Scenes list displaying name, type, and duration; includes buttons for Add, Duplicate, and Delete; supports drag-and-drop reordering.
  - Center pane: Type-specific scene editor with inline fields, validation, file pickers for images, and color pickers for text.
  - Right pane: Live preview rendered to QImage, with play controls (play/pause, next/previous, loop toggle) and duration interval input.
- **Global Elements**: Toolbar for project actions (New, Open, Save, Save As, Export/Import); status bar showing device connection state and push results.
- **Aesthetics**: Ample whitespace, consistent alignment, and responsive elements to accommodate different window sizes. Leverage Qt6's native widgets for a familiar desktop experience while applying custom styling for brand consistency.
- **Color Palette**: Neutral base with accents for interactive elements (e.g., blue for primary actions), ensuring readability on various displays.
- **Typography**: Sans-serif fonts (e.g., system default like Segoe UI on Windows) with hierarchical sizing for headings, labels, and content.

This direction supports seamless workflow from scene creation to device playback, with immediate visual feedback.

For detailed component guidelines, see [components.md](docs/design-system/components.md).

## Tokens

The token system ensures consistency across the UI by defining reusable values for colors, typography, spacing, and other primitives. Based on planning specifications for a cohesive look:

- **Color Tokens**:
  - Primary: #007BFF (used for buttons, links, active states).
  - Secondary: #6C757D (for secondary actions, borders).
  - Success: #28A745 (for positive feedback, e.g., connection success).
  - Warning: #FFC107 (for cautions, e.g., unsaved changes).
  - Error: #DC3545 (for errors, e.g., validation failures).
  - Background: #FFFFFF (light mode default), #121212 (dark mode).
  - Surface: #F8F9FA (cards, panes).
  - Text: #212529 (primary), #6C757D (secondary).

- **Typography Tokens**:
  - Font Family: System sans-serif (e.g., 'Segoe UI', Arial).
  - Headings: H1 24px bold, H2 20px bold, H3 16px bold.
  - Body: 14px regular.
  - Labels: 12px medium.
  - Line Height: 1.5 for body, 1.25 for headings.

- **Spacing Tokens**:
  - XS: 4px (tight padding).
  - S: 8px (small gaps).
  - M: 16px (standard margin/padding).
  - L: 24px (section spacing).
  - XL: 32px (major divisions).

- **Border Radius Tokens**:
  - S: 4px (buttons, inputs).
  - M: 8px (cards, panes).

- **Shadow Tokens** (for elevation):
  - Low: 0 1px 3px rgba(0,0,0,0.12).
  - Medium: 0 4px 6px rgba(0,0,0,0.1).

Tokens are semantic to allow easy theming. See [tokens.md](docs/design-system/tokens.md) for full specification and usage guidelines.

## Components

Component redesign focuses on reusable, accessible UI elements tailored to the scenes editor. Guidelines from planning:

- **Button**: Standard Qt QPushButton with primary/secondary variants; rounded corners (4px); hover states with color shift.
- **List View**: QAbstractListModel for scenes; drag handles; inline editing for duration.
- **Editor Fields**: QLineEdit for text, QFileDialog integration for images, QColorDialog for colors; validation with red borders on error.
- **Preview Pane**: Custom QWidget rendering QImage; animated updates for scrolling text and system info.
- **Play Controls**: Icon buttons (▶ play, ⏸ pause, etc.); grouped in a toolbar.
- **Status Bar**: QLabel for connection status; color-coded (green connected, red disconnected).

All components follow token system for styling. Ensure keyboard navigation and focus indicators. Detailed redesign guidelines in [components.md](docs/design-system/components.md).

## Theming Architecture

The ThemeManager handles light/dark mode switching and custom theming, as specified in planning for flexible UI adaptation.

- **Structure**: Centralized ThemeManager class loads token sets from JSON; applies via Qt stylesheets or QPalette.
- **Modes**: Light (default), Dark; toggle via menu or system preference.
- **Implementation**: Use QSS (Qt Style Sheets) for global application; override per-widget for specifics.
- **Dynamic Updates**: Signal-based reloading on theme change; persist user preference in settings.
- **Extensibility**: Support custom themes via plugins or config files.

See [theming.md](docs/design-system/theming.md) for architecture diagram and code examples.

## Accessibility

A11y guidelines ensure inclusive design, covering WCAG 2.1 principles:

- **Contrast**: Minimum 4.5:1 for text; use color tokens to verify.
- **Keyboard Navigation**: Full tab-focus support; logical order in panes.
- **Screen Readers**: ARIA labels for custom widgets (e.g., role="list" for scenes); alt text for previews.
- **Resize/Zoom**: Responsive layout up to 200% zoom.
- **i18n**: Use Qt's translation system (tr() for strings); RTL support for future languages.

Guidelines in [accessibility.md](docs/design-system/accessibility.md).

## Motion

Animation specifications enhance UX without overwhelming:

- **Scrolling Text**: Smooth horizontal/vertical scroll at configurable speed (e.g., 50px/s); ease-in-out timing.
- **Preview Updates**: Fade transitions (300ms) for scene changes; real-time updates for sysinfo every 1s.
- **Drag Reorder**: Visual feedback with opacity change during drag.
- **Loading States**: Spinner for device pushes (indeterminate, 500ms min).

Use QPropertyAnimation for all motions. Details in [motion.md](docs/design-system/motion.md).

## Assets

Asset strategy for icons and images:

- **Icons**: Use Qt's built-in or SVG assets; 16x16 for buttons, 24x24 for toolbar.
- **Images**: Relative paths in projects; thumbnail previews (64x64); support PNG/JPG.
- **Management**: Asset folder in project root; relink on load if missing.
- **Strategy**: Minimal custom assets; leverage open-source icon sets (e.g., Material Icons) for consistency.

See [assets.md](docs/design-system/assets.md).

## Roadmap

Implementation phases from planning milestones:

1. **Phase 0: Foundation** - Core refactor (device, project, scenes). Status: DONE.
2. **Phase 1: UI Implementation** - Scenes tab, editors, preview. Status: DONE (basic).
3. **Phase 2: Playback Engine** - Player controls, persistence. Status: DONE.
4. **Phase 3: Polish and Testing** - Validation, shortcuts, full tests. Status: PARTIAL.
5. **Phase 4: Advanced Features** - Schedules, transitions (nice-to-haves).

Detailed phases in [roadmap.md](docs/design-system/roadmap.md).

## Metrics

Success criteria:

- **Usability**: 90% task completion in user tests (e.g., create and play a scene).
- **Performance**: <100ms preview render; <500ms device push.
- **Consistency**: 100% token usage; no style violations in audits.
- **Accessibility**: AA WCAG compliance; passes automated tools (e.g., axe).
- **Adoption**: Reduced support queries post-release; positive feedback on UX.

Tracking in [metrics.md](docs/design-system/metrics.md).

## Next Steps

Refer to [IMPLEMENTATION_KICKOFF.md](IMPLEMENTATION_KICKOFF.md) for starting Phase 0 refinements. Cross-reference sub-documents for implementation details.
