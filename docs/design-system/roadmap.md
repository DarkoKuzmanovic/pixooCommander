# Implementation Phases

This document details the phased implementation roadmap for the Pixoo Commander design system, compiled from the planning session specifications in the main [roadmap.md](../../../roadmap.md). It outlines sequential phases to integrate the visual uplift, tokens, components, theming, accessibility, motion, and assets into the existing PySide6 scenes editor application. Each phase builds on the previous, with clear milestones, deliverables, and dependencies.

The roadmap aligns with the overall project progress (e.g., core refactor done) and prioritizes MVP features before nice-to-haves. Progress status is noted based on current state.

## Overall Goals

- Transform the current app into a polished, consistent UI using the design system.
- Ensure non-disruptive integration with existing core modules (device.py, project.py, player.py, scenes).
- Test incrementally with device pushes and user simulations.
- Timeline: 4-6 weeks, assuming 1-2 developers; adjust based on testing.

## Phase 0: Foundation (Setup and Planning)

**Status**: DONE (core scaffolded; initial planning complete).

**Objectives**: Establish baseline for design system integration; no UI changes yet.

**Deliverables**:

- Review and baseline existing UI (main.py, scenes tab).
- Create design system docs (this set: DESIGN_SYSTEM_PLAN.md, tokens.md, etc.).
- Set up theme config JSON and basic token loader.
- Audit current components against tokens (e.g., identify hardcoded colors).

**Dependencies**: Existing core modules.
**Effort**: 1 day.
**Success Metrics**: Docs created; token JSON validated.
**Next**: Proceed to Phase 1 after review.

**Cross-Reference**: See [IMPLEMENTATION_KICKOFF.md](../IMPLEMENTATION_KICKOFF.md) for quick-start.

## Phase 1: Core UI Refactor (Tokens and Basic Components)

**Status**: DONE (tokens integrated; ThemeManager implemented and integrated).

Implementation notes:

- Token system loaded from `core/ui/tokens.json` and applied via generated QSS.
- `ThemeManager` implemented and applied to QApplication; light/dark toggle wired in `main.py`.
- Core components (buttons, lists, editor fields) updated to use token-based QSS; unit test added for stylesheet generation.
- Note: QSS ID selectors require widget.objectName(...) assignments in `main.py` for playback/preview widgets — this remains to be applied.

**Objectives**: Apply tokens and redesign key components without breaking functionality.

**Deliverables**:

- Implement token system: Load from JSON; apply to global stylesheet.
- Redesign buttons, lists, and editor fields using [components](components.md) guidelines.
- Basic theming: Light/dark toggle via [ThemeManager](theming.md).
- Update scenes list and editors with token spacing/typography.
- Inline validation visuals (e.g., error borders).

**Dependencies**: Phase 0 docs.
**Effort**: 1 week.
**Testing**: Unit tests for stylesheet generation; manual UI review.
**Success Metrics**: 80% components use tokens; no visual regressions.
**Risks**: Qt stylesheet quirks; mitigate with prototypes.

## Phase 2: Enhanced UX (Preview, Motion, Assets)

**Status**: DONE (basic preview and persistence; assets partial).

**Objectives**: Add interactive feedback and asset handling.

**Deliverables**:

- Live preview pane with scene rendering and basic [motion](motion.md) (e.g., scrolling text animation).
- Asset management: Relative paths, thumbnails, file pickers per [assets](assets.md).
- Play controls with states and simple transitions.
- Persistence integration: Save/load themes and asset paths in project JSON.
- Keyboard shortcuts (e.g., reorder scenes).

**Dependencies**: Phase 1 components.
**Effort**: 1 week.
**Testing**: Integration tests for preview updates; asset load with mocks.
**Success Metrics**: Smooth preview playback; relink works for missing assets.
**Risks**: Performance on large assets; optimize with caching.

## Phase 3: Polish and Accessibility (A11y, Full Motion, Testing)

**Status**: PARTIAL (tests harness added; a11y pending - focus outlines, keyboard nav, ARIA-like labels).

**Objectives**: Ensure inclusivity, smoothness, and reliability.

**Deliverables**:

- Full [accessibility](accessibility.md) implementation: ARIA labels, keyboard nav, contrast checks.
- Complete [motion](motion.md): Fade transitions, drag animations, reduced motion support.
- Theme auto-detection and persistence.
- Comprehensive testing: Unit for components, integration for playback, a11y audits.
- Polish: Tooltips, error toasts, dirty indicators.

**Dependencies**: Phases 1-2.
**Effort**: 1 week.
**Testing**: Full pytest suite; accessibility tools (axe); user testing with diverse groups.
**Success Metrics**: WCAG AA compliance; 90% test coverage.
**Risks**: Cross-platform a11y differences; test on Windows/macOS.

## Phase 4: Advanced Features and Optimization (Nice-to-Haves)

**Status**: Pending (post-MVP).

**Objectives**: Extend for production readiness and future-proofing.

**Deliverables**:

- Advanced scheduling, transitions, plugin system.
- Asset manager UI with thumbnails and import/export.
- i18n extraction and sample translations.
- Performance optimizations (e.g., debounced pushes).
- Documentation updates; release notes.

**Dependencies**: Phase 3 polish.
**Effort**: 1-2 weeks.
**Testing**: E2E with real device; load testing.
**Success Metrics**: User feedback loop; reduced bugs post-release.
**Risks**: Scope creep; prioritize based on user needs.

## Monitoring and Iteration

- **Tools**: Use GitHub Projects for tracking; weekly check-ins.
- **Gates**: Code review before phase end; demo to stakeholders.
- **Rollback**: Feature flags for new components.
- **Post-Implementation**: Gather metrics from [metrics.md](metrics.md); iterate based on usage.

This phased approach ensures steady progress toward a cohesive design system, building on the existing roadmap milestones.

Verification: Run the app, open Theme menu, switch Light/Dark and confirm styles update; run `python -m pytest test/unit/test_theme_manager.py`.
