# Icon and Asset Strategy

This document outlines the strategy for managing icons and assets in the Pixoo Commander design system, based on the planning session specifications. Assets include icons for UI elements, images for scenes, and related resources. The strategy emphasizes minimalism, consistency, and efficient handling to support project persistence and relative paths, as detailed in the UX plan.

Assets are organized to facilitate drag-and-drop, thumbnails, and relinking, integrating with [components](components.md) for previews and [theming](theming.md) for adaptive icons. Storage is relative to project files to ensure portability.

## Core Principles

- **Minimalism**: Use built-in Qt icons where possible; add custom only when necessary to reduce bundle size.
- **Consistency**: All assets follow token-based sizing and theming (e.g., color overrides in dark mode).
- **Performance**: Lazy loading for images; thumbnails for previews to avoid full-res loads.
- **Accessibility**: Icons have alt text/ARIA labels; high-contrast variants (see [accessibility.md](accessibility.md)).
- **Scalability**: Support SVG for vector icons; raster (PNG/JPG) for scene images with compression.

## Icon Strategy

Icons provide visual cues for actions and states in the UI (e.g., play button, scene types).

### Icon Types and Sizing

- **UI Icons**: For buttons and toolbars.
  - Size Tokens: `size-xs` (8px) for subtle; `size-s` (16px) for inline; `size-m` (24px) for toolbar (from [tokens](tokens.md)).
  - Formats: Prefer SVG for scalability; fallback to PNG.
- **Scene Type Icons**: Small indicators in scenes list (e.g., text 'T', image 'I', sysinfo 'S').
  - Size: 12px; monochrome `color-secondary`, tinted `color-primary` on selection.
- **Status Icons**: For connection (Wi-Fi symbol), errors (warning triangle).
  - Adaptive: Color-shift based on theme (e.g., green for success).

### Sourcing and Management

- **Built-in**: Use Qt's QIcon.fromTheme() or standard icons (e.g., "media-playback-start" for play).
- **Custom Icons**: Store in `assets/icons/`; name semantically (e.g., `icon-play.svg`).
  - Set: Leverage open-source libraries like Material Design Icons (subset only, ~50 icons).
  - Theming: SVG with currentColor CSS equivalent in QSS for color adaptation.
- **Fallbacks**: Graceful degradation; text labels if icon load fails.
- **Implementation**: Load via QIcon; set in QPushButton or QLabel. For previews, use QPixmap scaled to token size.

### Guidelines

- **Neutrality**: Avoid culture-specific icons; test with [i18n](accessibility.md).
- **Motion**: Animate icons (e.g., rotate spinner) per [motion](motion.md).
- **Testing**: Verify rendering in all themes; accessibility with screen readers.

## Asset Strategy (Images and Media)

Assets for scenes (e.g., images in image scenes) and thumbnails.

### Storage and Organization

- **Project Assets**: Relative paths to `project_assets/` folder beside JSON project file.
  - Example: Project `myproject.json` stores images in `myproject_assets/images/logo.png`.
  - Relinking: On load, prompt to relink missing files; scan subfolders.
- **Thumbnails**: Auto-generate 64x64px previews (scaled from `size-xl`) using QImage; store as .thumb.png.
- **Supported Formats**: PNG (preferred for transparency), JPG for photos; max 1MB per asset to prevent bloat.
- **Compression**: Use Qt's QImageIOHandler for optimized saving.

### Management Features

- **Asset Manager**: Planned post-MVP (from roadmap); UI pane for browsing, importing, tagging assets.
  - Drag-and-Drop: Support dropping images into editor; auto-relative path.
  - Thumbnails: Grid view with previews; search by name/tag.
- **Validation**: Check file existence on project load; warn on invalid formats/sizes.
- **Export/Import**: Bundle assets with project ZIP; option to embed small images in JSON (base64, <10KB).

### Usage in Components

- **Image Scene Editor**: QFileDialog for selection; preview with fit modes (contain/cover/stretch).
- **Preview Pane**: Render asset with scene config; animate if applicable.
- **Persistence**: In JSON: `"config": { "path": "assets/logo.png", "fit": "contain" }`; resolve relative to project dir.

### Performance and Optimization

- **Lazy Loading**: Load full image only on play/push; use thumbnail for editing.
- **Caching**: QPixmapCache for recent assets; clear on memory pressure.
- **Device Push**: Resize/optimize for Pixoo screen (64x64) before sending.

## Implementation Guidelines

- **Code Integration**: Use core/project.py for path resolution; scene.image.py for loading/rendering.
- **Tools**: Integrate with player for asset pushes; test with mock device.
- **Phased**: Basic relative paths in Phase 2; full manager in Phase 4 (nice-to-haves).
- **Security**: Validate paths to prevent directory traversal; no remote assets.

## Cross-References

- **Roadmap**: Asset management in [phases](roadmap.md); persistence in core/project.py.
- **Components**: File pickers in [editors](components.md).
- **Metrics**: Track asset load times in [success criteria](metrics.md).

This strategy ensures assets are manageable and performant, supporting the scenes editor's workflow.
