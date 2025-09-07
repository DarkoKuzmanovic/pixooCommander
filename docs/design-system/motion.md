# Animation Specifications

This document specifies the motion and animation guidelines for the Pixoo Commander design system, based on the planning session specifications. Animations enhance user experience by providing smooth feedback and transitions without overwhelming the interface. They are implemented using Qt's animation framework (QPropertyAnimation, QTimer) to ensure performance on desktop.

Motions are subtle, respectful of user preferences (e.g., reduced motion via system settings), and integrated with [components](components.md) and [accessibility](accessibility.md). All durations and easing are configurable via tokens if extended.

## Core Principles

- **Purposeful**: Animations communicate state changes (e.g., scene switch, drag reorder) or provide delight (e.g., smooth scrolling).
- **Performance**: Non-blocking; use QTimer for timed updates; limit to 60fps.
- **Accessibility**: Respect `prefers-reduced-motion` (detect via QSettings or platform API); provide static alternatives.
- **Consistency**: Use standard easing (easeInOutQuad) and token-based durations.
- **Subtlety**: No excessive effects; focus on functional UX like live preview updates.

## Animation Tokens

Define reusable values for motion, extending [tokens](tokens.md):

- **Durations**:
  - `motion-duration-fast`: 150ms - Quick feedback (e.g., focus expand).
  - `motion-duration-normal`: 300ms - Standard transitions (e.g., fade on theme change).
  - `motion-duration-slow`: 500ms - Longer interactions (e.g., loading spinner min display).

- **Easing Curves**:
  - `motion-easing-standard`: QEasingCurve.InOutQuad - Smooth acceleration/deceleration.
  - `motion-easing-linear`: QEasingCurve.Linear - Constant speed (e.g., scrolling).
  - `motion-easing-elastic`: QEasingCurve.OutBounce - Playful bounces (optional, for non-critical).

- **Delays**:
  - `motion-delay-short`: 100ms - Staggered starts (e.g., button ripple).

Usage: Reference in code, e.g., `QPropertyAnimation.setDuration(motion_duration_normal)`.

## Specific Animations

### Scrolling Text Animation

**Description**: For text scenes with scroll enabled, animate text movement across the preview and device.

**Specs**:

- Direction: Left-to-right (default) or configurable (up/down/right-to-left).
- Speed: Configurable 20-100px/s; default 50px/s.
- Easing: Linear for continuous scroll.
- Duration: Infinite loop until scene end; pause on hover in preview.
- Implementation: Use QPropertyAnimation on x/y properties of text item; update position in timer callback.
- Device Sync: Mirror preview animation to device pushes via player engine.

**Context**: Text scene editor and live preview; from planning for enhanced multi-line text support.

### Preview Updates and Transitions

**Description**: Smooth changes when switching scenes or updating live data (e.g., sysinfo every 1s).

**Specs**:

- Fade Transition: Cross-fade between old/new preview (opacity from 1 to 0 over 300ms).
- SysInfo Refresh: Subtle pulse or slide-in for updated values (e.g., CPU bar grows/shrinks).
- Easing: InOutQuad.
- Duration: 300ms for scene switch; 200ms for data refresh.
- Implementation: QGraphicsOpacityEffect on preview widget; QSequentialAnimationGroup for complex sequences.

**Context**: Right pane of scenes tab; ensures immediate visual feedback without jarring cuts.

### Drag and Reorder Motion

**Description**: Visual feedback during drag-and-drop in scenes list.

**Specs**:

- Drag Start: Item scales up slightly (1.05x) and opacity to 0.8.
- During Drag: Follow mouse with shadow (`shadow-medium`); drop zones highlight with scale (1.02x).
- Drop: Animate to new position with slide (200ms); others shift smoothly.
- Easing: InOutQuad.
- Implementation: Override drag events in QListView; use QPropertyAnimation for position changes.

**Context**: Left pane reordering; supports Alt+Up/Down keyboard equivalent.

### Loading and Progress States

**Description**: Indicate ongoing operations like device push or image load.

**Specs**:

- Spinner: Rotate 360° indefinitely (1s per rotation, linear); size 24px, `color-primary`.
- Progress Bar: Indeterminate slide or determinate fill (easeInOut).
- Duration: Min 500ms to avoid flicker; fade out on complete.
- Implementation: QProgressBar with animation; or custom QWidget with QTimer for spinner.
- Feedback: Accompany with status bar update.

**Context**: Device pushes in player; error states show shake (3px offset, 150ms).

### Button and Interaction Feedback

**Description**: Hover, focus, and press states for interactive elements.

**Specs**:

- Hover: Scale 1.02x or color shift (10% brighter), 150ms.
- Press: Scale down 0.98x, 100ms bounce back.
- Focus: Glow pulse (opacity cycle), but static if reduced motion.
- Easing: OutBack for bounce effects.
- Implementation: QStateMachine or event-driven animations on QPushButton.

**Context**: All buttons (e.g., play controls, add scene).

### Theme Switch Motion

**Description**: Smooth transition when changing themes.

**Specs**:

- Cross-Fade: Fade out old theme, apply new, fade in (600ms total).
- Implementation: Animate global opacity; defer stylesheet set to mid-animation.

**Context**: ThemeManager [application](theming.md).

## Implementation Guidelines

- **Framework**: Prefer QPropertyAnimation for property changes; QTimer for timed sequences (e.g., sysinfo 1s updates).
- **Reduced Motion**: Check system preference; if true, set durations to 0ms or static.
  - Detection: Use QPlatformTheme or registry query on Windows.
- **Performance**: Limit concurrent animations; use QVariantAnimation for complex curves.
- **Testing**: Verify smoothness on target hardware; test with reduced motion enabled.
- **Fallback**: Graceful degradation to static UI if animation fails.

## Cross-References

- **Components**: Apply to specific [elements](components.md) like preview pane.
- **Accessibility**: Integrate with [a11y guidelines](accessibility.md) for timing adjustments.
- **Roadmap**: Implement in Phase 3 polishing; test with playback engine.

These specifications align with the UX plan for non-blocking, cooperative updates in the scenes editor.
