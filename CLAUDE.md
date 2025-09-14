# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pixoo Commander is a NeutralinoJS desktop application that controls Divoom Pixoo LED display devices. It features a plugin-based widget system similar to Android widgets, allowing users to create multiple scenes with customizable display elements.

## Development Commands

### NeutralinoJS Commands

- **Run development**: `neu run` - Starts the application in development mode
- **Build application**: `neu build` - Creates distribution binaries
- **Update client library**: `neu update` - Updates neutralino.js client library

### Application Structure

- **Entry Point**: `resources/index.html` - Main HTML file with complete UI layout
- **Main Script**: `resources/js/main.js` - Application bootstrapping and initialization
- **Configuration**: `neutralino.config.json` - NeutralinoJS app configuration (window: 1000x700px)

## Core Architecture

### Plugin System

The application uses a modular plugin architecture centered around widgets:

- **PluginManager** (`js/core/plugin-manager.js`) - Loads and registers widget plugins
- **Plugin** base class - Defines plugin interface with `init()`, `destroy()`, and widget registration
- **Core Widgets Plugin** (`js/plugins/core-widgets.js`) - Built-in widgets like Clock, Weather, Counter, etc.

### Scene Management

Multi-scene system for different display layouts:

- **SceneManager** (`js/core/scene-manager.js`) - Manages multiple scenes, handles scene switching
- **Scene** class - Contains widgets, manages render loop (default 1000ms intervals), handles widget lifecycle
- Each scene renders independently with its own widget collection and refresh rate

### Widget System

Three-tier widget hierarchy:

- **Widget** base class (`js/core/widget-base.js`) - Core widget functionality, position management, rendering lifecycle
- **AnimatedWidget** - Extends Widget for frame-based animations
- **DataWidget** - Extends Widget for data-fetching widgets with configurable intervals

Key widget concepts:

- Widgets operate on a 64x64 pixel buffer
- Each widget has position (x,y), dimensions, and update intervals
- Widget lifecycle: `init()` → `render()` → `destroy()`

### Device Communication

Pixoo device connection with CORS handling:

- **PixooClient** (`js/core/pixoo-client.js`) - HTTP API communication to Pixoo devices
- **DeviceScanner** (`js/core/device-scanner.js`) - Network discovery of Pixoo devices
- **Critical**: Uses `mode: 'no-cors'` in fetch requests to bypass browser CORS restrictions for local device communication
- Auto-discovers working ports (80, 64, 8080) and endpoints (/post, /api/post)

### UI Management

Single-page application with modular UI:

- **UIManager** (`js/ui/ui-manager.js`) - Handles all DOM interactions, device scanning UI, scene management UI
- **Canvas Preview** - Real-time 320x320px canvas showing 64x64 pixel buffer (5x5 pixel scaling)
- **Device Discovery UI** - Shows discovered devices with port information, click-to-select functionality

## Key Implementation Details

### CORS Handling for Local Devices

The application communicates with local Pixoo devices using `fetch()` with `mode: 'no-cors'`. This bypasses browser CORS restrictions but means responses cannot be read. Commands are sent fire-and-forget style, which works for most Pixoo operations.

### Multi-Port Device Detection

The DeviceScanner and PixooClient test multiple common ports automatically:

- Primary: Port 80 with `/post`
- Secondary: Port 64, 8080 with various endpoints
- Stores working endpoint configuration for subsequent requests

### Widget Plugin Registration

Widgets self-register with the PluginManager using static properties:

```javascript
static TYPE = 'widget_type';
static NAME = 'Display Name';
static DESCRIPTION = 'Widget description';
static ICON = '🔲';
```

### Scene Rendering Pipeline

1. Scene calls `widget.render()` for each enabled widget
2. Widget draws to shared PixooClient buffer
3. Scene calls `pixooClient.push()` to send buffer to device
4. Process repeats based on scene refresh rate

## File Organization

```shell
resources/js/
├── core/           # Core system classes
│   ├── pixoo-client.js      # Device communication
│   ├── device-scanner.js    # Network device discovery
│   ├── scene-manager.js     # Scene and widget management
│   ├── plugin-manager.js    # Plugin system
│   └── widget-base.js       # Widget base classes
├── plugins/        # Widget plugins
│   └── core-widgets.js      # Built-in widget collection
├── ui/            # User interface
│   └── ui-manager.js        # DOM management and interactions
└── main.js        # Application initialization
```

## Development Notes

### Adding New Widgets

1. Extend appropriate base class (Widget, AnimatedWidget, or DataWidget)
2. Implement required static properties (TYPE, NAME, etc.)
3. Override `onRender()` or `onAnimationFrame()` methods
4. Register widget in a plugin's widgets array

### Scene System

- Only one scene active at a time
- Scene switching stops current scene and starts new one
- Widget initialization/destruction handled automatically by scene lifecycle

### Device Connection Flow

1. User clicks scan or enters IP manually
2. DeviceScanner tests multiple ports/endpoints
3. Working configuration stored in PixooClient
4. Subsequent commands use discovered endpoint configuration
